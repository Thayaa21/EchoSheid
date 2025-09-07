import webrtcvad
import numpy as np

vad = webrtcvad.Vad(3)  # Aggressiveness: 0–3

def is_speech(audio, sample_rate):
    # Convert float32 [-1, 1] to int16
    int16_audio = (audio * 32767).astype(np.int16).tobytes()
    return vad.is_speech(int16_audio, sample_rate)