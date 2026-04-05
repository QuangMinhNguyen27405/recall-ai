from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.workspaces import crud
from app.workspaces.schemas import WorkspaceCreate, WorkspaceRead

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate, session: AsyncSession = Depends(get_session)
) -> WorkspaceRead:
    workspace = await crud.create_workspace(session, payload)
    return WorkspaceRead.model_validate(workspace)


@router.get("", response_model=list[WorkspaceRead])
async def list_workspaces(
    user_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[WorkspaceRead]:
    workspaces = await crud.list_workspaces(session, user_id=user_id)
    return [WorkspaceRead.model_validate(workspace) for workspace in workspaces]


@router.get("/{workspace_id}", response_model=WorkspaceRead)
async def get_workspace(
    workspace_id: int, session: AsyncSession = Depends(get_session)
) -> WorkspaceRead:
    workspace = await crud.get_workspace(session, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return WorkspaceRead.model_validate(workspace)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: int, session: AsyncSession = Depends(get_session)
) -> None:
    workspace = await crud.get_workspace(session, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    await crud.delete_workspace(session, workspace)
