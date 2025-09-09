#!/usr/bin/env python3
"""
Voice Calibration Tool
Helps you find the right voice similarity threshold
"""

import sounddevice as sd
import numpy as np
import time
import os
from resemblyzer import VoiceEncoder, preprocess_wav

class VoiceCalibration:
    def __init__(self):
        self.sample_rate = 16000
        self.frame_size = 480  # 30ms
        self.voice_encoder = VoiceEncoder()
        self.user_voice_embedding = None
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
    
    def audio_callback(self, indata, outdata, frames, time, status):
        """Audio callback for calibration"""
        if status:
            print(f"Status: {status}")
        
        audio = indata[:, 0]  # mono
        
        # Add to buffer
        self.audio_buffer.extend(audio.tolist())
        
        # Process when buffer is full (2 seconds)
        if len(self.audio_buffer) >= self.sample_rate * 2:
            audio_chunk = np.array(self.audio_buffer[-self.sample_rate * 2:])
            
            if self.user_voice_embedding is not None:
                try:
                    wav = preprocess_wav(audio_chunk)
                    current_embedding = self.voice_encoder.embed_utterance(wav)
                    similarity = np.dot(self.user_voice_embedding, current_embedding)
                    
                    print(f"🎯 Voice similarity: {similarity:.3f}", end='\r')
                    
                    if similarity > 0.6:
                        print(f"✅ YOUR VOICE detected (similarity: {similarity:.3f})")
                    elif similarity > 0.4:
                        print(f"⚠️  UNCERTAIN (similarity: {similarity:.3f})")
                    else:
                        print(f"❌ OTHER VOICE detected (similarity: {similarity:.3f})")
                        
                except Exception as e:
                    print(f"Error: {e}")
        
        # Pass audio through
        outdata[:] = indata
    
    def run_calibration(self, voice_file_path):
        """Run voice calibration"""
        print("🎤 Voice Calibration Tool")
        print("=" * 50)
        
        # Load voice sample
        if not self.load_user_voice(voice_file_path):
            return False
        
        print("\n🎯 Calibration Instructions:")
        print("1. Speak normally (this should show 'YOUR VOICE')")
        print("2. Have someone else speak (this should show 'OTHER VOICE')")
        print("3. Play music/videos (this should show 'OTHER VOICE')")
        print("4. Stay quiet (should show low similarity)")
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
                print("🎤 Listening for calibration...")
                
                while True:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Calibration stopped")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def suggest_threshold(self, voice_file_path):
        """Suggest optimal threshold based on voice sample"""
        print("🧠 Analyzing voice sample for optimal threshold...")
        
        if not self.load_user_voice(voice_file_path):
            return
        
        try:
            # Load the voice sample multiple times to test consistency
            wav = preprocess_wav(voice_file_path)
            
            # Split into chunks and test similarity
            chunk_size = self.sample_rate * 1  # 1 second chunks
            similarities = []
            
            for i in range(0, len(wav) - chunk_size, chunk_size // 2):
                chunk = wav[i:i + chunk_size]
                if len(chunk) >= chunk_size:
                    chunk_embedding = self.voice_encoder.embed_utterance(chunk)
                    similarity = np.dot(self.user_voice_embedding, chunk_embedding)
                    similarities.append(similarity)
            
            if similarities:
                avg_similarity = np.mean(similarities)
                min_similarity = np.min(similarities)
                max_similarity = np.max(similarities)
                
                print(f"📊 Voice Analysis Results:")
                print(f"   Average similarity: {avg_similarity:.3f}")
                print(f"   Min similarity: {min_similarity:.3f}")
                print(f"   Max similarity: {max_similarity:.3f}")
                
                # Suggest threshold
                suggested_threshold = min_similarity - 0.1
                suggested_threshold = max(0.3, min(0.7, suggested_threshold))
                
                print(f"\n💡 Suggested threshold: {suggested_threshold:.3f}")
                print(f"   This should allow your voice while blocking others")
                
                return suggested_threshold
                
        except Exception as e:
            print(f"❌ Error analyzing voice: {e}")
            return None

def main():
    """Main function"""
    voice_file = "audio_samples/my_voice.wav"
    
    if not os.path.exists(voice_file):
        print(f"❌ Voice file not found: {voice_file}")
        print("   Run: python record_voice_sample.py")
        print("   Or: python voice_upload.py your_voice_file.wav")
        return
    
    calibrator = VoiceCalibration()
    
    print("Choose calibration mode:")
    print("1. Live calibration (speak and test)")
    print("2. Analyze voice sample (suggest threshold)")
    
    try:
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == "1":
            calibrator.run_calibration(voice_file)
        elif choice == "2":
            calibrator.suggest_threshold(voice_file)
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
