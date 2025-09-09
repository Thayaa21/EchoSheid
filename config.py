#!/usr/bin/env python3
"""
EchoShield Configuration
Centralized configuration for all EchoShield settings
"""

# Audio Settings
SAMPLE_RATE = 16000  # Required for WebRTC VAD
FRAME_DURATION_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)

# Voice Identification Settings
VOICE_SIMILARITY_THRESHOLD = 0.7  # 0-1, higher = more strict
AUDIO_BUFFER_SIZE = SAMPLE_RATE * 2  # 2 seconds for voice identification

# Wake Word Detection Settings
WAKE_WORD_BUFFER_SIZE = SAMPLE_RATE * 5  # 5 seconds for wake word detection
WAKE_WORD_PROCESSING_CHUNK = SAMPLE_RATE * 2  # 2 seconds processing chunks

# Default Wake Words
DEFAULT_WAKE_WORDS = ["thayaa", "excuse me", "hey echo", "wake up"]

# Audio Processing Settings
ENABLE_NOISE_REDUCTION = True
ENABLE_VOICE_IDENTIFICATION = True
ENABLE_WAKE_WORD_DETECTION = True

# File Paths
AUDIO_SAMPLES_DIR = "audio_samples"
DEFAULT_VOICE_SAMPLE = "audio_samples/my_voice.wav"
DEFAULT_VOSK_MODEL = "vosk-model-small-en-us-0.15"

# Ambient Mode Settings
AMBIENT_MODE_DURATION = 5.0  # seconds
CHIME_ENABLED = True

# Logging Settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
VERBOSE_OUTPUT = True

# Performance Settings
MAX_CPU_USAGE = 80  # Maximum CPU usage percentage
AUDIO_QUEUE_SIZE = 10  # Audio processing queue size

# Debug Settings
DEBUG_MODE = False
SAVE_AUDIO_SAMPLES = False  # Save processed audio for debugging
