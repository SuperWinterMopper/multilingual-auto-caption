from ..src.VAD.training.VADPipeline import VADPipeline

def test_basic():
    pipe = VADPipeline()
    pipe.run_pipeline(collect_data=True)

    assert 4 == 4, "something wrong"

def test_integration_up_to_split_data():
    pipe = VADPipeline()

    pipe.run_pipeline(collect_data=True, preprocess_data=True, split_data=True)

    print(pipe.X_train.shape)

def test_train():
    pipe = VADPipeline()

    pipe.run_pipeline(collect_data=True, preprocess_data=True, split_data=True, train=True)

    print(pipe.X_train.shape)