import asyncio
import sys

from app.chat_sessions.model import ChatSession  # noqa: F401
from app.db.session import AsyncSessionLocal
from app.files.model import File  # noqa: F401
from app.files import crud
from app.config.settings import settings
from app.users.model import User  # noqa: F401
from app.workspaces.model import Workspace  # noqa: F401

from langchain_community.document_loaders import S3FileLoader
from langchain_text_splitters import CharacterTextSplitter

async def start_ingestion(file_id: int) -> dict:
    """
    Start the ingestion pipeline for a file.
    """
    async with AsyncSessionLocal() as session:
        file = await crud.get_file(session, file_id)
        if file is None:
            raise ValueError(f"File id={file_id} not found")
        docs = load_file_from_s3(file.s3_key)
        return {"docs": docs}


def load_file_from_s3(s3_key: str):
    """
    Load a file from S3 and save it to the local filesystem.
    """
    loader = S3FileLoader(
        bucket=settings.s3_bucket,
        key=s3_key,
        endpoint_url=settings.aws_endpoint_url,
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
    docs = loader.load()
    print(docs)
    return docs

def split_documents(document, chunk_size: int = 1000, chunk_overlap: int = 200):
   text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


if __name__ == "__main__":
    file_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    result = asyncio.run(start_ingestion(file_id))
    
    print(f"Loaded {len(result['docs'])} docs for file_id={file_id}")
