import os
from contextlib import asynccontextmanager

import asyncpg
import boto3
import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from app.config.logger import logger
from app.config.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        engine = create_async_engine(settings.database_url)
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        await engine.dispose()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise e
    yield

app = FastAPI(title="RecallAI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)   
@app.get("/health")
async def health():
    """
    Check the health of the application.
    """
    checks: dict[str, str] = {}

    # PostgreSQL
    try:
        dsn = settings.database_url.replace("+asyncpg", "")
        conn = await asyncpg.connect(dsn)
        await conn.execute("SELECT 1")
        await conn.close()
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {e}"

    # S3 via LocalStack
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.aws_endpoint_url,
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
        )
        existing = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
        if settings.s3_bucket not in existing:
            s3.create_bucket(Bucket=settings.s3_bucket)
        s3.list_objects_v2(Bucket=settings.s3_bucket, MaxKeys=1)
        checks["s3"] = "ok"
    except Exception as e:
        checks["s3"] = f"error: {e}"

    # OpenSearch
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.opensearch_url}/_cluster/health")
            resp.raise_for_status()
            checks["opensearch"] = "ok"
    except Exception as e:
        checks["opensearch"] = f"error: {e}"

    all_ok = all(v == "ok" for v in checks.values())
    return {"healthy": all_ok, "services": checks}

def start():
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
