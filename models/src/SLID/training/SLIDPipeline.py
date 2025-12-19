from ...common.PipelineStructure import ModelPipeline, PipelineLogger, PipelineTester
from ...common.logger import Logger

from .SLIDPipelineTester import SLIDPipelineTester
from .SLIDPipelineLogger import SLIDPipelineLogger

class SLIDPipeline(ModelPipeline):
    """
    SLID model training pipeline.
    """

    tester: PipelineTester = SLIDPipelineTester()
    logger: PipelineLogger = SLIDPipelineLogger(logger=Logger(name="SLID"))

    def run_pipeline(self, collect_data: bool, preprocess_data: bool, split_data: bool, train: bool, evaluate: bool, save_model: bool) -> None:
        """Run the model with the specified steps involved"""
        self._collect_data()        
        

    def _collect_data(self) -> None:
        """Collects data and puts it into /data for appropriate model"""
        self.tester.btest_collect_data()
        self.logger.blog_collect_data()

        pass

        self.tester.atest_collect_data()
        self.logger.alog_collect_data()

    def _preprocess_data(self) -> None:
        """Preprocesses the data stored under /data"""
        self.tester.btest_preprocess_data()
        self.logger.blog_preprocess_data()

        pass

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