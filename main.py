#!/usr/bin/env python3
"""
EchoShield - Real-time Voice Isolation and Ambient Mode Trigger
A personal AI project for voice filtering and wake word detection
"""

import argparse
import os
import sys
import threading
import time
from pathlib import Path

from voice_filter.mic_stream import run_stream
from wake_word.detector import initialize_wake_word_detection, add_audio_to_detector

def create_voice_sample_script():
    """Create a script to record user's voice sample"""
    script_content = '''#!/usr/bin/env python3
"""
Script to record your voice sample for EchoShield voice identification
"""

import sounddevice as sd
import numpy as np
import soundfile as sf
from pathlib import Path

SAMPLE_RATE = 16000
DURATION = 5  # seconds

def record_voice_sample():
    print("🎤 EchoShield Voice Sample Recorder")
    print("=" * 40)
    print("This will record a 5-second sample of your voice.")
    print("Speak naturally - this will be used to identify your voice.")
    print("=" * 40)
    
    input("Press Enter when ready to start recording...")
    
    print("🔴 Recording... Speak now!")
    
    # Record audio
    audio = sd.rec(int(DURATION * SAMPLE_RATE), 
                   samplerate=SAMPLE_RATE, 
                   channels=1, 
                   dtype='int16')
    sd.wait()  # Wait until recording is finished
    
    print("✅ Recording complete!")
    
    # Save the audio
    output_path = "audio_samples/my_voice.wav"
    os.makedirs("audio_samples", exist_ok=True)
    
    sf.write(output_path, audio, SAMPLE_RATE)
    print(f"💾 Voice sample saved to: {output_path}")
    
    return output_path

if __name__ == "__main__":
    record_voice_sample()
'''
    
    with open("record_voice_sample.py", "w") as f:
        f.write(script_content)
    
    print("📝 Created 'record_voice_sample.py' - run this to record your voice sample")

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []
    
    try:
        import sounddevice
    except ImportError:
        missing_deps.append("sounddevice")
    
    try:
        import webrtcvad
    except ImportError:
        missing_deps.append("webrtcvad")
    
    try:
        import resemblyzer
    except ImportError:
        missing_deps.append("resemblyzer")
    
    try:
        import noisereduce
    except ImportError:
        missing_deps.append("noisereduce")
    
    try:
        import vosk
    except ImportError:
        missing_deps.append("vosk")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstall them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def main():
    parser = argparse.ArgumentParser(description="EchoShield - Real-time Voice Isolation and Ambient Mode")
    parser.add_argument("--voice-sample", type=str, help="Path to your voice sample file (.wav)")
    parser.add_argument("--vosk-model", type=str, help="Path to Vosk model directory")
    parser.add_argument("--wake-words", nargs="+", default=["thayaa", "excuse me", "hey echo"], 
                       help="Wake words to detect")
    parser.add_argument("--no-noise-reduction", action="store_true", 
                       help="Disable noise reduction")
    parser.add_argument("--no-wake-word", action="store_true", 
                       help="Disable wake word detection")
    parser.add_argument("--create-voice-sample", action="store_true", 
                       help="Create voice sample recording script")
    
    args = parser.parse_args()
    
    print("🛡️  EchoShield - Real-time Voice Isolation and Ambient Mode")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create voice sample script if requested
    if args.create_voice_sample:
        create_voice_sample_script()
        return
    
    # Check for voice sample
    voice_sample_path = args.voice_sample
    if not voice_sample_path:
        # Look for default voice sample
        default_paths = [
            "audio_samples/my_voice.wav",
            "audio_samples/voice_sample.wav",
            "my_voice.wav"
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                voice_sample_path = path
                break
    
    if voice_sample_path and not os.path.exists(voice_sample_path):
        print(f"❌ Voice sample file not found: {voice_sample_path}")
        print("   Run with --create-voice-sample to create a recording script")
        voice_sample_path = None
    
    # Initialize wake word detection if not disabled
    wake_word_detector = None
    if not args.no_wake_word:
        print("🔍 Initializing wake word detection...")
        wake_word_detector, ambient_trigger = initialize_wake_word_detection(
            model_path=args.vosk_model,
            wake_words=args.wake_words
        )
        
        if wake_word_detector and wake_word_detector.rec:
            wake_word_detector.start_listening()
        else:
            print("⚠️  Wake word detection disabled - no Vosk model available")
            print("   Download a model from: https://alphacephei.com/vosk/models")
    
    # Start the audio stream
    print("\n🎤 Starting EchoShield...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        run_stream(
            voice_sample_path=voice_sample_path,
            enable_noise_reduction=not args.no_noise_reduction
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down EchoShield...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if wake_word_detector:
            wake_word_detector.stop_listening()

if __name__ == "__main__":
    main()