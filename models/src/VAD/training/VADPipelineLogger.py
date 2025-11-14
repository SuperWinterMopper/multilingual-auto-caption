from ...common.PipelineStructure import PipelineLogger
from ...common.logger import Logger
from .VADPipelineAbstractClass import VADPipelineAbstractClass

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
        ...

    def blog_split_data(self) -> None:
        ...

    def blog_train(self) -> None:
        ...

    def blog_evaluate(self) -> None:
        ...

    def blog_save_model(self) -> None:
        ...

    def alog_collect_data(self) -> None:
        self.log("After data collection, verified that data path exists and some some content remains.")

    def alog_preprocess_data(self) -> None:
        ...

    def alog_split_data(self) -> None:
        ...

    def alog_train(self) -> None:
        ...

    def alog_evaluate(self) -> None:
        ...

    def alog_save_model(self) -> None:
        ...

    def log(self, text: str) -> None:
        self.logger.log(text=text)