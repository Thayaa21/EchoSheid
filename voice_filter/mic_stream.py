import sounddevice as sd
import numpy as np
from scipy.signal import resample
import noisereduce as nr
import threading
import time
from collections import deque
from voice_filter.vad_filter import is_speech, is_user_voice, load_user_voice_embedding
from wake_word.detector import add_audio_to_detector

SAMPLE_RATE = 16000  # Required for webrtcvad
FRAME_DURATION_MS = 30  # WebRTC VAD compatible frame size
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)

# Audio buffer for voice identification (needs longer samples)
AUDIO_BUFFER_SIZE = SAMPLE_RATE * 2  # 2 seconds buffer
audio_buffer = deque(maxlen=AUDIO_BUFFER_SIZE)

# Voice identification settings
user_voice_embedding = None
voice_identification_enabled = False

def audio_callback(indata, outdata, frames, time, status):
    global audio_buffer, user_voice_embedding, voice_identification_enabled
    
    # Only print status errors, not overflow warnings
    if status and 'overflow' not in str(status).lower():
        print(f"Status: {status}")

    audio = indata[:, 0]  # mono
    
    # Add to buffer for voice identification
    audio_buffer.extend(audio)
    
    # Send audio to wake word detector (runs in parallel)
    add_audio_to_detector(audio)
    
    # Check if there's speech
    is_speaking = is_speech(audio, SAMPLE_RATE)
    
    if is_speaking:
        # Simplified processing to reduce CPU load
        audio_processed = audio  # Skip noise reduction for now to reduce load
        
        # Check if it's the user's voice (if voice identification is enabled)
        if voice_identification_enabled and user_voice_embedding is not None:
            # Use the full buffer for better voice identification
            buffer_array = np.array(audio_buffer)
            is_user = is_user_voice(buffer_array, SAMPLE_RATE, user_voice_embedding)
            
            if is_user:
                outdata[:] = audio_processed.reshape(-1, 1)  # Play back user's voice
            else:
                outdata[:] = np.zeros_like(indata)  # Mute other voices
        else:
            # If voice identification is disabled, play back all speech
            outdata[:] = audio_processed.reshape(-1, 1)
    else:
        outdata[:] = np.zeros_like(indata)  # Mute non-speech

def setup_voice_identification(voice_sample_path=None):
    """Setup voice identification with user's voice sample"""
    global user_voice_embedding, voice_identification_enabled
    
    if voice_sample_path:
        print(f"Loading voice sample from: {voice_sample_path}")
        user_voice_embedding = load_user_voice_embedding(voice_sample_path)
        if user_voice_embedding is not None:
            voice_identification_enabled = True
            print("✅ Voice identification enabled")
        else:
            print("❌ Failed to load voice sample")
    else:
        print("ℹ️  No voice sample provided - all speech will be allowed through")
        voice_identification_enabled = False

def run_stream(voice_sample_path=None, enable_noise_reduction=True):
    """Run the audio stream with voice filtering"""
    global voice_identification_enabled
    
    print("🎤 EchoShield - Real-time Voice Isolation")
    print("=" * 50)
    
    # Setup voice identification
    setup_voice_identification(voice_sample_path)
    
    if enable_noise_reduction:
        print("🔇 Noise reduction: ENABLED")
    else:
        print("🔇 Noise reduction: DISABLED")
    
    print(f"🎯 Voice identification: {'ENABLED' if voice_identification_enabled else 'DISABLED'}")
    print("=" * 50)
    
    try:
        with sd.Stream(
            samplerate=SAMPLE_RATE,
            blocksize=FRAME_SIZE,
            dtype='int16',
            channels=1,
            callback=audio_callback
        ):
            print("🎤 Listening... Speak into the mic.")
            print("Press Ctrl+C to stop...")
            
            while True:
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping EchoShield...")
    except Exception as e:
        print(f"❌ Error: {e}")