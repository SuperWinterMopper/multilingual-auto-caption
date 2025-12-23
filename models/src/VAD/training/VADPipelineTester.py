from ...common.PipelineStructure import PipelineTester
from .VADPipelineAbstractClass import VADPipelineAbstractClass


class VADPipelineTester(PipelineTester):

    def btest_collect_data(self, pipeline=None) -> None:
        """Ensures the data directory exists and contains expected files after data collection"""
        assert pipeline is not None
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

    def btest_preprocess_data(self, pipeline=None) -> None:
        assert pipeline is not None

        train_root = pipeline.data_path / "train"
        valid_root = pipeline.data_path / "dev"
        test_root = pipeline.data_path / "eval"

        assert train_root.exists(), train_root
        assert valid_root.exists(), valid_root
        assert test_root.exists(), test_root

        assert (train_root / "session_0").exists()
        assert (valid_root / "session_0").exists()
        assert (test_root / "session_0").exists()
        assert (train_root / f"session_{pipeline.n_train - 1}").exists()
        assert (valid_root / f"session_{pipeline.n_valid - 1}").exists()
        assert (test_root / f"session_{pipeline.n_test - 1}").exists()

    def btest_split_data(self, pipeline=None) -> None:
        assert pipeline is not None
        assert pipeline.X_train is not None and pipeline.y_train is not None, "Training data not set"
        assert pipeline.X_valid is not None and pipeline.y_valid is not None, "Validation data not set"
        assert pipeline.X_test is not None and pipeline.y_test is not None, "Test data not set"

    def btest_train(self, pipeline=None) -> None:
        assert pipeline is not None
        assert pipeline.model is not None, "Model is not initialized."
        assert pipeline.trainer is not None, "Trainer is not initialized."

        assert hasattr(pipeline, "preprocessed_files"), "Pipeline missing preprocessed_files list."
        assert pipeline.preprocessed_files is not None, "Pipeline preprocessed_files is None."
        assert len(pipeline.preprocessed_files) > 0, "Pipeline preprocessed_files is empty."

        missing = [str(p) for p in pipeline.preprocessed_files if not p.exists()]
        assert not missing, f"Missing preprocessed .pt files: {missing}"
        
    def btest_evaluate(self, pipeline) -> None:
        assert pipeline.preprocessed_files[2].exists(), f"VAD_test_ds.pt file not found at {pipeline.preprocessed_files[2]}"

    def btest_save_model(self, pipeline=None) -> None:
        ...

    def atest_collect_data(self, pipeline=None) -> None:
        assert pipeline is not None
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

    def atest_preprocess_data(self, pipeline=None) -> None:
        assert pipeline is not None
        assert pipeline.X_train is not None and pipeline.y_train is not None, "Training data not set"
        assert pipeline.X_valid is not None and pipeline.y_valid is not None, "Validation data not set"
        assert pipeline.X_test is not None and pipeline.y_test is not None, "Test data not set"

        assert pipeline.X_test.shape[0] == pipeline.y_test.shape[0], "Test data size mismatch"
        assert pipeline.X_train.shape[0] == pipeline.y_train.shape[0], "Train data size mismatch"
        assert pipeline.X_valid.shape[0] == pipeline.y_valid.shape[0], "Validation data size mismatch"

        for t in [pipeline.X_test, pipeline.X_train, pipeline.X_valid]:
            assert t.shape[1] == t.shape[2] == pipeline.num_mel_bands, "Spectrogram tensors are not the right size of num_mel_bands x num_mel_bands"

    def atest_split_data(self, pipeline=None) -> None:
        assert pipeline is not None
        margin_of_error = .05 # 5 percent error ok

        assert abs(abs(pipeline.X_train.shape[0] / pipeline.X_valid.shape[0] - (pipeline.n_train / pipeline.n_valid)) < margin_of_error), "the difference in expected proportion of data between X_train and X_valid is too large."
        assert abs(abs(pipeline.X_train.shape[0] / pipeline.X_test.shape[0] - (pipeline.n_train / pipeline.n_test)) < margin_of_error), "the difference in expected proportion of data between X_train and X_test is too large."
        assert abs(abs(pipeline.X_test.shape[0] / pipeline.X_train.shape[0] - (pipeline.n_test / pipeline.n_train)) < margin_of_error), "the difference in expected proportion of data between X_test and X_train is too large."
        
    def atest_train(self, pipeline) -> None:
        assert pipeline.trainer is not None, "Trainer is not initialized."
        assert pipeline.logger.vad_accuracy_history_plot_path.exists(), "Accuracy history plot was not saved: " + str(pipeline.logger.vad_accuracy_history_plot_path)

    def atest_evaluate(self, pipeline=None) -> None:
        pass

    def atest_save_model(self, pipeline=None) -> None:
        ...