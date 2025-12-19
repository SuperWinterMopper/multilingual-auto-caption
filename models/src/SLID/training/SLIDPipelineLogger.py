from ...common.PipelineStructure import PipelineLogger
from ...common.logger import Logger

class SLIDPipelineLogger(PipelineLogger):
    """
    Subclasses must implement both blog_* (before) and alog_* after their corresponding methods. These should be logged to the logger the method uses. 
    """

    logger: Logger

    def link_pipeline(self, pipeline):
        self.pipeline = pipeline

    def blog_collect_data(self) -> None:
        ...

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
        ...

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