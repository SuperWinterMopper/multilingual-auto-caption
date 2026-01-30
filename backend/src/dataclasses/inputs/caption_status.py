from pydantic import BaseModel, Field
from uuid import uuid4, UUID
from typing import Optional
from .status import Status


class CaptionStatus(BaseModel):
    job_id: UUID = Field(default_factory=uuid4)
    status: Status = Status.UNINITIATED
    output_url: Optional[str] = None
    message: Optional[str] = None
