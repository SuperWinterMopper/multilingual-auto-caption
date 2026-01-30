from dataclasses import dataclass
import torch
import uuid

unknown_language = "UNKNOWN_LANG"
unknown_text = "UNKNOWN_TEXT"


@dataclass
class AudioSegment:
    audio: torch.Tensor
    start_time: float
    end_time: float
    orig_file: str
    sample_rate: int
    lang: str = unknown_language  # language of subtitle, not audio
    text: str = unknown_text  # should align with lang property
    id: uuid.UUID = uuid.uuid4()
