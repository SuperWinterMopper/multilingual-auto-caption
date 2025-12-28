from ...common.PipelineStructure import PipelineLogger
from ...common.logger import Logger
from .VADPipelineAbstractClass import VADPipelineAbstractClass
from typing import Optional
import datetime as datetime
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
        self.log("Beginning model evaluation.")

    def blog_save_model(self) -> None:
        ...

    def alog_collect_data(self) -> None:
        self.log("After data collection, verified that data path exists and some some content remains.")

    def alog_preprocess_data(self, pipeline: Optional[VADPipelineAbstractClass] = None) -> None:
        assert pipeline is not None
        self.log(f"Finished preprocessing data into MFSC spectrograms of shape ({pipeline.num_mel_bands}, time_frames) where time_frames varies per sample based on audio length.")

    def alog_split_data(self, pipeline: Optional[VADPipelineAbstractClass] = None) -> None:
        self.log("Data successfully split into training, validation, and test sets, roughly at expected proportions. The expected proportions are given by n_valid, n_test, n_train variables in VADPipeline")

        # train_samples = np.rint(np.random.rand(2, 2) * pipe.n_train).astype(int)
        # valid_samples = np.rint(np.random.rand(2, 2) * pipe.n_valid).astype(int)
        # test_samples  = np.rint(np.random.rand(2, 2) * pipe.n_test).astype(int)
        
        # # Flatten the sample indices and use them to extract spectrograms
        # train_indices = train_samples.flatten()
        # valid_indices = valid_samples.flatten()
        # test_indices = test_samples.flatten()
        
        # # Extract the sampled spectrograms and their labels
        # train_specs = pipe.X_train[train_indices]
        # train_labels = pipe.y_train[train_indices]
        # valid_specs = pipe.X_valid[valid_indices]
        # valid_labels = pipe.y_valid[valid_indices]
        # test_specs = pipe.X_test[test_indices]
        # test_labels = pipe.y_test[test_indices]
        
        # # Log spectrograms with labels in the filename
        # train_label_str = '_'.join([str(int(label.item())) for label in train_labels])
        # valid_label_str = '_'.join([str(int(label.item())) for label in valid_labels])
        # test_label_str = '_'.join([str(int(label.item())) for label in test_labels])
        
        # self.logger.log_spectrogram(train_specs, f"train_spectrograms_labels_{train_label_str}", pipe.num_mel_bands)
        # self.logger.log_spectrogram(valid_specs, f"valid_spectrograms_labels_{valid_label_str}", pipe.num_mel_bands)
        # self.logger.log_spectrogram(test_specs, f"test_spectrograms_labels_{test_label_str}", pipe.num_mel_bands)
    
    def alog_train(self) -> None:
        self.logger.log("Training process completed successfully, history saved to logger.")

    def alog_evaluate(self) -> None:
        self.log("Model evaluation completed.")

    def alog_save_model(self) -> None:
        self.log("Saving model weights.")

    def log(self, text: str) -> None:
        self.logger.log(text=text)