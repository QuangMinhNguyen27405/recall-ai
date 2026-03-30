import os

import asyncpg
import boto3
import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="RecallAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.environ["DATABASE_URL"]
AWS_ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
S3_BUCKET = os.environ.get("S3_BUCKET", "recallai-files")
OPENSEARCH_URL = os.environ["OPENSEARCH_URL"]


@app.get("/")
async def root():
    return {"message": "RecallAI API"}


@app.get("/health")
async def health():
    """
    Check the health of the application.
    """
    checks: dict[str, str] = {}

    # PostgreSQL
    try:
        dsn = DATABASE_URL.replace("+asyncpg", "")
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
            endpoint_url=AWS_ENDPOINT_URL,
            region_name=AWS_REGION,
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
        )
        existing = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
        if S3_BUCKET not in existing:
            s3.create_bucket(Bucket=S3_BUCKET)
        s3.list_objects_v2(Bucket=S3_BUCKET, MaxKeys=1)
        checks["s3"] = "ok"
    except Exception as e:
        checks["s3"] = f"error: {e}"

    # OpenSearch
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OPENSEARCH_URL}/_cluster/health")
            resp.raise_for_status()
            checks["opensearch"] = "ok"
    except Exception as e:
        checks["opensearch"] = f"error: {e}"

    all_ok = all(v == "ok" for v in checks.values())
    return {"healthy": all_ok, "services": checks}


def start():
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
