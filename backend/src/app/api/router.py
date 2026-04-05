from fastapi import APIRouter

from app.chat_sessions.router import router as chat_sessions_router
from app.files.router import router as files_router
from app.users.router import router as users_router
from app.workspaces.router import router as workspaces_router

api_router = APIRouter(prefix="/api")
api_router.include_router(users_router)
api_router.include_router(workspaces_router)
api_router.include_router(files_router)
api_router.include_router(chat_sessions_router)
