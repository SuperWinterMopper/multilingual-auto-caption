from ...common.PipelineStructure import PipelineTester
from .VADPipelineAbstractClass import VADPipelineAbstractClass

class VADPipelineTester(PipelineTester):

    def btest_collect_data(self, pipeline: VADPipelineAbstractClass) -> None:
        """Ensures the data directory exists and contains expected files after data collection"""
        assert pipeline.data_path.exists(), "Data path does not exist: " + str(pipeline.data_path)

        dev = pipeline.data_path / "dev"
        eval = pipeline.data_path / "eval"
        train = pipeline.data_path / "train"

        assert dev.exists(), "Dev path does not exist: " + str(dev)
        assert eval.exists(), "Eval path does not exist: " + str(eval)
        assert train.exists(), "Train path does not exist: " + str(train)

        dev_session_0 = dev / "session_0" / "session_0_mixture.wav"
        eval_session_0 = eval / "session_0" / "session_0_mixture.wav"
        train_session_0 = train / "session_0" / "session_0_mixture.wav"

        assert dev_session_0.exists(), "Dev session 0 mixture does not exist: " + str(dev_session_0)
        assert eval_session_0.exists(), "Eval session 0 mixture does not exist: " + str(eval_session_0)
        assert train_session_0.exists(), "Train session 0 mixture does not exist: " + str(train_session_0)

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

    def atest_collect_data(self, pipeline: VADPipelineAbstractClass) -> None:
        assert pipeline.data_path.exists(), "Data path does not exist: " + str(pipeline.data_path)

        dev = pipeline.data_path / "dev"
        eval = pipeline.data_path / "eval"
        train = pipeline.data_path / "train"

        assert dev.exists(), "Dev path does not exist: " + str(dev)
        assert eval.exists(), "Eval path does not exist: " + str(eval)
        assert train.exists(), "Train path does not exist: " + str(train)

        dev_session_0 = dev / "session_0" / "session_0_mixture.wav"
        eval_session_0 = eval / "session_0" / "session_0_mixture.wav"
        train_session_0 = train / "session_0" / "session_0_mixture.wav"

        assert dev_session_0.exists(), "Dev session 0 mixture does not exist: " + str(dev_session_0)
        assert eval_session_0.exists(), "Eval session 0 mixture does not exist: " + str(eval_session_0)
        assert train_session_0.exists(), "Train session 0 mixture does not exist: " + str(train_session_0)

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