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

    def btest_preprocess_data(self, pipeline: VADPipelineAbstractClass, train_root, valid_root, test_root) -> None:
        assert train_root.exists(), train_root
        assert valid_root.exists(), valid_root
        assert test_root.exists(), test_root

        assert pipeline._gen_data_path(train_root, 0).exists()
        assert pipeline._gen_data_path(valid_root, 0).exists()
        assert pipeline._gen_data_path(test_root, 0).exists()
        assert pipeline._gen_data_path(train_root, pipeline.n_train - 1).exists()
        assert pipeline._gen_data_path(valid_root, pipeline.n_valid - 1).exists()
        assert pipeline._gen_data_path(test_root, pipeline.n_test - 1).exists()

    def btest_split_data(self, pipe: VADPipelineAbstractClass) -> None:
        assert pipe.X_train is not None and pipe.y_train is not None, "Training data not set"
        assert pipe.X_valid is not None and pipe.y_valid is not None, "Validation data not set"
        assert pipe.X_test is not None and pipe.y_test is not None, "Test data not set"

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

    def atest_preprocess_data(self, pipe: VADPipelineAbstractClass) -> None:
        assert pipe.X_train is not None and pipe.y_train is not None, "Training data not set"
        assert pipe.X_valid is not None and pipe.y_valid is not None, "Validation data not set"
        assert pipe.X_test is not None and pipe.y_test is not None, "Test data not set"

        assert pipe.X_test.shape[0] == pipe.y_test.shape[0], "Test data size mismatch"
        assert pipe.X_train.shape[0] == pipe.y_train.shape[0], "Train data size mismatch"
        assert pipe.X_valid.shape[0] == pipe.y_valid.shape[0], "Validation data size mismatch"

        for t in [pipe.X_test, pipe.X_train, pipe.X_valid]:
            assert t.shape[1] == t.shape[2] == pipe.num_mel_bands, "Spectrogram tensors are not the right size of num_mel_bands x num_mel_bands"

    def atest_split_data(self, pipe: VADPipelineAbstractClass) -> None:
        margin_of_error = .05 # 5 percent error ok

        assert abs(abs(pipe.X_train.shape[0] / pipe.X_valid.shape[0] - (pipe.n_train / pipe.n_valid)) < margin_of_error), "the difference in expected proportion of data between X_train and X_valid is too large."
        assert abs(abs(pipe.X_train.shape[0] / pipe.X_test.shape[0] - (pipe.n_train / pipe.n_test)) < margin_of_error), "the difference in expected proportion of data between X_train and X_test is too large."
        assert abs(abs(pipe.X_test.shape[0] / pipe.X_train.shape[0] - (pipe.n_test / pipe.n_train)) < margin_of_error), "the difference in expected proportion of data between X_test and X_train is too large."
        
    def atest_train(self) -> None:
        ...

    def atest_evaluate(self) -> None:
        ...

    def atest_save_model(self) -> None:
        ...