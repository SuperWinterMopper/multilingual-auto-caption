from dataclasses import dataclass, field
from pathlib import Path
     
@dataclass
class AppInput:
    video_path: Path
    caption_color: str = "#FFFFFF"
    font_size: int = 48
    stroke_width: int = 4
    convert_to: str = "en"  
    explicit_langs: list[str] = field(default_factory=list)