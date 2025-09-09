#!/usr/bin/env python3
"""
Script to record your voice sample for EchoShield voice identification
"""

import sounddevice as sd
import numpy as np
import soundfile as sf
import os
from pathlib import Path

SAMPLE_RATE = 16000
DURATION = 5  # seconds

def record_voice_sample():
    print("🎤 EchoShield Voice Sample Recorder")
    print("=" * 40)
    print("This will record a 5-second sample of your voice.")
    print("Speak naturally - this will be used to identify your voice.")
    print("=" * 40)
    
    input("Press Enter when ready to start recording...")
    
    print("🔴 Recording... Speak now!")
    
    # Record audio
    audio = sd.rec(int(DURATION * SAMPLE_RATE), 
                   samplerate=SAMPLE_RATE, 
                   channels=1, 
                   dtype='int16')
    sd.wait()  # Wait until recording is finished
    
    print("✅ Recording complete!")
    
    # Save the audio
    output_path = "audio_samples/my_voice.wav"
    os.makedirs("audio_samples", exist_ok=True)
    
    sf.write(output_path, audio, SAMPLE_RATE)
    print(f"💾 Voice sample saved to: {output_path}")
    
    return output_path

if __name__ == "__main__":
    record_voice_sample()
