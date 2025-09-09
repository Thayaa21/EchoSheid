#!/usr/bin/env python3
"""
Simple Audio Test - Just test if microphone and speakers work
"""

import sounddevice as sd
import numpy as np
import time

SAMPLE_RATE = 16000
FRAME_SIZE = 480  # 30ms at 16kHz

def test_callback(indata, outdata, frames, time, status):
    """Simple passthrough - just copy input to output"""
    if status:
        print(f"Status: {status}")
    
    # Just pass audio through (no processing)
    outdata[:] = indata
    print("🎤 Audio flowing...", end='\r')

def main():
    print("🔊 EchoShield Audio Test")
    print("=" * 30)
    print("This just tests if your microphone and speakers work.")
    print("You should hear yourself speaking.")
    print("Press Ctrl+C to stop.")
    print("=" * 30)
    
    try:
        with sd.Stream(
            samplerate=SAMPLE_RATE,
            blocksize=FRAME_SIZE,
            dtype='float32',
            channels=1,
            callback=test_callback
        ):
            print("🎤 Speak into your microphone...")
            print("You should hear yourself in your headphones/speakers.")
            
            while True:
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n🛑 Test stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
