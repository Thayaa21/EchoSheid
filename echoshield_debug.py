#!/usr/bin/env python3
"""
EchoShield Debug Mode
Shows voice similarity scores in real-time for debugging
"""

import sounddevice as sd
import numpy as np
import time
import os
import signal
import sys
from resemblyzer import VoiceEncoder, preprocess_wav
import webrtcvad

class EchoShieldDebug:
    def __init__(self):
        # Audio settings
        self.sample_rate = 16000
        self.frame_duration_ms = 30
        self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)
        
        # Voice isolation
        self.vad = webrtcvad.Vad(3)
        self.voice_encoder = VoiceEncoder()
        self.user_voice_embedding = None
        self.voice_similarity_threshold = 0.5
        
        # Audio buffer
        self.audio_buffer = []
        
    def load_user_voice(self, voice_file_path):
        """Load user voice sample"""
        try:
            if os.path.exists(voice_file_path):
                wav = preprocess_wav(voice_file_path)
                self.user_voice_embedding = self.voice_encoder.embed_utterance(wav)
                print(f"✅ Voice sample loaded: {voice_file_path}")
                return True
            else:
                print(f"❌ Voice file not found: {voice_file_path}")
                return False
        except Exception as e:
            print(f"❌ Error loading voice sample: {e}")
            return False
    
    def is_speech(self, audio):
        """Check if audio contains speech"""
        try:
            audio_energy = np.mean(np.abs(audio))
            if audio_energy < 0.005:
                return False
            
            frame_length_ms = len(audio) * 1000 / self.sample_rate
            if frame_length_ms > 30:
                samples_30ms = int(self.sample_rate * 0.03)
                audio = audio[-samples_30ms:]
            
            int16_audio = (audio * 32767).astype(np.int16).tobytes()
            if len(int16_audio) < 320:
                return False
            
            return self.vad.is_speech(int16_audio, self.sample_rate)
        except:
            return False
    
    def is_user_voice(self, audio):
        """Check if audio matches user's voice with debug info"""
        if self.user_voice_embedding is None:
            return True
        
        try:
            if len(audio) < self.sample_rate * 0.3:
                return False
            
            wav = preprocess_wav(audio)
            current_embedding = self.voice_encoder.embed_utterance(wav)
            similarity = np.dot(self.user_voice_embedding, current_embedding)
            
            return similarity > self.voice_similarity_threshold, similarity
        except Exception as e:
            return True, 0.0
    
    def audio_callback(self, indata, outdata, frames, time, status):
        """Debug audio callback"""
        if status and 'overflow' not in str(status).lower():
            print(f"Status: {status}")
        
        audio = indata[:, 0]  # mono
        
        # Add to buffer
        self.audio_buffer.extend(audio.tolist())
        
        # Process when buffer is full (2 seconds)
        if len(self.audio_buffer) >= self.sample_rate * 2:
            audio_chunk = np.array(self.audio_buffer[-self.sample_rate * 2:])
            
            is_speaking = self.is_speech(audio_chunk)
            
            if is_speaking:
                is_user, similarity = self.is_user_voice(audio_chunk)
                
                if is_user:
                    outdata[:] = indata  # Pass through
                    print(f"✅ YOUR VOICE: {similarity:.3f} (threshold: {self.voice_similarity_threshold:.3f})")
                else:
                    outdata[:] = np.zeros_like(indata)  # Block
                    print(f"❌ OTHER VOICE: {similarity:.3f} (threshold: {self.voice_similarity_threshold:.3f})")
            else:
                outdata[:] = np.zeros_like(indata)  # Block silence
                print("🔇 SILENCE")
        else:
            outdata[:] = np.zeros_like(indata)
    
    def run_debug(self, voice_file_path):
        """Run debug mode"""
        print("🐛 EchoShield Debug Mode")
        print("=" * 50)
        
        # Load voice sample
        if not self.load_user_voice(voice_file_path):
            return False
        
        print(f"\n🎯 Current threshold: {self.voice_similarity_threshold}")
        print("📊 You'll see real-time similarity scores:")
        print("  ✅ YOUR VOICE: X.XXX (similarity score)")
        print("  ❌ OTHER VOICE: X.XXX (similarity score)")
        print("  🔇 SILENCE")
        print("\nPress Ctrl+C to stop")
        print("=" * 50)
        
        try:
            with sd.Stream(
                samplerate=self.sample_rate,
                blocksize=self.frame_size,
                dtype='float32',
                channels=1,
                callback=self.audio_callback
            ):
                print("🎤 Debug mode active...")
                
                while True:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Debug mode stopped")
        except Exception as e:
            print(f"❌ Error: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Received interrupt signal")
    sys.exit(0)

def main():
    """Main function"""
    signal.signal(signal.SIGINT, signal_handler)
    
    voice_file = "audio_samples/my_voice.wav"
    
    if not os.path.exists(voice_file):
        print(f"❌ Voice file not found: {voice_file}")
        print("   Run: python record_voice_sample.py")
        print("   Or: python voice_upload.py your_voice_file.wav")
        return
    
    debug = EchoShieldDebug()
    debug.run_debug(voice_file)

if __name__ == "__main__":
    main()
