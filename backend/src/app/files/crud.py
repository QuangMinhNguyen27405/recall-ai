from uuid import UUID
from app.db.session import settings
import boto3
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.files.model import File
from app.files.schemas import FileCreate

S3_BUCKET = settings.s3_bucket
s3 = boto3.client("s3")

async def create_presigned_url(
    session: AsyncSession, 
    workspace_id: UUID,
    file_name: str, 
    content_type: str, 
    size: int,
) -> str:
    s3_key = f"workspaces/{workspace_id}/files/{file_name}"
    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": S3_BUCKET, "Key": s3_key, "ContentType": content_type},
        ExpiresIn=900,
    )

async def get_file(
    session: AsyncSession, 
    file_id: UUID, 
    workspace_id: UUID, 
    user_id: UUID,
) -> File | None:
    statement = select(File)
    statement = statement.where(File.id == file_id)
    statement = statement.where(File.workspace_id == workspace_id)
    statement = statement.where(File.user_id == user_id)
    result = await session.exec(statement)
    return result.first()

async def update_file(session: AsyncSession, file_id: UUID, data: dict) -> File:
    file = await session.get(File, file_id)
    if file is None:
        raise ValueError(f"File id={file_id} not found")
    for key, value in data.items():
        if hasattr(file, key):
            setattr(file, key, value)
            
    session.add(file)
    await session.commit()
    await session.refresh(file)
    return file

async def list_files(
    session: AsyncSession,
    user_id: UUID | None = None,
    workspace_id: UUID | None = None,
) -> list[File]:
    statement = select(File)
    if user_id is not None:
        statement = statement.where(File.user_id == user_id)
    if workspace_id is not None:
        statement = statement.where(File.workspace_id == workspace_id)
    result = await session.exec(statement)
    return result.all()

async def delete_file(session: AsyncSession, file: File) -> None:
    await session.delete(file)
    await session.commit()
