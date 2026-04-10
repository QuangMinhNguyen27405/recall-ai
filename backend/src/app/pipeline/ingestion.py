import asyncio
import datetime
import hashlib
import sys
from uuid import UUID
from urllib.parse import urlparse

from app.chat_sessions.model import ChatSession  # noqa: F401
from app.db.session import AsyncSessionLocal
from app.files.model import File  # noqa: F401
from app.files import crud
from app.config.settings import settings
from app.users.model import User  # noqa: F401
from app.workspaces.model import Workspace  # noqa: F401

from langchain_community.document_loaders import S3FileLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.helpers import bulk


INDEX_NAME = "notes"
EMBEDDING_DIMENSION = 384

async def start_ingestion(file_id: UUID) -> dict:
    """
    Start the ingestion pipeline for a file.
    """
    async with AsyncSessionLocal() as session:
        
        try: 
                
            file = await crud.get_file(session, file_id)
            if file is None:
                raise ValueError(f"File id={file_id} not found")
            
            await crud.update_file(session, file_id, {"status": "processing"})

            workspace_name = ""
            if file.workspace_id is not None:
                workspace = await session.get(Workspace, file.workspace_id)
                if workspace is not None:
                    workspace_name = workspace.name

            docs = load_file_from_s3(file.s3_key)
            chunks = split_documents(docs, chunk_size=300, chunk_overlap=40)

            opensearch_client = create_opensearch_client()
            ensure_notes_index(opensearch_client)
            deleted_count = delete_existing_file_chunks(
                opensearch_client=opensearch_client,
                file_id=file.id,
            )
            
            indexed_count = index_chunks(
                opensearch_client=opensearch_client,
                chunks=chunks,
                file=file,
                workspace_name=workspace_name,
            )
            
            await crud.update_file(session, file.id, {"status": "ready", "ingested_at": datetime.datetime.now() })
        except Exception as e:
            await crud.update_file(session, file.id, {"status": "error", "error_reason": str(e)})
            raise e
        finally:
            await session.commit()
            return {
                "docs_count": len(docs),
                "chunks_count": len(chunks),
                "deleted_count": deleted_count,
                "indexed_count": indexed_count,
            }


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
    return docs


def split_documents(document, chunk_size: int = 1000, chunk_overlap: int = 200):
    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    chunks = text_splitter.split_documents(document)
    return chunks


def create_opensearch_client() -> OpenSearch:
    opensearch_url = settings.opensearch_url
    if "://" in opensearch_url:
        parsed = urlparse(opensearch_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 9200)
        scheme = parsed.scheme
    else:
        host = opensearch_url
        port = 9200
        scheme = "http"

    return OpenSearch(
        hosts=[{"host": host, "port": port, "scheme": scheme}],
        use_ssl=scheme == "https",
        verify_certs=False,
        connection_class=RequestsHttpConnection,
    )


def ensure_notes_index(opensearch_client: OpenSearch) -> None:
    index_body = {
        "settings": {"index.knn": True},
        "mappings": {
            "properties": {
                "embedding": {
                    "type": "knn_vector",
                    "dimension": EMBEDDING_DIMENSION,
                },
                "content": {"type": "text"},
                "file_id": {"type": "keyword"},
                "file_name": {"type": "keyword"},
                "workspace_id": {"type": "keyword"},
                "workspace_name": {"type": "keyword"},
                "page": {"type": "integer"},
            }
        },
    }

    if not opensearch_client.indices.exists(index=INDEX_NAME):
        opensearch_client.indices.create(index=INDEX_NAME, body=index_body)
        return

    opensearch_client.indices.put_mapping(
        index=INDEX_NAME, body=index_body["mappings"]
    )


def resolve_page_number(chunk, fallback: int) -> int:
    page = chunk.metadata.get("page") if chunk.metadata else None
    try:
        return int(page) if page is not None else fallback
    except (TypeError, ValueError):
        return fallback


def delete_existing_file_chunks(opensearch_client: OpenSearch, file_id: UUID | None) -> int:
    if file_id is None:
        return 0

    response = opensearch_client.delete_by_query(
        index=INDEX_NAME,
        body={"query": {"term": {"file_id": str(file_id)}}},
        conflicts="proceed",
        refresh=True,
    )
    return int(response.get("deleted", 0))


def chunk_document_id(file_id: UUID | None, page: int, chunk_text: str, ordinal: int) -> str:
    payload = f"{file_id or 'unknown'}:{page}:{ordinal}:{chunk_text}".encode("utf-8")
    digest = hashlib.sha1(payload).hexdigest()
    return f"{file_id or 'unknown'}:{page}:{ordinal}:{digest}"


def index_chunks(
    opensearch_client: OpenSearch,
    chunks,
    file: File,
    workspace_name: str,
) -> int:
    if not chunks:
        return 0

    texts = [chunk.page_content for chunk in chunks]
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-small", 
        dimensions=EMBEDDING_DIMENSION,
        openai_api_key=settings.openai_api_key,
    )
    vectors = embedding_model.embed_documents(texts)

    actions = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors, strict=False), start=1):
        page = resolve_page_number(chunk, fallback=i)
        actions.append(
            {
                "_index": INDEX_NAME,
                "_id": chunk_document_id(
                    file_id=file.id,
                    page=page,
                    chunk_text=chunk.page_content,
                    ordinal=i,
                ),
                "_source": {
                    "embedding": vector,
                    "content": chunk.page_content,
                    "file_id": str(file.id) if file.id is not None else "",
                    "file_name": file.name,
                    "workspace_id": (
                        str(file.workspace_id) if file.workspace_id is not None else ""
                    ),
                    "workspace_name": workspace_name,
                    "page": page,
                },
            }
        )

    bulk(opensearch_client, actions)
    return len(actions)


if __name__ == "__main__":
    for file_id in range(1, 3):
        result = asyncio.run(start_ingestion(file_id))
        print(
            f"Loaded {result['docs_count']} docs, split into {result['chunks_count']} chunks, "
            f"deleted {result['deleted_count']} existing chunks, "
            f"indexed {result['indexed_count']} docs into '{INDEX_NAME}' "
            f"for file_id={file_id}"
        )
