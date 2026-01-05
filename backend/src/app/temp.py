from faster_whisper import WhisperModel 
import torch


def load_asr_model() -> WhisperModel:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if torch.cuda.is_available() else "float32"

    # load model on GPU if available, else cpu
    model = WhisperModel("distil-whisper/distil-large-v3.5-ct2", device=device, compute_type=compute_type)

    return model

def main():
    print('Loading ASR model...')
    model = load_asr_model()
    print('Model loaded. Transcribing sample file...')
    segments, info = model.transcribe("korean.mp4", beam_size=1, language="ko")
    
    print(segments)
    print(info)

if __name__ == '__main__':
    main()