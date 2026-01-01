import boto3
from .logger import AppLogger
import uuid
import os 
import tempfile
from datetime import datetime
from urllib.parse import urlparse
from moviepy import VideoFileClip

class AppDataLoader():
    def __init__(self, logger: AppLogger, prod=False):
        self.logger = logger
        self.prod = prod
        
        try:
            self.s3_client = boto3.client('s3')
            self.logger.logger.info("S3 client successfully created")
        except Exception as e:
            self.logger.logger.error(f"Failed to create S3 client: {str(e)}")
            raise
        
        self.BUCKET = os.getenv("UPLOAD_BUCKET")
        if not self.BUCKET:
            raise ValueError("UPLOAD_BUCKET environment variable is not set")

        self.allowed_formats = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
        self.content_types = {
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.mkv': 'video/x-matroska',
            '.flv': 'video/x-flv',
            '.wmv': 'video/x-ms-wmv',
        }
        self.upload_dir = 'uploads'
        
        self.temp_files = []    
        
    def gen_s3_presigned_url(self, filename: str) -> dict:
        if not filename.lower().endswith(self.allowed_formats):
            raise ValueError(f"Only {', '.join(self.allowed_formats)} files are supported")
        
        try:
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            file_ext = filename[filename.rfind('.'):]
            key = f"{self.upload_dir}/videos/{timestamp}_{uuid.uuid4().hex}{file_ext}"
            expiration = 300  # 5 minutes
            content_type = self.content_types.get(file_ext.lower())
        except Exception as e:
            self.logger.logger.error(f"Error preparing presigned URL parameters: {str(e)}")
            raise
            
        try:
            url = self.s3_client.generate_presigned_url(
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
        except Exception as e:
            self.logger.logger.error(f"Error generating presigned URL: {str(e)}")
            raise
        
    def retrieve_video(self, s3_url: str) -> VideoFileClip:
        key = ""
        try:
            if s3_url.startswith("http"):
                parsed = urlparse(s3_url)
                key = parsed.path.lstrip("/")
            else:
                key = s3_url

            self.logger.logger.info(f"Retrieving video from S3: {key}")
            if not key.lower().endswith(self.allowed_formats):
                raise ValueError(f"For downloading, only {', '.join(self.allowed_formats)} files are supported")

            file_ext = key[key.rfind("."):]

            # Create a temp file path in the logger's logs directory
            temp_file = tempfile.NamedTemporaryFile(
                suffix=file_ext, 
                delete=False,
                dir=self.logger.logs_root
            )
            temp_path = temp_file.name
            temp_file.close()
            
            self.temp_files.append(temp_path)

            # Stream download straight to disk
            with open(temp_path, "wb") as f:
                self.s3_client.download_fileobj(self.BUCKET, key, f)

            video_clip = VideoFileClip(temp_path)

            self.logger.logger.info(f"Successfully retrieved video: {key}")
            return video_clip

        except self.s3_client.exceptions.NoSuchKey:
            self.logger.logger.error(f"Video not found in S3: {key}")
            raise FileNotFoundError(f"Video not found, need to have been uploaded beforehand: {key}")
        except Exception as e:
            self.logger.logger.error(f"Error retrieving video: {str(e)}")
            raise
    
    def cleanup_temp_files(self):
        for temp_path in self.temp_files:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                self.logger.logger.info(f"Deleted temporary file: {temp_path}")
            else:
                self.logger.logger.warning(f"Temporary file not found for deletion: {temp_path}")
        self.temp_files = [] # clear temp files after cleanup