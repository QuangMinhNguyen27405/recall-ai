from uuid import UUID

import boto3
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import settings
from app.files import crud
from app.files.model import File, FileStatus
from app.workspaces import crud as workspaces_crud

S3_BUCKET = settings.s3_bucket
s3 = boto3.client("s3")


async def create_presigned_url(
    session: AsyncSession,
    workspace_id: UUID,
    user_id: UUID,
    file_name: str,
    content_type: str,
    size: int,
) -> str:
    workspace = await workspaces_crud.get_workspace(session, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if workspace.user_id != user_id:
        raise HTTPException(
            status_code=400,
            detail="Workspace does not belong to the provided user",
        )

    s3_key = f"/users/{user_id}/workspaces/{workspace_id}/files/{file_name}"
    file = File(
        user_id=user_id,
        workspace_id=workspace_id,
        name=file_name,
        s3_key=s3_key,
        status=FileStatus.unprocessed,
    )
    await crud.create_file(session, file)

    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": S3_BUCKET, "Key": s3_key, "ContentType": content_type},
        ExpiresIn=900,
    )


async def list_files(
    session: AsyncSession,
    user_id: UUID | None = None,
    workspace_id: UUID | None = None,
) -> list[File]:
    return await crud.list_files(session, user_id=user_id, workspace_id=workspace_id)


async def get_file(session: AsyncSession, file_id: UUID) -> File:
    file = await crud.get_file(session, file_id)
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return file


async def delete_file(session: AsyncSession, file_id: UUID) -> None:
    await get_file(session, file_id)
    await crud.delete_file(session, file_id)
