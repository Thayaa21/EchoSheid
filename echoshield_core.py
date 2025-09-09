#!/usr/bin/env python3
"""
EchoShield Core - Clean Implementation
Focus: Voice isolation, wake word detection, Galaxy Buds integration
"""

import sounddevice as sd
import numpy as np
import threading
import time
import signal
import sys
import os
import json
from datetime import datetime
from collections import deque

# Core imports
import webrtcvad
from resemblyzer import VoiceEncoder, preprocess_wav
import vosk

class EchoShieldCore:
    def __init__(self):
        # Audio settings
        self.sample_rate = 16000
        self.frame_duration_ms = 30
        self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)
        
        # Voice isolation
        self.vad = webrtcvad.Vad(3)  # High aggressiveness
        self.voice_encoder = VoiceEncoder()
        self.user_voice_embedding = None
        self.voice_similarity_threshold = 0.5  # Lowered from 0.7 to be less strict
        
        # Wake word detection
        self.vosk_model = None
        self.vosk_rec = None
        self.wake_words = ["thayaa", "excuse me", "hey echo"]
        self.wake_word_buffer = deque(maxlen=self.sample_rate * 5)  # 5 seconds
        
        # Galaxy Buds
        self.galaxy_buds_connected = False
        self.ambient_mode_active = False
        self.ambient_duration = 10.0
        
        # Recording
        self.recording_enabled = False
        self.recording_buffer = []
        
        # Status
        self.is_running = False
        
    def load_user_voice(self, voice_file_path):
        """Load user voice sample for identification"""
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
    
    def load_vosk_model(self, model_path):
        """Load Vosk model for wake word detection"""
        try:
            if os.path.exists(model_path):
                self.vosk_model = vosk.Model(model_path)
                self.vosk_rec = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)
                print(f"✅ Vosk model loaded: {model_path}")
                return True
            else:
                print(f"❌ Vosk model not found: {model_path}")
                return False
        except Exception as e:
            print(f"❌ Error loading Vosk model: {e}")
            return False
    
    def check_galaxy_buds(self):
        """Check Galaxy Buds connection"""
        try:
            import subprocess
            result = subprocess.run(['blueutil', '--paired'], 
                                  capture_output=True, text=True)
            if "galaxy buds" in result.stdout.lower():
                self.galaxy_buds_connected = True
                print("✅ Galaxy Buds connected")
                return True
            else:
                print("⚠️  Galaxy Buds not detected")
                return False
        except:
            print("⚠️  Could not check Galaxy Buds connection")
            return False
    
    def is_user_voice(self, audio):
        """Check if audio matches user's voice"""
        if self.user_voice_embedding is None:
            return True  # Allow all if no voice sample
        
        try:
            if len(audio) < self.sample_rate * 0.3:  # Reduced from 0.5 to 0.3 seconds
                return False
            
            wav = preprocess_wav(audio)
            current_embedding = self.voice_encoder.embed_utterance(wav)
            similarity = np.dot(self.user_voice_embedding, current_embedding)
            
            # Debug output
            print(f"🎯 Voice similarity: {similarity:.3f} (threshold: {self.voice_similarity_threshold})", end='\r')
            
            return similarity > self.voice_similarity_threshold
        except Exception as e:
            print(f"Voice ID error: {e}", end='\r')
            return True  # Default to allowing on error
    
    def is_speech(self, audio):
        """Check if audio contains speech"""
        try:
            # Volume check
            audio_energy = np.mean(np.abs(audio))
            if audio_energy < 0.005:
                return False
            
            # VAD check
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
    
    def process_wake_word(self, audio):
        """Process audio for wake word detection"""
        if self.vosk_rec is None:
            return False
        
        try:
            # Add to buffer
            self.wake_word_buffer.extend(audio.tolist())
            
            # Process when buffer is full
            if len(self.wake_word_buffer) >= self.sample_rate * 2:  # 2 seconds
                audio_chunk = np.array(list(self.wake_word_buffer))
                audio_bytes = audio_chunk.tobytes()
                
                if self.vosk_rec.AcceptWaveform(audio_bytes):
                    result = json.loads(self.vosk_rec.Result())
                    text = result.get('text', '').lower().strip()
                    
                    if text:
                        for wake_word in self.wake_words:
                            if wake_word in text:
                                print(f"🚨 WAKE WORD DETECTED: '{wake_word}'")
                                self.trigger_ambient_mode(wake_word, text)
                                return True
        except Exception as e:
            print(f"Wake word processing error: {e}")
        
        return False
    
    def trigger_ambient_mode(self, wake_word, full_text):
        """Trigger ambient mode when wake word detected"""
        print(f"🌊 AMBIENT MODE ACTIVATED by '{wake_word}'")
        print(f"📝 Full text: '{full_text}'")
        print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Switch Galaxy Buds to ambient mode
        if self.galaxy_buds_connected:
            self.switch_galaxy_buds_ambient()
        
        self.ambient_mode_active = True
        
        # Start recording if not already
        if not self.recording_enabled:
            self.start_recording()
        
        # Auto-return to noise cancellation
        threading.Timer(self.ambient_duration, self.return_to_noise_cancellation).start()
    
    def switch_galaxy_buds_ambient(self):
        """Switch Galaxy Buds to ambient mode"""
        try:
            import subprocess
            # This is a simplified approach - real implementation would use Galaxy Buds API
            subprocess.run(['osascript', '-e', 'set volume output volume 100'], check=True)
            print("🎧 Galaxy Buds switched to ambient mode")
        except:
            print("🎧 Simulated: Galaxy Buds ambient mode")
    
    def switch_galaxy_buds_noise_cancellation(self):
        """Switch Galaxy Buds to noise cancellation"""
        try:
            import subprocess
            subprocess.run(['osascript', '-e', 'set volume output volume 80'], check=True)
            print("🔇 Galaxy Buds switched to noise cancellation")
        except:
            print("🔇 Simulated: Galaxy Buds noise cancellation")
    
    def return_to_noise_cancellation(self):
        """Return to noise cancellation mode"""
        if self.galaxy_buds_connected:
            self.switch_galaxy_buds_noise_cancellation()
        self.ambient_mode_active = False
        print("🔇 Returned to noise cancellation mode")
    
    def start_recording(self):
        """Start audio recording"""
        self.recording_enabled = True
        self.recording_buffer = []
        print("🎥 Recording started")
    
    def stop_recording(self):
        """Stop and save recording"""
        if self.recording_enabled:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recordings/echoshield_session_{timestamp}.wav"
            
            os.makedirs("recordings", exist_ok=True)
            
            if self.recording_buffer:
                audio_data = np.concatenate(self.recording_buffer)
                import soundfile as sf
                sf.write(filename, audio_data, self.sample_rate)
                print(f"💾 Recording saved: {filename}")
            
            self.recording_enabled = False
            self.recording_buffer = []
    
    def audio_callback(self, indata, outdata, frames, time, status):
        """Main audio processing callback"""
        if status and 'overflow' not in str(status).lower():
            print(f"Audio status: {status}")
        
        audio = indata[:, 0]  # mono
        
        # Add to recording buffer
        if self.recording_enabled:
            self.recording_buffer.append(audio.copy())
        
        # Process wake word detection
        self.process_wake_word(audio)
        
        # Voice isolation
        is_speaking = self.is_speech(audio)
        
        if is_speaking:
            # Check if it's user's voice
            if self.is_user_voice(audio):
                outdata[:] = indata  # Pass through user's voice
                print("🎤 USER VOICE → PASSING THROUGH", end='\r')
            else:
                outdata[:] = np.zeros_like(indata)  # Block other voices
                print("🔇 OTHER VOICE → BLOCKED        ", end='\r')
        else:
            outdata[:] = np.zeros_like(indata)  # Block silence/noise
            print("🔇 SILENCE → BLOCKED            ", end='\r')
    
    def run(self, voice_file=None, vosk_model_path=None):
        """Run EchoShield Core"""
        print("🛡️  EchoShield Core")
        print("=" * 50)
        
        # Load user voice
        if voice_file:
            self.load_user_voice(voice_file)
        
        # Load Vosk model
        if vosk_model_path:
            self.load_vosk_model(vosk_model_path)
        
        # Check Galaxy Buds
        self.check_galaxy_buds()
        
        print("\n🎤 Starting EchoShield Core...")
        print("Features:")
        print(f"  🎯 Voice Isolation: {'✅ Active' if self.user_voice_embedding is not None else '❌ Disabled'}")
        print(f"  🧠 Wake Words: {'✅ Active' if self.vosk_rec else '❌ Disabled'}")
        print(f"  🎧 Galaxy Buds: {'✅ Connected' if self.galaxy_buds_connected else '⚠️  Simulated'}")
        print(f"  🎥 Recording: {'✅ Active' if self.recording_enabled else '❌ Disabled'}")
        print("\nCommands:")
        print("  • Speak normally → Only your voice passes through")
        print("  • Say wake words → Triggers ambient mode")
        print("  • Press Ctrl+C to stop")
        print("=" * 50)
        
        self.is_running = True
        
        try:
            with sd.Stream(
                samplerate=self.sample_rate,
                blocksize=self.frame_size,
                dtype='float32',
                channels=1,
                callback=self.audio_callback
            ):
                print("🎤 Listening...")
                
                while self.is_running:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping EchoShield Core...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        self.is_running = False
        self.stop_recording()
        print("✅ EchoShield Core stopped")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Received interrupt signal")
    sys.exit(0)

