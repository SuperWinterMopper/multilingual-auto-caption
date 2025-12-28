from ...common.PipelineStructure import PipelineLogger, PipelineTester
from ...common.logger import Logger
from pathlib import Path
from .VADPipelineAbstractClass import VADPipelineAbstractClass
from typing import Optional

from .VADPipelineTester import VADPipelineTester
from .VADPipelineLogger import VADPipelineLogger
from .MelSpecPipeline import MelSpecPipeline
from .VADModel import VADModel
from .VADModelTrainer import VADModelTrainer

import torch
from torch.utils.data import TensorDataset
from torchcodec.decoders import AudioDecoder
import json
from json import JSONDecodeError
import numpy as np
import shutil
import gc

class VADPipeline(VADPipelineAbstractClass):
    """
    VAD model training pipeline.
    """
    tester: PipelineTester = VADPipelineTester()
    logger: PipelineLogger = VADPipelineLogger(logger=Logger(name="VAD"))

    data_path: Path = Path(__file__).resolve().parent.parent / "data" / "LibriParty" / "dataset"
    preprocessed_dir: Path = data_path / "preprocessed"
    preprocessed_files: list[Path] = [
        preprocessed_dir / "VAD_train_ds.pt",
        preprocessed_dir / "VAD_valid_ds.pt",
        preprocessed_dir / "VAD_test_ds.pt",
    ]
    
    model: VADModel = VADModel()
    model_definition_path: Path = Path(__file__).resolve().parent / "VADModel.py"
    model_weight_save_path: Path = Path(__file__).resolve().parent.parent / "data" / "vad_model.pth"
    
    backend_model_root: Path = Path(__file__).resolve().parent.parent.parent.parent.parent / "backend" / "model"
    
    windowed_signal_length: int = 512
    sample_rate: int = 16000
    num_mel_bands: int = 40
    overlap: int = 2
    hop_length: int = windowed_signal_length // overlap
    n_valid: int = 50
    n_test: int = 50
    n_train: int = 250

    X_train: Optional[torch.Tensor] = None
    y_train: Optional[torch.Tensor] = None
    X_valid: Optional[torch.Tensor] = None
    y_valid: Optional[torch.Tensor] = None
    X_test: Optional[torch.Tensor] = None
    y_test: Optional[torch.Tensor] = None
    
    mel_spec_pipeline: MelSpecPipeline = MelSpecPipeline(n_fft=windowed_signal_length, sample_rate=sample_rate, n_mel=num_mel_bands, hop_length=hop_length)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert self.model_definition_path.exists(), "Model definition file does not exist: " + str(self.model_definition_path)

    def run_pipeline(self, collect_data=False, preprocess_data=False, split_data=False, train=False, evaluate=False, save_model=False) -> None:
        """Run the model with the specified steps involved"""
        if collect_data:
            self._collect_data()
        if preprocess_data:
            self._preprocess_data()
        if split_data:
            self._split_data()
        if train:
            self._train()
        if evaluate:
            self._evaluate()
        if save_model:
            self._save_model()

    def _collect_data(self) -> None:
        """Collects data and puts it into /data for appropriate model"""
        self.tester.btest_collect_data(self)
        self.logger.blog_collect_data()

        pass

        self.tester.atest_collect_data(self)
        self.logger.alog_collect_data()

    @staticmethod
    def _gen_data_path(root: Path, id: int) -> Path:
        return root / f"session_{id}"

    def _create_mel_spectrogram_data(self, split_root: Path, session_id: int):
        """Create mel-spectrogram slices and labels for a single session."""
        session_dir = self._gen_data_path(split_root, session_id)

        def _check_audio_metadata(metadata):
            assert metadata.sample_rate == self.sample_rate
            assert metadata.num_channels == 1

        def _speechOverlap(mel_time_start, mel_time_end, speech_segments):
            for speech_start, speech_end in speech_segments:
                if speech_start < mel_time_end and mel_time_start < speech_end:
                    return True
            return False

        wav_path = session_dir / f"session_{session_id}_mixture.wav"
        json_path = session_dir / f"session_{session_id}.json"

        decoder = AudioDecoder(str(wav_path))

        metadata = decoder.metadata
        _check_audio_metadata(metadata)
        wave_len = metadata.duration_seconds_from_header

        speech_segments = set()
        with open(json_path, 'rb') as f:
            _raw = f.read()
        try:
            speech_info = json.loads(_raw.decode('utf-8'))
        except JSONDecodeError as _e:
            print(f'Error decoding JSON at file: {json_path}')
            _preview = repr(_raw[:400])
            raise RuntimeError(f"Failed to parse JSON file {json_path!r} (size={len(_raw)} bytes). preview={_preview}") from _e
        for key in speech_info:
            if key.isdigit():
                for info in speech_info[key]:
                    segment = (info["start"], info["stop"])
                    assert segment[0] < segment[1]
                    speech_segments.add(segment)

        samples = decoder.get_all_samples()
        mels = self.mel_spec_pipeline(samples)
        mels.squeeze_(0)

        num_data = mels.shape[1] // (self.num_mel_bands // self.overlap)
        one_mel_length_time = (self.windowed_signal_length // self.overlap) / self.sample_rate

        X = []
        y = []
        for i in range(num_data - 1):
            mel_slice_start = i * (self.num_mel_bands // self.overlap)
            mel_slice_end = mel_slice_start + self.num_mel_bands

            mel_time_start = mel_slice_start * one_mel_length_time
            mel_time_end = mel_slice_end * one_mel_length_time

            X.append(mels[:, mel_slice_start:mel_slice_end].clone().detach())
            y.append(torch.ones(1) if _speechOverlap(mel_time_start, mel_time_end, speech_segments) else torch.zeros(1))

            assert X[-1].shape == (self.num_mel_bands, self.num_mel_bands)
            assert y[-1].shape == (1,)

        X = torch.stack(X, dim=0)
        y = torch.stack(y, dim=0)

        # sanity check ensuring our speech time amount is more or less accurate
        times_to_check = np.arange(start=0, stop=wave_len, step=wave_len / num_data)
        speech_times = [int(_speechOverlap(times_to_check[i], times_to_check[i + 1], speech_segments)) for i in range(len(times_to_check) - 1)]
        speech_ratio_theory = sum(speech_times) / len(speech_times)
        speech_ratio_data = ((y == 1).sum() / len(y))
        required_closeness_percentage = .05
        if abs(speech_ratio_theory - speech_ratio_data) > required_closeness_percentage:
            print(f'theoretical ratio of speech lables: {speech_ratio_theory}')
            print(f"This data's ratio of speech labels: {speech_ratio_data}")
            assert False
        assert all(isinstance(x, torch.Tensor) for x in X)
        assert all(isinstance(t, torch.Tensor) for t in y)
        return X, y

    def _preprocess_data(self) -> None:
        """Preprocesses the data stored under /data"""
        
        # Check if preprocessed data already exists        
        if all(f.exists() for f in self.preprocessed_files):
            self.logger.log("Preprocessed data already exists. Loading from disk...")
            train_ds_tensors = torch.load(self.preprocessed_files[0], weights_only=True)
            valid_ds_tensors = torch.load(self.preprocessed_files[1], weights_only=True)
            test_ds_tensors = torch.load(self.preprocessed_files[2], weights_only=True)
            train_ds = torch.utils.data.TensorDataset(*train_ds_tensors)
            valid_ds = torch.utils.data.TensorDataset(*valid_ds_tensors)
            test_ds = torch.utils.data.TensorDataset(*test_ds_tensors)
            
            # Stored datasets use channel-first inputs: (N, 1, M, M). For pipeline logging, keep 3D (N, M, M).
            self.X_train, self.y_train = train_ds.tensors[0].squeeze(1), train_ds.tensors[1]
            self.X_valid, self.y_valid = valid_ds.tensors[0].squeeze(1), valid_ds.tensors[1]
            self.X_test, self.y_test = test_ds.tensors[0].squeeze(1), test_ds.tensors[1]
            self.logger.log("Successfully loaded preprocessed data from disk.")
            
            self.tester.atest_preprocess_data(self)
            self.logger.alog_preprocess_data(self)
            return
        
        train_root = self.data_path / "train"
        valid_root = self.data_path / "dev"
        test_root = self.data_path / "eval"

        self.tester.btest_preprocess_data(self)
        self.logger.blog_preprocess_data()

        def _process_split(root: Path, limit: int):
            X_parts = []
            Y_parts = []
            sessions = sorted([p for p in root.iterdir() if p.is_dir() and p.name.startswith("session_")])
            if limit:
                sessions = sessions[:limit]
            for i, session_dir in enumerate(sessions):
                raw_id = int(session_dir.name.split("_")[1])
                X_split, y_split = self._create_mel_spectrogram_data(root, raw_id)
                X_parts.append(X_split)
                Y_parts.append(y_split)
                
                if (i + 1) % 200 == 0 or (i + 1) == len(sessions):
                    self.logger.log(f"Processed {i + 1}/{len(sessions)} sessions")
                    
                    self.logger.log(f"Latest X_split shape: {X_split.shape}, dtype: {X_split.dtype}")
                    self.logger.log(f"Latest y_split shape: {y_split.shape}, dtype: {y_split.dtype}")
                    
                    speech_count = (y_split == 1).sum().item()
                    non_speech_count = (y_split == 0).sum().item()
                    total = len(y_split)
                    speech_ratio = speech_count / total if total > 0 else 0
                    self.logger.log(f"Speech samples: {speech_count}/{total} ({speech_ratio:.2%})")
                    
                    assert X_split.shape[0] == y_split.shape[0], f"Mismatch: X has {X_split.shape[0]} samples, y has {y_split.shape[0]}"
                    assert X_split.shape[1:] == (self.num_mel_bands, self.num_mel_bands), f"Expected shape (*, {self.num_mel_bands}, {self.num_mel_bands}), got {X_split.shape}"
                    self.logger.log(f"Validation passed for session `batch` ending at {i + 1}")
                    
            if not X_parts:
                raise RuntimeError(f"No usable data was produced under {root}. See logs for skipped sessions.")

            X_full = torch.cat(X_parts, dim=0)
            y_full = torch.cat(Y_parts, dim=0)
            return X_full, y_full
        
        # Create directory to store preprocessed datasets to disk
        self.preprocessed_dir.mkdir(parents=True, exist_ok=True)

        # process each split, and make sure to empty variables to not crash RAM
        self.X_train, self.y_train = _process_split(train_root, self.n_train)
        train_ds = TensorDataset(self.X_train.unsqueeze(1), self.y_train)
        self.logger.log(f"Saving train dataset to {self.preprocessed_files[0]}")
        torch.save(train_ds.tensors, self.preprocessed_files[0])
        del train_ds
        self.X_train, self.y_train = None, None
        gc.collect()
        
        self.X_valid, self.y_valid = _process_split(valid_root, self.n_valid)
        valid_ds = TensorDataset(self.X_valid.unsqueeze(1), self.y_valid)
        self.logger.log(f"Saving valid dataset to {self.preprocessed_files[1]}")
        torch.save(valid_ds.tensors, self.preprocessed_files[1])
        del valid_ds
        self.X_valid, self.y_valid = None, None
        gc.collect()
        
        self.X_test, self.y_test = _process_split(test_root, self.n_test)
        test_ds = TensorDataset(self.X_test.unsqueeze(1), self.y_test)
        self.logger.log(f"Saving test dataset to {self.preprocessed_files[2]}")
        torch.save(test_ds.tensors, self.preprocessed_files[2])
        del test_ds
        self.X_test, self.y_test = None, None
        gc.collect()
        
        self.tester.atest_preprocess_data(self)
        self.logger.alog_preprocess_data(self)

    def _split_data(self) -> None:
        """Splits data into train, validation, test sets"""
        self.tester.btest_split_data(self)
        self.logger.blog_split_data()

        # the data is already split during preprocessing
        pass

        self.tester.atest_split_data(self)
        self.logger.alog_split_data(self)

    def _train(self) -> None:
        """Training method"""
        self.tester.btest_train(self)
        self.logger.blog_train()
        
        self.trainer: VADModelTrainer = VADModelTrainer (
            model=self.model, 
            logger=self.logger.logger,
            loss_fn = torch.nn.BCELoss(),
            train_ds_path = str(self.preprocessed_files[0]),
            valid_ds_path = str(self.preprocessed_files[1]),
            test_ds_path = str(self.preprocessed_files[2]),
            batch_size = 32
        )
        
        self.trainer.train(num_epochs=20)
        
        self.tester.atest_train(self)
        self.logger.alog_train()

    def _evaluate(self) -> None:
        """Model evaluation after finishing training"""
        self.tester.btest_evaluate(self)
        self.logger.blog_evaluate()
        
        self.trainer.evaluate()
        
        self.tester.atest_evaluate(self)
        self.logger.alog_evaluate()

    def _save_model(self) -> None:
        """Saves model weights"""
        self.tester.btest_save_model(self)
        self.logger.blog_save_model()

        self.trainer.save_model(self.model_weight_save_path)

        self.tester.atest_save_model(self)
        self.logger.alog_save_model()
        
        self._copy_model_to_backend()
        self.logger.log("Model copied to backend successfully.")
    
    def _copy_model_to_backend(self):
        """Copies model weights + model definition into backend for inference use."""
        backend_root = self.backend_model_root
        backend_root.mkdir(parents=True, exist_ok=True)

        # Copy weights (saved by trainer.save_model)
        src_weights = self.model_weight_save_path
        dst_weights = backend_root / "vad_model.pth"
        if not src_weights.exists():
            raise FileNotFoundError(f"Model weights not found at {src_weights}")
        shutil.copy2(src_weights, dst_weights)
        self.logger.log(f"Copied model weights to backend at {dst_weights}")

        # Copy model definition file
        src_def = self.model_definition_path
        dst_def = backend_root / src_def.name  # "VADModel.py"
        if not src_def.exists():
            raise FileNotFoundError(f"Model definition not found at {src_def}")
        shutil.copy2(src_def, dst_def)
        self.logger.log(f"Copied model definition to backend at {dst_def}")