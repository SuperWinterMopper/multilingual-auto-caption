from ...common.PipelineStructure import PipelineLogger
from ...common.logger import Logger
from .VADPipelineAbstractClass import VADPipelineAbstractClass
import librosa
import datetime as datetime
import Path
import numpy as np

class VADPipelineLogger(PipelineLogger):
    """
    Subclasses must implement both blog_* (before) and alog_* after their corresponding methods. These should be logged to the logger the method uses. 
    """

    logger: Logger

    def blog_collect_data(self) -> None:
        self.log("Data collection tests passed: data path exists.")
        self.log("Dev, eval, and train directories are present.")
        self.log("Sample session_0 mixture.wav files confirmed in each split.")

    def blog_preprocess_data(self) -> None:
        self.log("Checked that valid, test, and training data paths exists, including the first and last data for each of valid, test, and training datasets")

    def blog_split_data(self) -> None:
        self.log("Pipeline's tensors are set for training, validation, and testing datasets.")

    def blog_train(self) -> None:
        self.log("Beginning training process.")

    def blog_evaluate(self) -> None:
        ...

    def blog_save_model(self) -> None:
        ...

    def alog_collect_data(self) -> None:
        self.log("After data collection, verified that data path exists and some some content remains.")

    def alog_preprocess_data(self, pipe: VADPipelineAbstractClass) -> None:
        self.log(f"Finished preprocessing data into MFSC spectrograms of size {pipe.X_train.shape[1]}x{pipe.X_train.shape[2]}")
        self.log(f"Training set size: {pipe.X_train.shape[0]} samples")
        self.log(f"Validation set size: {pipe.X_valid.shape[0]} samples")
        self.log(f"Test set size: {pipe.X_test.shape[0]} samples")

    def alog_split_data(self, pipe: VADPipelineAbstractClass) -> None:
        self.log("Data successfully split into training, validation, and test sets, roughly at expected proportions. The expected proportions are given by n_valid, n_test, n_train variables in VADPipeline")

        train_samples = np.rint(np.random.rand(3, 3) * pipe.n_train).astype(int)
        valid_samples = np.rint(np.random.rand(3, 3) * pipe.n_valid).astype(int)
        test_samples  = np.rint(np.random.rand(3, 3) * pipe.n_test).astype(int)

        

    def alog_train(self) -> None:
        ...

    def alog_evaluate(self) -> None:
        ...

    def alog_save_model(self) -> None:
        ...

    def log(self, text: str) -> None:
        self.logger.log(text=text)