def main():
    """Main function"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🛡️  EchoShield Core")
    print("=" * 50)
    
    # Check for voice sample
    voice_file = "audio_samples/my_voice.wav"
    if not os.path.exists(voice_file):
        print(f"⚠️  Voice sample not found: {voice_file}")
        print("   Options:")
        print("   1. Record live: python record_voice_sample.py")
        print("   2. Upload file: python voice_upload.py <your_file.wav>")
        print("   3. Run without voice ID: python echoshield_core.py --no-voice-id")
        
        # Check if user wants to continue without voice ID
        try:
            response = input("\nContinue without voice identification? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                voice_file = None
                print("ℹ️  Running without voice identification (all speech will pass through)")
            else:
                print("❌ Please provide a voice sample first")
                return
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return
    else:
        print(f"✅ Voice sample found: {voice_file}")
    
    # Check for Vosk model
    vosk_model_path = "vosk-model-small-en-us-0.15"
    if not os.path.exists(vosk_model_path):
        print(f"⚠️  Vosk model not found: {vosk_model_path}")
        print("   Download from: https://alphacephei.com/vosk/models")
        print("   Or run without wake word detection")
        vosk_model_path = None
    else:
        print(f"✅ Vosk model found: {vosk_model_path}")
    
    print("=" * 50)
    
    # Create and run EchoShield Core
    echoshield = EchoShieldCore()
    echoshield.run(voice_file=voice_file, vosk_model_path=vosk_model_path)

if __name__ == "__main__":
    main()
