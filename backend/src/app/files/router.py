from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.files import crud
from app.files.schemas import FileCreate, FileRead

router = APIRouter(prefix="/files", tags=["files"])


@router.post("", response_model=FileRead, status_code=status.HTTP_201_CREATED)
async def create_file(
    payload: FileCreate, session: AsyncSession = Depends(get_session)
) -> FileRead:
    file = await crud.create_file(session, payload)
    return FileRead.model_validate(file)


@router.get("", response_model=list[FileRead])
async def list_files(
    user_id: int | None = Query(default=None),
    workspace_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[FileRead]:
    files = await crud.list_files(session, user_id=user_id, workspace_id=workspace_id)
    return [FileRead.model_validate(file) for file in files]


@router.get("/{file_id}", response_model=FileRead)
async def get_file(file_id: int, session: AsyncSession = Depends(get_session)) -> FileRead:
    file = await crud.get_file(session, file_id)
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return FileRead.model_validate(file)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: int, session: AsyncSession = Depends(get_session)) -> None:
    file = await crud.get_file(session, file_id)
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    await crud.delete_file(session, file)
