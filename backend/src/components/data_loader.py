from uuid import UUID
import boto3
from pydantic import AnyHttpUrl
from .logger_component import AppLogger
import os
import tempfile
from datetime import datetime
from urllib.parse import urlparse
from moviepy import VideoFileClip, CompositeVideoClip
from pathlib import Path
from ..dataclasses.inputs.caption_status import CaptionStatus, Status


class AppDataLoader:
    def __init__(self, logger: AppLogger, prod=False):
        self.logger = logger
        self.prod = prod

        try:
            self.s3_client = boto3.client("s3")
            self.logger.logger.info("S3 client successfully created")
        except Exception as e:
            self.logger.logger.error(f"Failed to create S3 client: {str(e)}")
            raise

        self.BUCKET = "multilingual-auto-caption"

        self.allowed_formats = (".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv")
        self.content_types = {
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".mkv": "video/x-matroska",
            ".flv": "video/x-flv",
            ".wmv": "video/x-ms-wmv",
        }
        self.aws_upload_dir = "uploads"
        self.aws_downloads_dir = "downloads"

        self.fonts = self.get_avail_fonts()

        self.temp_files = []

    @classmethod
    def get_avail_fonts(cls) -> list[Path]:
        fonts_dir = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts"

        return [
            fonts_dir / "NotoSans-Regular.ttf",
            fonts_dir / "NotoSans-Regular.ttf",
            fonts_dir / "NotoSansCJKjp-Regular.otf",
            fonts_dir / "NotoSansArabic-Regular.ttf",
            fonts_dir / "NotoSansDevanagari-Regular.ttf",
            fonts_dir / "NotoSansThai-Regular.ttf",
        ]

    def gen_s3_upload_url(self, filename: str) -> dict:
        if not filename.lower().endswith(self.allowed_formats):
            raise ValueError(
                f"Only {', '.join(self.allowed_formats)} files are supported"
            )

        try:
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            file_ext = filename[filename.rfind(".") :]
            key = f"{self.aws_upload_dir}/{timestamp}{file_ext}"
            expiration = 300  # 5 minutes
            content_type = self.content_types.get(file_ext.lower())
        except Exception as e:
            self.logger.logger.error(
                f"Error preparing presigned URL parameters: {str(e)}"
            )
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
                "upload_url": url,
                "bucket": self.BUCKET,
                "key": key,
                "expiresIn": expiration,
            }
        except Exception as e:
            self.logger.logger.error(f"Error generating presigned URL: {str(e)}")
            raise ConnectionError(
                f"Error in trying to generate presigned URL: {str(e)}"
            )

    def retrieve_video(self, s3_url: AnyHttpUrl) -> tuple[VideoFileClip, Path]:
        key = ""
        try:
            # AnyHttpUrl guarantees this is an http/https URL
            # Extract the path component directly (e.g., "/uploads/video.mp4")
            # Use .path to get just the path without query parameters
            key = urlparse(s3_url.unicode_string()).path.lstrip("/")

            self.logger.logger.info(f"Retrieving video from S3: {key}")
            if not key.lower().endswith(self.allowed_formats):
                raise ValueError(
                    f"For downloading, only {', '.join(self.allowed_formats)} files are supported. Given: {key}"
                )

            file_ext = key[key.rfind(".") :]

            # Create a temp file path in the logger's logs directory
            temp_file = tempfile.NamedTemporaryFile(
                suffix=file_ext, delete=False, dir=self.logger.log_root
            )
            temp_path = Path(temp_file.name)
            temp_file.close()

            self.temp_files.append(temp_path)

            # Stream download straight to disk
            with open(temp_path, "wb") as f:
                self.s3_client.download_fileobj(self.BUCKET, key, f)

            video_clip = VideoFileClip(temp_path)

            self.logger.logger.info(f"Successfully retrieved video: {key}")
            return video_clip, temp_path

        except self.s3_client.exceptions.NoSuchKey:
            self.logger.logger.error(f"Video not found in S3: {key}")
            raise FileNotFoundError(
                f"Video not found, need to have been uploaded beforehand: {key}"
            )
        except Exception as e:
            self.logger.logger.error(f"Error retrieving video: {str(e)}")
            raise

    def save_captioned_disk(self, video: CompositeVideoClip) -> Path:
        try:
            output_filename = (
                f"captioned_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.mp4"
            )

            # changed output to prevent weird behavior of writing to root directory which could break permissions on docker image
            output_path = Path(__file__).parent.parent / output_filename

            self.logger.logger.info(f"Saving captioned video to: {output_path}")
            video.write_videofile(str(output_path), codec="libx264", audio_codec="aac")

            # make sure to delete afterwards
            self.temp_files.append(output_path)

            self.logger.logger.info(
                f"Successfully saved captioned video: {output_path}"
            )

            return output_path
        except Exception as e:
            self.logger.logger.error(f"Error saving captioned video: {str(e)}")
            raise

    def save_captioned_s3(self, video_path: Path) -> tuple[str, str]:
        try:
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            file_ext = video_path.suffix
            key = f"{self.aws_downloads_dir}/{timestamp}{file_ext}"
            content_type = self.content_types.get(file_ext.lower())

            self.logger.logger.info(
                f"Uploading captioned video to S3: s3://{self.BUCKET}/{key}"
            )
        except Exception as e:
            self.logger.logger.error(f"Error preparing S3 upload parameters: {str(e)}")
            raise

        try:
            self.s3_client.upload_file(
                str(video_path),
                self.BUCKET,
                key,
                ExtraArgs={"ContentType": content_type},
            )
            self.logger.logger.info(
                f"Successfully uploaded captioned video to S3: s3://{self.BUCKET}/{key}"
            )

            return self.BUCKET, key

        except Exception as e:
            self.logger.logger.error(f"Error uploading captioned video to S3: {str(e)}")
            raise

    def gen_s3_download_url(
        self, bucket: str, key: str, expiration: int = 5 * 24 * 60 * 60
    ) -> str:
        """Generates s3 download url

        Args:
            bucket (str): S3 bucket
            key (str): S3 key
            expiration (int, optional): Expiration time. Defaults to 5*24*60*60 (5 days)

        Returns:
            str: download url
        """
        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": bucket,
                    "Key": key,
                },
                ExpiresIn=expiration,
            )
            self.logger.logger.info(
                f"Generated download URL for s3://{bucket}/{key} (expires in {expiration}s)"
            )
            return url
        except Exception as e:
            self.logger.logger.error(f"Error generating download URL: {str(e)}")
            raise

    def cleanup_temp_files(self):
        for temp_path in self.temp_files:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                self.logger.logger.info(f"Deleted temporary file: {temp_path}")
            else:
                self.logger.logger.warning(
                    f"Temporary file not found for deletion: {temp_path}"
                )
        self.temp_files = []  # clear temp files after cleanup

    def upload_status_file(self, caption_status: CaptionStatus):
        try:
            key = self.gen_status_file_key(caption_status.job_id)
            self.s3_client.put_object(
                Body=caption_status.model_dump_json(),
                Bucket=self.BUCKET,
                Key=key,
                ContentType="application/json",
            )
            self.logger.logger.info(
                f"Uploaded status file to S3: s3://{self.BUCKET}/{key}"
            )
        except Exception as e:
            self.logger.logger.error(f"Error uploading status file to S3: {str(e)}")
            raise

    def get_caption_status(self, job_id: UUID) -> CaptionStatus:
        try:
            key = self.gen_status_file_key(job_id)
            obj = self.s3_client.get_object(Bucket=self.BUCKET, Key=key)
            content = obj["Body"].read().decode("utf-8")
            try:
                return CaptionStatus.model_validate_json(content)
            except Exception as e:
                self.logger.logger.error(f"Error parsing status file JSON: {str(e)}")
                return CaptionStatus(
                    job_id=job_id,
                    status=Status.FAILED,
                    message="Error parsing status file JSON",
                )

        except self.s3_client.exceptions.NoSuchKey:
            return CaptionStatus(
                job_id=job_id,
                status=Status.UNINITIATED,
                message="No status file found for this job_id",
            )
        except Exception as e:
            self.logger.logger.error(f"Error retrieving status file from S3: {str(e)}")
            return CaptionStatus(
                job_id=job_id,
                status=Status.FAILED,
                message="Error retrieving status file from S3: " + str(e),
            )

    def gen_status_file_key(self, job_id: UUID) -> str:
        return f"{self.aws_upload_dir}/{str(job_id)}_status.txt"