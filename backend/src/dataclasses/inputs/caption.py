from pydantic import BaseModel, field_validator, Field, HttpUrl
from typing import Literal
from pydantic.dataclasses import dataclass
import re

class CaptionInput(BaseModel):
    upload_url: HttpUrl
    caption_color: str = "#FFFFFF"
    font_size: int = Field(default=48, ge=12, le=120)
    stroke_width: int = Field(default=4, ge=0, le=10)
    convert_to: str = "ORIG_LANG"
    explicit_langs: list[str] = Field(default_factory=list)
    
    @field_validator("caption_color")
    @classmethod
    def validate_caption_color(cls, v: str) -> str:
        if not re.compile(r"^#[0-9A-Fa-f]{6}$").fullmatch(v):
            raise ValueError("caption_color must be a hex color like '#FFFFFF'")
        return v.upper()