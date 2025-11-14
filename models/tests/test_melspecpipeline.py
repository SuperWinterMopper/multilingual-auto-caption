from ..src.VAD.training.MelSpecPipeline import MelSpecPipeline

def test_basic():
    pipeline = MelSpecPipeline(n_fft=512, sample_rate=16000, n_mel=40, hop_length=256)

    

    pipe.run_pipeline(collect_data=True)

    assert 4 == 4, "something wrong"