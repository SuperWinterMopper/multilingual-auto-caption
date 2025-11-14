from ...common.PipelineStructure import PipelineLogger, PipelineTester
from ...common.logger import Logger
from pathlib import Path
from .VADPipelineAbstractClass import VADPipelineAbstractClass

from .VADPipelineTester import VADPipelineTester
from .VADPipelineLogger import VADPipelineLogger
from .MelSpecPipeline import MelSpecPipeline

class VADPipeline(VADPipelineAbstractClass):
    """
    VAD model training pipeline.
    """

    tester: PipelineTester = VADPipelineTester()
    logger: PipelineLogger = VADPipelineLogger(logger=Logger(name="VAD"))

    data_path: Path = Path(__file__).resolve().parent.parent / "data" / "LibriParty" / "dataset"    

    windowed_signal_length = 512
    sample_rate = 16000
    num_mel_bands = 40
    overlap = 2
    hop_length = windowed_signal_length // overlap

    mel_spec_pipeline: MelSpecPipeline = MelSpecPipeline(n_fft=windowed_signal_length, sample_rate=sample_rate, n_mel=num_mel_bands, hop_length=hop_length)

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

        # data is locally stored currently
        pass

        self.tester.atest_collect_data(self)
        self.logger.alog_collect_data()

    def _preprocess_data(self) -> None:
        """Preprocesses the data stored under /data"""
        self.tester.btest_preprocess_data()
        self.logger.blog_preprocess_data()
    
        

        self.tester.atest_preprocess_data()
        self.logger.alog_preprocess_data()

    def _split_data(self) -> None:
        """Splits data into train, validation, test sets"""
        self.tester.btest_split_data()
        self.logger.blog_split_data()

        pass

        self.tester.atest_split_data()
        self.logger.alog_split_data()

    def _train(self) -> None:
        """Training method"""
        self.tester.btest_train()
        self.logger.blog_train()

        pass

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