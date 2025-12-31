import boto3
from .data_loader import AppDataLoader
import uuid
import os 
import s3
import time
from datetime import datetime

BUCKET = os.getenv("UPLOAD_BUCKET")

class AppDataLoader():
    def __init__(self, logger: AppDataLoader, prod=False):
        self.s3_client = boto3.client('s3')
    
    @staticmethod
    def gen_s3_presigned_url() -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        key = f"uploads/videos/{timestamp}_{uuid.uuid4().hex}"
        expiration = 300  # 5 minutes
        content_type = "application/octet-stream"

        url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": BUCKET,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expiration, 
        )

        return {
            "uploadUrl": url,
            "bucket": BUCKET,
            "key": key,
            "expiresIn": expiration,
        }