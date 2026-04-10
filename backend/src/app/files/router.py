from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.files import service
from app.files.schemas import FileRead

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/presigned-url", response_model=str)
async def create_presigned_url(
    workspace_id: UUID,
    user_id: UUID,
    file_name: str,
    content_type: str,
    size: int,  
    session: AsyncSession = Depends(get_session)
) -> str:
    url = await service.create_presigned_url(
        session, workspace_id, user_id, file_name, content_type, size
    )
    return url

@router.get("", response_model=list[FileRead])
async def list_files(
    user_id: UUID | None = Query(default=None),
    workspace_id: UUID | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[FileRead]:
    files = await service.list_files(session, user_id=user_id, workspace_id=workspace_id)
    return [FileRead.model_validate(file) for file in files]


@router.get("/{file_id}", response_model=FileRead)
async def get_file(file_id: UUID, session: AsyncSession = Depends(get_session)) -> FileRead:
    file = await service.get_file(session, file_id)
    return FileRead.model_validate(file)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: UUID, session: AsyncSession = Depends(get_session)) -> None:
    await service.delete_file(session, file_id)
