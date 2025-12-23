
from ..src.VAD.training.MelSpecPipeline import MelSpecPipeline
from pathlib import Path
import torchcodec

def test_basic():
    pipeline = MelSpecPipeline(n_fft=512, sample_rate=16000, n_mel=40, hop_length=256)

    path = Path(__file__).resolve().parent / "materials" / "testscore.wav"

    assert path.exists()
    assert 4 == 4, "something wrong"