from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.workspaces import service
from app.workspaces.schemas import WorkspaceCreate, WorkspaceRead

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate, session: AsyncSession = Depends(get_session)
) -> WorkspaceRead:
    workspace = await service.create_workspace(session, payload)
    return WorkspaceRead.model_validate(workspace)


@router.get("", response_model=list[WorkspaceRead])
async def list_workspaces(
    user_id: UUID | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[WorkspaceRead]:
    workspaces = await service.list_workspaces(session, user_id=user_id)
    return [WorkspaceRead.model_validate(workspace) for workspace in workspaces]


@router.get("/{workspace_id}", response_model=WorkspaceRead)
async def get_workspace(
    workspace_id: UUID, session: AsyncSession = Depends(get_session)
) -> WorkspaceRead:
    workspace = await service.get_workspace(session, workspace_id)
    return WorkspaceRead.model_validate(workspace)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: UUID, session: AsyncSession = Depends(get_session)
) -> None:
    await service.delete_workspace(session, workspace_id)
