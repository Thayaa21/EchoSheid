#!/usr/bin/env python3
"""
EchoShield Simple Runner
A lightweight version with minimal processing for testing
"""

import sounddevice as sd
import numpy as np
import webrtcvad
import time

# Simple configuration
SAMPLE_RATE = 16000
FRAME_DURATION_MS = 30  # WebRTC VAD compatible frame size
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)

# Initialize VAD with higher aggressiveness
vad = webrtcvad.Vad(3)  # High aggressiveness (0-3, 3 is most strict)

def is_speech(audio, sample_rate):
    """Simple speech detection with volume threshold"""
    try:
        # Check audio volume first (simple energy-based detection)
        audio_energy = np.mean(np.abs(audio))
        if audio_energy < 0.01:  # Very quiet, probably not speech
            return False
        
        # Ensure audio is the right length for WebRTC VAD
        frame_length_ms = len(audio) * 1000 / sample_rate
        
        # If frame is too long, take the last 30ms
        if frame_length_ms > 30:
            samples_30ms = int(sample_rate * 0.03)  # 30ms in samples
            audio = audio[-samples_30ms:]
        
        # Convert float32 [-1, 1] to int16
        int16_audio = (audio * 32767).astype(np.int16).tobytes()
        
        # Check if we have enough data
        if len(int16_audio) < 320:  # Minimum 20ms at 16kHz
            return False
            
        return vad.is_speech(int16_audio, sample_rate)
    except Exception as e:
        print(f"VAD error: {e}")
        return False

def simple_audio_callback(indata, outdata, frames, time, status):
    """Simplified audio callback"""
    if status and 'overflow' not in str(status).lower():
        print(f"Status: {status}")
    
    audio = indata[:, 0]  # mono
    
    # Simple speech detection
    is_speaking = is_speech(audio, SAMPLE_RATE)
    
    if is_speaking:
        outdata[:] = indata  # Pass through speech
        print("🎤 SPEECH DETECTED", end='\r')  # Show feedback
    else:
        outdata[:] = np.zeros_like(indata)  # Mute silence
        print("🔇 Listening...", end='\r')  # Show feedback

def main():
    print("🛡️  EchoShield Simple Mode")
    print("=" * 40)
    print("This is a lightweight version for testing.")
    print("It only does basic speech detection.")
    print("Press Ctrl+C to stop.")
    print("=" * 40)
    
    try:
        with sd.Stream(
            samplerate=SAMPLE_RATE,
            blocksize=FRAME_SIZE,
            dtype='int16',
            channels=1,
            callback=simple_audio_callback
        ):
            print("🎤 Listening... Speak into the mic.")
            print("You should see 'SPEECH DETECTED' when you talk.")
            print("Press Ctrl+C to stop.")
            
            while True:
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping EchoShield...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
