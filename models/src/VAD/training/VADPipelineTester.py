from ...common.PipelineStructure import PipelineTester

class VADPipelineTester(PipelineTester):

    def link_pipeline(self, pipeline):
        self.pipeline = pipeline

    def btest_collect_data(self) -> None:
        ...

    def btest_preprocess_data(self) -> None:
        ...

    def btest_split_data(self) -> None:
        ...

    def btest_train(self) -> None:
        ...

    def btest_evaluate(self) -> None:
        ...

    def btest_save_model(self) -> None:
        ...

    def atest_collect_data(self) -> None:
        ...

    def atest_preprocess_data(self) -> None:
        ...

    def atest_split_data(self) -> None:
        ...

    def atest_train(self) -> None:
        ...

    def atest_evaluate(self) -> None:
        ...

    def atest_save_model(self) -> None:
        ...
