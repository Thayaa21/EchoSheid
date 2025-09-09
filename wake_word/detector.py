import json
import os
import vosk
import numpy as np
import threading
import time
from collections import deque

class WakeWordDetector:
    def __init__(self, model_path=None, wake_words=None, sample_rate=16000):
        """
        Initialize wake word detector using Vosk
        
        Args:
            model_path: Path to Vosk model directory
            wake_words: List of wake words to detect (default: ["thayaa", "excuse me"])
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
        self.wake_words = wake_words or ["thayaa", "excuse me", "hey echo", "wake up"]
        self.model = None
        self.rec = None
        self.is_listening = False
        self.audio_buffer = deque(maxlen=sample_rate * 5)  # 5 second buffer
        
        # Callback function for when wake word is detected
        self.wake_word_callback = None
        
        # Load Vosk model
        self.load_model(model_path)
    
    def load_model(self, model_path=None):
        """Load Vosk model for speech recognition"""
        if model_path and os.path.exists(model_path):
            try:
                self.model = vosk.Model(model_path)
                self.rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
                print(f"✅ Vosk model loaded from: {model_path}")
            except Exception as e:
                print(f"❌ Failed to load Vosk model: {e}")
                self.model = None
                self.rec = None
        else:
            print("⚠️  No Vosk model provided - wake word detection disabled")
            print("   Download a model from: https://alphacephei.com/vosk/models")
    
    def set_wake_word_callback(self, callback):
        """Set callback function to be called when wake word is detected"""
        self.wake_word_callback = callback
    
    def add_audio_data(self, audio_data):
        """Add audio data to the buffer for processing"""
        if self.rec is None:
            return
        
        # Convert to bytes if needed
        if audio_data.dtype != np.int16:
            audio_data = (audio_data * 32767).astype(np.int16)
        
        # Add to buffer
        self.audio_buffer.extend(audio_data.tolist())
        
        # Process audio in chunks (reduced frequency to lower CPU load)
        if len(self.audio_buffer) >= self.sample_rate * 3:  # Process 3-second chunks
            self._process_audio_chunk()
    
    def _process_audio_chunk(self):
        """Process audio chunk for wake word detection"""
        if self.rec is None or not self.is_listening:
            return
        
        try:
            # Get audio chunk
            audio_chunk = np.array(list(self.audio_buffer))
            audio_bytes = audio_chunk.tobytes()
            
            # Process with Vosk
            if self.rec.AcceptWaveform(audio_bytes):
                result = json.loads(self.rec.Result())
                text = result.get('text', '').lower().strip()
                
                if text:
                    print(f"🎤 Detected: '{text}'")
                    
                    # Check for wake words
                    for wake_word in self.wake_words:
                        if wake_word.lower() in text:
                            print(f"🚨 WAKE WORD DETECTED: '{wake_word}'")
                            if self.wake_word_callback:
                                self.wake_word_callback(wake_word, text)
                            break
        except Exception as e:
            print(f"Error processing audio: {e}")
    
    def start_listening(self):
        """Start wake word detection"""
        if self.rec is None:
            print("❌ Cannot start listening - no model loaded")
            return False
        
        self.is_listening = True
        print(f"👂 Wake word detection started. Listening for: {', '.join(self.wake_words)}")
        return True
    
    def stop_listening(self):
        """Stop wake word detection"""
        self.is_listening = False
        print("🔇 Wake word detection stopped")
    
    def reset(self):
        """Reset the recognizer"""
        if self.rec:
            self.rec.Reset()

class AmbientModeTrigger:
    """Handles ambient mode triggering and feedback"""
    
    def __init__(self):
        self.is_ambient_mode = False
        self.chime_sound = None
        self.load_chime()
    
    def load_chime(self):
        """Load chime sound for ambient mode feedback"""
        try:
            # You can replace this with a custom chime file
            # For now, we'll use a simple beep
            self.chime_sound = None  # Placeholder for actual chime file
            print("🔔 Chime sound loaded")
        except Exception as e:
            print(f"⚠️  Could not load chime sound: {e}")
    
    def trigger_ambient_mode(self, wake_word, full_text):
        """Trigger ambient mode when wake word is detected"""
        self.is_ambient_mode = True
        print("🌊 AMBIENT MODE ACTIVATED!")
        print(f"   Wake word: '{wake_word}'")
        print(f"   Full text: '{full_text}'")
        
        # Play chime
        self.play_chime()
        
        # Show visual feedback
        self.show_visual_feedback()
        
        # Reset after some time
        threading.Timer(5.0, self.reset_ambient_mode).start()
    
    def play_chime(self):
        """Play chime sound"""
        try:
            # Simple beep for now - you can replace with actual chime
            print("🔔 *CHIME*")
            # TODO: Add actual audio playback here
        except Exception as e:
            print(f"Error playing chime: {e}")
    
    def show_visual_feedback(self):
        """Show visual feedback for ambient mode"""
        print("=" * 50)
        print("🌊 AMBIENT MODE ACTIVE")
        print("   Your surroundings are now audible")
        print("=" * 50)
    
    def reset_ambient_mode(self):
        """Reset ambient mode"""
        self.is_ambient_mode = False
        print("🔇 Ambient mode deactivated")

# Global instances
wake_word_detector = None
ambient_trigger = None

def initialize_wake_word_detection(model_path=None, wake_words=None):
    """Initialize wake word detection system"""
    global wake_word_detector, ambient_trigger
    
    wake_word_detector = WakeWordDetector(model_path, wake_words)
    ambient_trigger = AmbientModeTrigger()
    
    # Set up callback
    wake_word_detector.set_wake_word_callback(ambient_trigger.trigger_ambient_mode)
    
    return wake_word_detector, ambient_trigger

def add_audio_to_detector(audio_data):
    """Add audio data to wake word detector"""
    global wake_word_detector
    if wake_word_detector:
        wake_word_detector.add_audio_data(audio_data)
