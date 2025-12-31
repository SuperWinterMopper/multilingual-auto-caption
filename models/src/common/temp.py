from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
from pathlib import Path

audio_test = Path(__file__).parent / "welcome.mp3"

def test():
    print("Testing Silero VAD...")
    if audio_test.exists():
        print(f"Audio test file found at: {audio_test}")
        model = load_silero_vad()
        wav = read_audio(audio_test)
        speech_timestamps = get_speech_timestamps (
            wav,
            model,
            return_seconds=True,  # Return speech timestamps in seconds (default is samples)
        )
        print(speech_timestamps)
        print("Silero VAD test completed.")
    else:
        print(f"Audio test file not found at: {audio_test}")
        
def main(): 
    test()

if __name__ == '__main__':
    main()