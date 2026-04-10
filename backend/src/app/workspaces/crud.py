from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.workspaces.model import Workspace
from app.workspaces.schemas import WorkspaceCreate


async def create_workspace(session: AsyncSession, data: WorkspaceCreate) -> Workspace:
    workspace = Workspace.model_validate(data)
    session.add(workspace)
    await session.commit()
    await session.refresh(workspace)
    return workspace


async def get_workspace(session: AsyncSession, workspace_id: UUID) -> Workspace | None:
    return await session.get(Workspace, workspace_id)


async def list_workspaces(session: AsyncSession, user_id: UUID | None = None) -> list[Workspace]:
    statement = select(Workspace)
    if user_id is not None:
        statement = statement.where(Workspace.user_id == user_id)
    result = await session.exec(statement)
    return result.all()


async def delete_workspace(session: AsyncSession, workspace_id: UUID) -> None:
    workspace = await session.get(Workspace, workspace_id)
    if workspace is None:
        return
    await session.delete(workspace)
    await session.commit()
