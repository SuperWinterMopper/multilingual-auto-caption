from pydantic import BaseModel, field_validator


class PresignedInput(BaseModel):
    filename: str

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        allowed_formats = (".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv")
        if not v.lower().endswith(allowed_formats):
            raise ValueError(f"Only {', '.join(allowed_formats)} files are supported")
        return v
