from uuid import UUID

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.users import crud as users_crud
from app.workspaces import crud
from app.workspaces.model import Workspace
from app.workspaces.schemas import WorkspaceCreate


async def create_workspace(session: AsyncSession, data: WorkspaceCreate) -> Workspace:
    user = await users_crud.get_user(session, data.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud.create_workspace(session, data)


async def list_workspaces(
    session: AsyncSession, user_id: UUID | None = None
) -> list[Workspace]:
    return await crud.list_workspaces(session, user_id=user_id)


async def get_workspace(session: AsyncSession, workspace_id: UUID) -> Workspace:
    workspace = await crud.get_workspace(session, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


async def delete_workspace(session: AsyncSession, workspace_id: UUID) -> None:
    await get_workspace(session, workspace_id)
    await crud.delete_workspace(session, workspace_id)
