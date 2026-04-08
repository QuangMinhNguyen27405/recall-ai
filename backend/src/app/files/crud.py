from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.files.model import File
from app.files.schemas import FileCreate


async def create_file(session: AsyncSession, data: FileCreate) -> File:
    file = File.model_validate(data)
    session.add(file)
    await session.commit()
    await session.refresh(file)
    return file


async def get_file(session: AsyncSession, file_id: int) -> File | None:
    return await session.get(File, file_id)

async def update_file(session: AsyncSession, file_id: int, data: dict) -> File:
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
    user_id: int | None = None,
    workspace_id: int | None = None,
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
