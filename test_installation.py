#!/usr/bin/env python3
"""
EchoShield Installation Test Script
Run this to verify all dependencies are working correctly
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        if package_name:
            module = importlib.import_module(module_name, package_name)
        else:
            module = importlib.import_module(module_name)
        print(f"✅ {module_name}: OK")
        return True
    except ImportError as e:
        print(f"❌ {module_name}: FAILED - {e}")
        return False

def test_audio_devices():
    """Test audio device availability"""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        print(f"✅ Audio devices: {len(devices)} found")
        
        # Check for input devices
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        if input_devices:
            print(f"   📱 Input devices: {len(input_devices)} available")
        else:
            print("   ⚠️  No input devices found")
            
        # Check for output devices
        output_devices = [d for d in devices if d['max_output_channels'] > 0]
        if output_devices:
            print(f"   🔊 Output devices: {len(output_devices)} available")
        else:
            print("   ⚠️  No output devices found")
            
        return True
    except Exception as e:
        print(f"❌ Audio devices: FAILED - {e}")
        return False

def test_vosk_model():
    """Test if Vosk model is available"""
    try:
        import vosk
        import os
        
        # Look for common model paths
        model_paths = [
            "vosk-model-small-en-us-0.15",
            "vosk-model-en-us-0.22",
            "models/vosk-model-small-en-us-0.15",
            "models/vosk-model-en-us-0.22"
        ]
        
        model_found = False
        for path in model_paths:
            if os.path.exists(path):
                print(f"✅ Vosk model: Found at {path}")
                model_found = True
                break
        
        if not model_found:
            print("⚠️  Vosk model: Not found (wake word detection will be disabled)")
            print("   Download from: https://alphacephei.com/vosk/models")
        
        return model_found
    except Exception as e:
        print(f"❌ Vosk model: FAILED - {e}")
        return False

def main():
    print("🛡️  EchoShield Installation Test")
    print("=" * 50)
    
    # Test core dependencies
    dependencies = [
        "numpy",
        "sounddevice", 
        "webrtcvad",
        "resemblyzer",
        "noisereduce",
        "vosk",
        "scipy",
        "soundfile"
    ]
    
    print("\n📦 Testing Dependencies:")
    all_deps_ok = True
    for dep in dependencies:
        if not test_import(dep):
            all_deps_ok = False
    
    print("\n🎤 Testing Audio System:")
    audio_ok = test_audio_devices()
    
    print("\n🧠 Testing Vosk Model:")
    vosk_ok = test_vosk_model()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Dependencies: {'✅ PASS' if all_deps_ok else '❌ FAIL'}")
    print(f"   Audio System: {'✅ PASS' if audio_ok else '❌ FAIL'}")
    print(f"   Vosk Model: {'✅ PASS' if vosk_ok else '⚠️  OPTIONAL'}")
    
    if all_deps_ok and audio_ok:
        print("\n🎉 EchoShield is ready to use!")
        print("\nNext steps:")
        print("1. Try simple mode: python run_simple.py")
        print("2. Record your voice: python record_voice_sample.py")
        print("3. Run full system: python main.py")
        if not vosk_ok:
            print("4. (Optional) Download Vosk model for wake word detection")
    else:
        print("\n❌ Some issues found. Please fix them before running EchoShield.")
        if not all_deps_ok:
            print("   Run: pip install -r requirements.txt")
        if not audio_ok:
            print("   Check your audio device settings and permissions")

if __name__ == "__main__":
    main()

