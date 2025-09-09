#!/usr/bin/env python3
"""
EchoShield Setup Script
Helps with initial configuration and setup
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
from pathlib import Path

def download_vosk_model():
    """Download a small Vosk model for wake word detection"""
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    model_name = "vosk-model-small-en-us-0.15"
    
    if os.path.exists(model_name):
        print(f"✅ Vosk model already exists: {model_name}")
        return model_name
    
    print(f"📥 Downloading Vosk model...")
    print(f"   URL: {model_url}")
    print("   This may take a few minutes...")
    
    try:
        urllib.request.urlretrieve(model_url, f"{model_name}.zip")
        print("✅ Download complete!")
        
        print("📦 Extracting model...")
        with zipfile.ZipFile(f"{model_name}.zip", 'r') as zip_ref:
            zip_ref.extractall()
        
        # Clean up zip file
        os.remove(f"{model_name}.zip")
        
        print(f"✅ Vosk model ready: {model_name}")
        return model_name
        
    except Exception as e:
        print(f"❌ Failed to download Vosk model: {e}")
        print("   You can download it manually from:")
        print("   https://alphacephei.com/vosk/models")
        return None

def create_audio_samples_dir():
    """Create audio samples directory"""
    audio_dir = Path("audio_samples")
    audio_dir.mkdir(exist_ok=True)
    print(f"✅ Created audio samples directory: {audio_dir}")

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python version {version.major}.{version.minor}.{version.micro} is not supported")
        print("   Please use Python 3.10 or higher")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    print("🛡️  EchoShield Setup")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed. Please install dependencies manually.")
        sys.exit(1)
    
    # Create directories
    create_audio_samples_dir()
    
    # Ask about Vosk model
    print("\n🧠 Vosk Model Setup")
    print("Vosk model is needed for wake word detection.")
    response = input("Download Vosk model now? (y/n): ").strip().lower()
    
    vosk_model = None
    if response in ['y', 'yes']:
        vosk_model = download_vosk_model()
    else:
        print("⚠️  Skipping Vosk model download")
        print("   You can download it later from: https://alphacephei.com/vosk/models")
    
    # Create voice sample script
    print("\n🎤 Voice Sample Setup")
    print("Creating voice sample recording script...")
    try:
        subprocess.run([sys.executable, "main.py", "--create-voice-sample"], check=True)
        print("✅ Voice sample script created: record_voice_sample.py")
    except subprocess.CalledProcessError:
        print("❌ Failed to create voice sample script")
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\nNext steps:")
    print("1. Record your voice sample:")
    print("   python record_voice_sample.py")
    print("\n2. Run EchoShield:")
    if vosk_model:
        print(f"   python main.py --vosk-model {vosk_model}")
    else:
        print("   python main.py")
    print("\n3. Or try the demo:")
    print("   python demo.py")
    print("\n4. Run installation test:")
    print("   python test_installation.py")

if __name__ == "__main__":
    main()
