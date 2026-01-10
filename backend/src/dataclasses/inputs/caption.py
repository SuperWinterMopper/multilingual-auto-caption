from pydantic import BaseModel, field_validator, Field, AnyHttpUrl
from typing import Literal
import re
from ...components.consolidator import Consolidator
from ...components.slid_model import SLIDModel
from ...components.asr_model import ASRModel
from ...components.translater import AppTranslater

ALLOWED_LANGS = tuple(Consolidator.consolidate_allowed_langs([
    SLIDModel.get_allowed_langs(),
    ASRModel.get_allowed_langs(),
    AppTranslater.get_allowed_langs(),
]))

class CaptionInput(BaseModel):
    upload_url: AnyHttpUrl
    caption_color: str = "#FFFFFF"
    font_size: int = Field(default=48, ge=12, le=120)
    stroke_width: int = Field(default=4, ge=0, le=10)
    convert_to: str = Field(default="")
    explicit_langs: list[str] = Field(default_factory=list)
    
    @field_validator("caption_color")
    @classmethod
    def validate_caption_color(cls, v: str) -> str:
        if not re.compile(r"^#[0-9A-Fa-f]{6}$").fullmatch(v):
            raise ValueError("caption_color must be a hex color like '#FFFFFF'")
        return v.upper()
    
    @field_validator("convert_to")
    @classmethod
    def validate_convert_to(cls, v: str) -> str:
        if v and v not in ALLOWED_LANGS:
            raise ValueError(f"convert_to must be one of {ALLOWED_LANGS}, got '{v}'")
        return v