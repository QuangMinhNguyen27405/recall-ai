from __future__ import annotations


import asyncio
import argparse
from pathlib import Path

import boto3
from sqlalchemy import and_
from sqlmodel import SQLModel, select

from app.config.settings import settings
from app.db.session import AsyncSessionLocal, engine
from app.files.model import File, FileStatus
from app.chat_sessions.model import ChatSession  # noqa: F401
from app.pipeline.ingestion import start_ingestion
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


async def _upsert_files_and_upload(
    user: User, workspace: Workspace, *, skip_s3: bool
) -> list[File]:
    s3 = None
    if not skip_s3:
        s3 = _build_s3_client()
        _ensure_bucket(s3)

    created_or_updated: list[File] = []
    text_files = _seed_files()
    async with AsyncSessionLocal() as session:
        for file_path in text_files:
            s3_key = f"/users/{user.id}/workspaces/{workspace.id}/files/{file_path.name}"
            file = File(
                user_id=user.id,
                workspace_id=workspace.id,
                name=file_path.name,
                s3_key=s3_key,
                status=FileStatus.unprocessed,
            )
            session.add(file)
            await session.commit()
            await session.refresh(file)
            if not skip_s3:
                s3.upload_file(file_path, settings.s3_bucket, s3_key)
                
            created_or_updated.append(file)
    return created_or_updated


async def _ingest_seeded_files(
    files: list[File], *, skip_ingestion: bool
) -> list[tuple[File, dict | None]]:
    if skip_ingestion:
        return [(file, None) for file in files]

    ingested_files: list[tuple[File, dict | None]] = []
    for file in files:
        result = await start_ingestion(file.id)
        async with AsyncSessionLocal() as session:
            refreshed_file = await session.get(File, file.id) or file
        ingested_files.append((refreshed_file, result))
    return ingested_files


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
    parser.add_argument(
        "--skip-ingestion",
        action="store_true",
        help="Skip running the ingestion pipeline after seeding files.",
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
    ingested_files = await _ingest_seeded_files(
        files,
        skip_ingestion=args.skip_s3 or args.skip_ingestion,
    )

    print("Seed completed:")
    print(f"- user_id={user.id} email={user.email}")
    print(f"- workspace_id={workspace.id} name={workspace.name}")
    if args.skip_s3:
        print(f"- files={len(files)} seeded in database only (S3 upload skipped)")
    else:
        print(
            f"- files={len(files)} uploaded to "
            f"s3://{settings.s3_bucket}/users/{user.id}/workspaces/{workspace.id}/files/"
        )
    if args.skip_s3:
        print("- ingestion skipped because S3 upload was skipped")
    elif args.skip_ingestion:
        print("- ingestion skipped by flag")
    else:
        print(f"- ingested_files={len(ingested_files)}")
    for seeded_file, ingestion_result in ingested_files:
        status = seeded_file.status
        if ingestion_result is None:
            print(f"  - file_id={seeded_file.id} name={seeded_file.name} status={status}")
            continue

        print(
            "  - "
            f"file_id={seeded_file.id} "
            f"name={seeded_file.name} "
            f"status={status} "
            f"docs={ingestion_result['docs_count']} "
            f"chunks={ingestion_result['chunks_count']} "
            f"deleted={ingestion_result['deleted_count']} "
            f"indexed={ingestion_result['indexed_count']}"
        )


if __name__ == "__main__":
    asyncio.run(main())
