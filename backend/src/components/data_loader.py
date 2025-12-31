import boto3
from .logger import AppLogger
import uuid
import os 
import s3
from datetime import datetime

class AppDataLoader():
    def __init__(self, logger: AppLogger, prod=False):
        self.s3_client = boto3.client('s3')
        self.BUCKET = os.getenv("UPLOAD_BUCKET")
        self.allowed_formats = ('.mp4', '.mp3', '.avi', '.mov', '.mkv', '.flv', '.wmv')
        self.content_types = {
            '.mp4': 'video/mp4',
            '.mp3': 'audio/mpeg',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.mkv': 'video/x-matroska',
            '.flv': 'video/x-flv',
            '.wmv': 'video/x-ms-wmv',
        }
        self.upload_dir = 'uploads'
        self.logger = logger
        self.prod = prod
        
    def gen_s3_presigned_url(self, filename: str) -> dict:
        if not filename.lower().endswith(self.allowed_formats):
            raise ValueError(f"Only {', '.join(self.allowed_formats)} files are supported")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = filename[filename.rfind('.'):]
        key = f"{self.upload_dir}/videos/{timestamp}_{uuid.uuid4().hex}{file_ext}"
        expiration = 300  # 5 minutes
        content_type = self.content_types.get(file_ext.lower())

        url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": self.BUCKET,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expiration, 
        )

        return {
            "uploadUrl": url,
            "bucket": self.BUCKET,
            "key": key,
            "expiresIn": expiration,
        }