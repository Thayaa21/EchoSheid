#!/usr/bin/env python3
"""
Normal Recording Test - Records audio without EchoShield processing
Use this to compare with EchoShield output
"""

import sounddevice as sd
import numpy as np
import time
import os
from datetime import datetime
import soundfile as sf

class NormalRecorder:
    def __init__(self):
        self.sample_rate = 16000
        self.frame_size = 480  # 30ms at 16kHz
        self.is_recording = False
        self.audio_buffer = []
        
    def start_recording(self, filename_prefix="normal_recording"):
        """Start normal recording"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"recordings/{filename_prefix}_{timestamp}.wav"
        
        os.makedirs("recordings", exist_ok=True)
        
        self.is_recording = True
        self.audio_buffer = []
        
        print(f"🎤 Normal recording started: {self.filename}")
        return True
    
    def stop_recording(self):
        """Stop and save recording"""
        if not self.is_recording:
            return False
        
        self.is_recording = False
        
        if self.audio_buffer:
            audio_data = np.concatenate(self.audio_buffer)
            sf.write(self.filename, audio_data, self.sample_rate)
            print(f"💾 Normal recording saved: {self.filename}")
        
        return True
    
    def audio_callback(self, indata, outdata, frames, time, status):
        """Simple passthrough callback"""
        if status:
            print(f"Status: {status}")
        
        # Just pass audio through (no processing)
        outdata[:] = indata
        
        # Record audio
        if self.is_recording:
            self.audio_buffer.append(indata.copy())
        
        print("🎤 Normal recording...", end='\r')
    
    def run(self, duration=10):
        """Run normal recording for specified duration"""
        print("🎤 Normal Recording Test")
        print("=" * 40)
        print("This records audio WITHOUT any EchoShield processing")
        print("Use this to compare with EchoShield output")
        print("=" * 40)
        
        # Start recording
        self.start_recording("normal_test")
        
        try:
            with sd.Stream(
                samplerate=self.sample_rate,
                blocksize=self.frame_size,
                dtype='float32',
                channels=1,
                callback=self.audio_callback
            ):
                print(f"🎤 Recording for {duration} seconds...")
                print("Speak normally - this will record everything")
                print("Press Ctrl+C to stop early")
                
                time.sleep(duration)
                
        except KeyboardInterrupt:
            print("\n🛑 Recording stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.stop_recording()
            print("✅ Normal recording test complete")

def main():
    """Main function"""
    recorder = NormalRecorder()
    
    print("Choose recording duration:")
    print("1. 10 seconds")
    print("2. 30 seconds")
    print("3. 60 seconds")
    print("4. Custom duration")
    
    try:
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            duration = 10
        elif choice == "2":
            duration = 30
        elif choice == "3":
            duration = 60
        elif choice == "4":
            duration = int(input("Enter duration in seconds: "))
        else:
            duration = 10
        
        recorder.run(duration)
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
