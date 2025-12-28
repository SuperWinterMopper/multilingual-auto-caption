from ...common.PipelineStructure import ModelPipeline, PipelineLogger, PipelineTester
from .VADModelTrainer import VADModelTrainer
from pathlib import Path
import torch
from .VADModel import VADModel
from .VADModelTrainer import VADModelTrainer

class VADPipelineAbstractClass(ModelPipeline):
    tester: PipelineTester
    logger: PipelineLogger

    data_path: Path
    
    model: VADModel
    trainer: VADModelTrainer | None = None
    
    preprocessed_dir: Path
    preprocessed_files: list[Path]

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
