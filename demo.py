#!/usr/bin/env python3
"""
EchoShield Demo Script
Demonstrates the key features of EchoShield
"""

import time
import sys
from voice_filter.mic_stream import run_stream
from wake_word.detector import initialize_wake_word_detection

def demo_voice_filtering():
    """Demo voice filtering without wake word detection"""
    print("🎤 EchoShield Voice Filtering Demo")
    print("=" * 50)
    print("This demo will:")
    print("1. Filter out silence and noise")
    print("2. Apply voice activity detection")
    print("3. Play back only speech (if voice sample provided)")
    print("=" * 50)
    
    try:
        run_stream(enable_noise_reduction=True)
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped")

def demo_with_wake_words():
    """Demo with wake word detection (if Vosk model available)"""
    print("🌊 EchoShield Full Demo (with Wake Words)")
    print("=" * 50)
    print("This demo includes:")
    print("1. Voice filtering")
    print("2. Wake word detection")
    print("3. Ambient mode triggering")
    print("=" * 50)
    
    # Initialize wake word detection
    wake_detector, ambient_trigger = initialize_wake_word_detection(
        wake_words=["thayaa", "excuse me", "hey echo"]
    )
    
    if wake_detector and wake_detector.rec:
        wake_detector.start_listening()
        print("✅ Wake word detection enabled")
    else:
        print("⚠️  Wake word detection disabled (no Vosk model)")
    
    try:
        run_stream(enable_noise_reduction=True)
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped")
    finally:
        if wake_detector:
            wake_detector.stop_listening()

def main():
    print("🛡️  EchoShield Demo")
    print("=" * 30)
    print("Choose a demo:")
    print("1. Voice Filtering Only")
    print("2. Full Demo (with Wake Words)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                demo_voice_filtering()
                break
            elif choice == "2":
                demo_with_wake_words()
                break
            elif choice == "3":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
