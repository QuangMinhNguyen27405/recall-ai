from __future__ import annotations


import asyncio
import argparse
from datetime import datetime
from pathlib import Path

import boto3
from sqlalchemy import and_
from sqlmodel import SQLModel, select

from app.config.settings import settings
from app.db.session import AsyncSessionLocal, engine
from app.files.model import File, FileStatus
from app.chat_sessions.model import ChatSession  # noqa: F401
from app.users.model import User
from app.workspaces.model import Workspace

SEED_USER_EMAIL = "seed.student@recallai.dev"
SEED_USERNAME = "seed_student"
SEED_PASSWORD = "seed_password"
SEED_WORKSPACE_NAME = "Biology 101"


def _seed_files() -> list[Path]:
    root = Path(__file__).resolve().parent
    files_dir = root / "files"
    txt_files = sorted(files_dir.glob("*.txt"))
    if not txt_files:
        raise RuntimeError(f"No seed files found in {files_dir}")
    return txt_files


def _build_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.aws_endpoint_url,
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def _ensure_bucket(s3_client) -> None:
    existing = [bucket["Name"] for bucket in s3_client.list_buckets().get("Buckets", [])]
    if settings.s3_bucket not in existing:
        s3_client.create_bucket(Bucket=settings.s3_bucket)


async def _ensure_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def _drop_all_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


async def _upsert_user_and_workspace() -> tuple[User, Workspace]:
    async with AsyncSessionLocal() as session:
        result = await session.exec(select(User).where(User.email == SEED_USER_EMAIL))
        user = result.first()
        if user is None:
            user = User(
                username=SEED_USERNAME,
                email=SEED_USER_EMAIL,
                password=SEED_PASSWORD,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        result = await session.exec(
            select(Workspace).where(
                and_(
                    Workspace.user_id == user.id,
                    Workspace.name == SEED_WORKSPACE_NAME,
                )
            )
        )
        workspace = result.first()
        if workspace is None:
            workspace = Workspace(user_id=user.id, name=SEED_WORKSPACE_NAME)
            session.add(workspace)
            await session.commit()
            await session.refresh(workspace)

    return user, workspace


async def _upsert_files_and_upload(user: User, workspace: Workspace, *, skip_s3: bool) -> list[File]:
    s3 = None
    if not skip_s3:
        s3 = _build_s3_client()
        _ensure_bucket(s3)

    now = datetime.now()
    created_or_updated: list[File] = []
    async with AsyncSessionLocal() as session:
        for file_path in _seed_files():
            s3_key = f"seed/workspaces/{workspace.id}/{file_path.name}"
            if s3 is not None:
                body = file_path.read_bytes()
                s3.put_object(
                    Bucket=settings.s3_bucket,
                    Key=s3_key,
                    Body=body,
                    ContentType="text/plain",
                )

            result = await session.exec(
                select(File).where(
                    and_(
                        File.user_id == user.id,
                        File.workspace_id == workspace.id,
                        File.s3_key == s3_key,
                    )
                )
            )
            db_file = result.first()
            if db_file is None:
                db_file = File(
                    user_id=user.id,
                    workspace_id=workspace.id,
                    name=file_path.name,
                    s3_key=s3_key,
                    status=FileStatus.ready,
                    ingested_at=now,
                )
                session.add(db_file)
            else:
                db_file.name = file_path.name
                db_file.status = FileStatus.ready
                db_file.ingested_at = now
                db_file.updated_at = now

            created_or_updated.append(db_file)

        await session.commit()
        for db_file in created_or_updated:
            await session.refresh(db_file)

    return created_or_updated


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed local development data and manage schema for RecallAI."
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="seed",
        choices=["seed", "drop-all", "reset"],
        help="seed (default), drop-all tables, or reset (drop-all + seed).",
    )
    parser.add_argument(
        "--skip-s3",
        action="store_true",
        help="Skip S3 bucket/object upload and only seed PostgreSQL rows.",
    )
    args = parser.parse_args()

    if args.command == "drop-all":
        await _drop_all_tables()
        print("Dropped all tables.")
        return

    if args.command == "reset":
        await _drop_all_tables()
        print("Dropped all tables.")

    await _ensure_tables()
    user, workspace = await _upsert_user_and_workspace()
    files = await _upsert_files_and_upload(user, workspace, skip_s3=args.skip_s3)

    print("Seed completed:")
    print(f"- user_id={user.id} email={user.email}")
    print(f"- workspace_id={workspace.id} name={workspace.name}")
    if args.skip_s3:
        print(f"- files={len(files)} seeded in database only (S3 upload skipped)")
    else:
        print(f"- files={len(files)} uploaded to s3://{settings.s3_bucket}/seed/workspaces/{workspace.id}/")
    for seeded_file in files:
        print(f"  - file_id={seeded_file.id} name={seeded_file.name} status={seeded_file.status}")


if __name__ == "__main__":
    asyncio.run(main())
