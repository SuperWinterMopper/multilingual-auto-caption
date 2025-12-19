from ...common.PipelineStructure import ModelPipeline, PipelineLogger, PipelineTester
from pathlib import Path
import torch

class VADPipelineAbstractClass(ModelPipeline):
    tester: PipelineTester
    logger: PipelineLogger

    data_path: Path

    windowed_signal_length: int
    sample_rate: int
    num_mel_bands: int
    overlap: int
    hop_length: int
    X_train: torch.Tensor
    y_train: torch.Tensor
    X_valid: torch.Tensor
    y_valid: torch.Tensor
    X_test: torch.Tensor
    y_test: torch.Tensor
    n_valid: int
    n_test: int
    n_train: int
