from torchaudio.transforms import MelSpectrogram
import torch

class MelSpecPipeline(torch.nn.Module):
    def __init__(self, n_fft: int, sample_rate: int, n_mel: int, hop_length: int):
        super().__init__()
        self.mel_spec = MelSpectrogram(sample_rate=sample_rate, n_fft=n_fft, n_mels=n_mel, power=2, center=False, hop_length=hop_length)

    def forward(self, wave):
        assert wave.data.shape[0] == 1

        mel_spec = self.mel_spec(wave.data)
        return mel_spec