import sounddevice as sd
import numpy as np
from scipy.signal import resample
from voice_filter.vad_filter import is_speech

SAMPLE_RATE = 16000  # Required for webrtcvad
FRAME_DURATION_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)

def audio_callback(indata, outdata, frames, time, status):
    if status:
        print(f"Status: {status}")

    audio = indata[:, 0]  # mono
    is_speaking = is_speech(audio, SAMPLE_RATE)

    if is_speaking:
        outdata[:] = indata  # play it back if voice detected
    else:
        outdata[:] = np.zeros_like(indata)  # mute non-speech

def run_stream():
    with sd.Stream(
        samplerate=SAMPLE_RATE,
        blocksize=FRAME_SIZE,
        dtype='int16',
        channels=1,
        callback=audio_callback
    ):
        print("🎤 Listening... Speak into the mic.")
        input("Press Enter to stop...\n")