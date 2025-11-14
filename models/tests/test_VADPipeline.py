from ..src.VAD.training.VADPipeline import VADPipeline

def test_basic():
    pipe = VADPipeline()

    pipe.run_pipeline(collect_data=True)

    assert 4 == 4, "something wrong"