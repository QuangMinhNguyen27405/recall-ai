import boto3
from app.config.settings import settings

s3_client = boto3.client('s3')

def ingestion_pipeline(file_id: str, s3_key: str):
    """
    Ingestion pipeline for the recallai project.
    """
    
    s3_client.download_file(settings.s3_bucket, s3_key, f"{file_id}.pdf")
    
    return file_id