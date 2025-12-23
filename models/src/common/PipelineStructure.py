import abc
import pydantic
from .logger import Logger

class PipelineLogger(pydantic.BaseModel, abc.ABC):
    """
    Abstract logger for model pipeline steps.
    Subclasses must implement both blog_* (before) and alog_* after their corresponding methods. These should be logged to the logger the method uses. 
    """

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    # the ModelPipeline which actually uses this logger.
    # Allows us to do self.pipe.variable to avoid passing in parameters
    logger: Logger
    pipeline = pydantic.PrivateAttr

    @abc.abstractmethod
    # def link_pipeline(self, pipeline):
    #     self.pipeline = pipeline

    @abc.abstractmethod
    def blog_collect_data(self) -> None:
        ...

    @abc.abstractmethod
    def blog_preprocess_data(self) -> None:
        ...

    @abc.abstractmethod
    def blog_split_data(self) -> None:
        ...

    @abc.abstractmethod
    def blog_train(self) -> None:
        ...

    @abc.abstractmethod
    def blog_evaluate(self) -> None:
        ...

    @abc.abstractmethod
    def blog_save_model(self) -> None:
        ...

    @abc.abstractmethod
    def alog_collect_data(self) -> None:
        ...

    @abc.abstractmethod
    def alog_preprocess_data(self) -> None:
        ...

    @abc.abstractmethod
    def alog_split_data(self) -> None:
        ...

    @abc.abstractmethod
    def alog_train(self) -> None:
        ...

    @abc.abstractmethod
    def alog_evaluate(self) -> None:
        ...

    @abc.abstractmethod
    def alog_save_model(self) -> None:
        ...
    
    @abc.abstractmethod
    def log(self, text: str) -> None:
        self.logger.log(text=text)


class PipelineTester(pydantic.BaseModel, abc.ABC):
    """
    Abstract testere for model pipeline steps.
    Subclasses must implement both blog_* (before) and alog_* after their corresponding methods. The pipeline will be halted if tests do not pass. 
    """

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    # the ModelPipeline which actually uses this logger.
    # Allows us to do self.pipe.variable to avoid passing in parameters
    pipeline = pydantic.PrivateAttr

    @abc.abstractmethod
    # def link_pipeline(self, pipeline):
    #     self.pipeline = pipeline

    @abc.abstractmethod
    def btest_collect_data(self, pipeline) -> None:
        ...

    @abc.abstractmethod
    def btest_preprocess_data(self) -> None:
        ...

    @abc.abstractmethod
    def btest_split_data(self) -> None:
        ...

    @abc.abstractmethod
    def btest_train(self) -> None:
        ...

    @abc.abstractmethod
    def btest_evaluate(self) -> None:
        ...

    @abc.abstractmethod
    def btest_save_model(self) -> None:
        ...

    @abc.abstractmethod
    def atest_collect_data(self, pipeline) -> None:
        ...

    @abc.abstractmethod
    def  atest_preprocess_data(self) -> None:
        ...

    @abc.abstractmethod
    def atest_split_data(self) -> None:
        ...

    @abc.abstractmethod
    def atest_train(self) -> None:
        ...

    @abc.abstractmethod
    def atest_evaluate(self) -> None:
        ...

    @abc.abstractmethod
    def atest_save_model(self) -> None:
        ...



class ModelPipeline(pydantic.BaseModel, abc.ABC):
    """
    Abstract model pipeline class. To be used by all models
    """

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    logger: PipelineLogger
    tester: PipelineTester

    @abc.abstractmethod
    def run_pipeline(self, collect_data: bool, preprocess_data: bool, split_data: bool, train: bool, evaluate: bool, save_model: bool) -> None:
        """Run the model with the specified steps involved"""
        ...

    @abc.abstractmethod
    def _collect_data(self) -> None:
        """Collects data and puts it into /data for appropriate model"""
        ...

    @abc.abstractmethod
    def _preprocess_data(self) -> None:
        """Preprocesses the data stored under /data"""
        ...

    @abc.abstractmethod
    def _split_data(self) -> None:
        """Splits data into train, validation, test sets"""
        ...

    @abc.abstractmethod
    def _train(self) -> None:
        """Training method"""
        ...

    @abc.abstractmethod
    def _evaluate(self) -> None:
        """Model evaluation after finishing training"""
        ...

    @abc.abstractmethod
    def _save_model(self) -> None:
        """Saves model weights"""
        ...

    @abc.abstractmethod
    def _fail(self, text: str) -> None:
        """Failure method"""
        ...