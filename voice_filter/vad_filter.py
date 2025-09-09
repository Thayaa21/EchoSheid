import webrtcvad
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import soundfile as sf
import os

vad = webrtcvad.Vad(3)  # Aggressiveness: 0–3
encoder = VoiceEncoder()

# Voice similarity threshold (0-1, higher = more strict)
VOICE_SIMILARITY_THRESHOLD = 0.7

def is_speech(audio, sample_rate):
    """Check if audio contains speech using VAD"""
    try:
        # Ensure audio is the right length for WebRTC VAD
        # WebRTC VAD requires specific frame lengths: 10, 20, or 30ms
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
        # If VAD fails, assume it's speech to be safe
        print(f"VAD error: {e}")
        return True

def load_user_voice_embedding(voice_sample_path=None):
    """Load or create user voice embedding for voice identification"""
    if voice_sample_path and os.path.exists(voice_sample_path):
        # Load existing voice sample
        wav = preprocess_wav(voice_sample_path)
        return encoder.embed_utterance(wav)
    else:
        # Return None if no voice sample available
        return None

def is_user_voice(audio, sample_rate, user_embedding):
    """Check if the audio matches the user's voice"""
    if user_embedding is None:
        return True  # If no user embedding, allow all speech through
    
    try:
        # Ensure audio is the right length for Resemblyzer
        if len(audio) < sample_rate * 0.5:  # Need at least 0.5 seconds
            return False
            
        # Preprocess audio for Resemblyzer
        wav = preprocess_wav(audio)
        
        # Get embedding for current audio
        current_embedding = encoder.embed_utterance(wav)
        
        # Calculate similarity
        similarity = np.dot(user_embedding, current_embedding)
        
        return similarity > VOICE_SIMILARITY_THRESHOLD
    except Exception as e:
        print(f"Error in voice identification: {e}")
        return True  # Default to allowing speech through on error