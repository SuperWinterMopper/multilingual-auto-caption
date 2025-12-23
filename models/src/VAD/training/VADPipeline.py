from ...common.PipelineStructure import PipelineLogger, PipelineTester
from ...common.logger import Logger
from pathlib import Path
from .VADPipelineAbstractClass import VADPipelineAbstractClass
from typing import ClassVar

from .VADPipelineTester import VADPipelineTester
from .VADPipelineLogger import VADPipelineLogger
from .MelSpecPipeline import MelSpecPipeline
from .VADModel import VADModel
from .VADModelTrainer import VADModelTrainer

import torch
from torchcodec.decoders import AudioDecoder
import json 
from json import JSONDecodeError
import numpy as np

class VADPipeline(VADPipelineAbstractClass):
    """
    VAD model training pipeline.
    """
    
    def __init__(self) -> None:
        self.tester: PipelineTester = VADPipelineTester()
        self.logger: PipelineLogger = VADPipelineLogger(logger=Logger(name="VAD"))

        self.data_path: Path = Path(__file__).resolve().parent.parent / "data" / "LibriParty" / "dataset"
        self.preprocessed_dir = self.data_path / "preprocessed"
        self.preprocessed_files = [
            self.preprocessed_dir / "VAD_X_train.pt",
            self.preprocessed_dir / "VAD_y_train.pt",
            self.preprocessed_dir / "VAD_X_valid.pt",
            self.preprocessed_dir / "VAD_y_valid.pt",
            self.preprocessed_dir / "VAD_X_test.pt",
            self.preprocessed_dir / "VAD_y_test.pt",
        ]
        
        self.model = VADModel(logger=self.logger)
        self.trainer = VADModelTrainer(
            model=self.model, 
            logger=self.logger,
            loss_fn = torch.nn.BCELoss(),
            optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001),
            train_ds_path = str(self.data_path / "preprocessed" / "VAD_X_train.pt"),
            valid_ds_path = str(self.data_path / "preprocessed" / "VAD_X_valid.pt"),
            batch_size = 32
        )
        
        self.windowed_signal_length: int = 512
        self.sample_rate: int = 16000
        self.num_mel_bands: ClassVar[int] = 40
        self.overlap: int = 2
        self.hop_length: int = self.windowed_signal_length // self.overlap
        self.n_valid: int = 50
        self.n_test: int = 50
        self.n_train: int = 250

        self.X_train: torch.Tensor = None
        self.y_train: torch.Tensor = None
        self.X_valid: torch.Tensor = None
        self.y_valid: torch.Tensor = None
        self.X_test: torch.Tensor = None
        self.y_test: torch.Tensor = None
        
        
        self.mel_spec_pipeline: MelSpecPipeline = MelSpecPipeline(n_fft=self.windowed_signal_length, sample_rate=self.sample_rate, n_mel=self.num_mel_bands, hop_length=self.hop_length)

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
            self.X_train = torch.load(self.preprocessed_files[0])
            self.y_train = torch.load(self.preprocessed_files[1])
            self.X_valid = torch.load(self.preprocessed_files[2])
            self.y_valid = torch.load(self.preprocessed_files[3])
            self.X_test = torch.load(self.preprocessed_files[4])
            self.y_test = torch.load(self.preprocessed_files[5])
            self.logger.log("Successfully loaded preprocessed data from disk.")
            
            self.tester.atest_preprocess_data(self)
            self.logger.alog_preprocess_data(self)
            return
        
        train_root = self.data_path / "train"
        valid_root = self.data_path / "dev"
        test_root = self.data_path / "eval"

        self.tester.btest_preprocess_data(self, train_root, valid_root, test_root)
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
                return None, None
            X_full = torch.cat(X_parts, dim=0)
            y_full = torch.cat(Y_parts, dim=0)
            return X_full, y_full

        # process each split
        self.X_train, self.y_train = _process_split(train_root, self.n_train)
        self.X_valid, self.y_valid = _process_split(valid_root, self.n_valid)
        self.X_test,  self.y_test  = _process_split(test_root,  self.n_test)

        # Save preprocessed data to disk
        self.preprocessed_dir.mkdir(parents=True, exist_ok=True)
        self.logger.log("Saving preprocessed data to disk...")
        torch.save(self.X_train, self.preprocessed_files[0])
        torch.save(self.y_train, self.preprocessed_files[1])
        torch.save(self.X_valid, self.preprocessed_files[2])
        torch.save(self.y_valid, self.preprocessed_files[3])
        torch.save(self.X_test, self.preprocessed_files[4])
        torch.save(self.y_test, self.preprocessed_files[5])
        self.logger.log(f"Preprocessed data saved to {self.preprocessed_dir}")

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
        self.tester.btest_train()
        self.logger.blog_train()

        self.trainer.train(num_epochs=20)
        
        self.tester.atest_train()
        self.logger.alog_train()

    def _evaluate(self) -> None:
        """Model evaluation after finishing training"""
        self.tester.btest_evaluate()
        self.logger.blog_evaluate()

        pass

        self.tester.atest_evaluate()
        self.logger.alog_evaluate()

    def _save_model(self) -> None:
        """Saves model weights"""
        self.tester.btest_save_model()
        self.logger.blog_save_model()

        pass

        self.tester.atest_save_model()
        self.logger.alog_save_model()

    def _fail(self, text: str) -> None:
        """Failure method"""
        ...