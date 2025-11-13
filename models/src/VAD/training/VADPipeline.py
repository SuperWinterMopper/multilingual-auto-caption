from ...common.PipelineStructure import ModelPipeline, PipelineLogger, PipelineTester
from ...common.logger import Logger

from .VADPipelineTester import VADPipelineTester
from .VADPipelineLogger import VADPipelineLogger

class VADPipeline(ModelPipeline):
    """
    VAD model training pipeline.
    """

    tester: PipelineTester = VADPipelineTester()
    logger: PipelineLogger = VADPipelineLogger(logger=Logger(name="VAD"))

    def run_pipeline(self, collect_data: bool, preprocess_data: bool, split_data: bool, train: bool, evaluate: bool, save_model: bool) -> None:
        """Run the model with the specified steps involved"""
        

    def _collect_data(self) -> None:
        """Collects data and puts it into /data for appropriate model"""
        ...

    def _preprocess_data(self) -> None:
        """Preprocesses the data stored under /data"""
        ...

    def _split_data(self) -> None:
        """Splits data into train, validation, test sets"""
        ...

    def _train(self) -> None:
        """Training method"""
        ...

    def _evaluate(self) -> None:
        """Model evaluation after finishing training"""
        ...

    def _save_model(self) -> None:
        """Saves model weights"""
        ...

    def _fail(self, text: str) -> None:
        """Failure method"""
        ...