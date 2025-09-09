#!/usr/bin/env python3
"""
Voice Upload System
Allows users to upload clean audio files for voice identification
"""

import os
import shutil
import soundfile as sf
import numpy as np
from pathlib import Path
import argparse

class VoiceUploader:
    def __init__(self):
        self.audio_samples_dir = Path("audio_samples")
        self.audio_samples_dir.mkdir(exist_ok=True)
        
        # Supported formats
        self.supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
        
    def upload_voice_file(self, file_path, target_name="my_voice.wav"):
        """Upload and convert voice file"""
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return False
            
            # Check file extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.supported_formats:
                print(f"❌ Unsupported format: {file_ext}")
                print(f"   Supported formats: {', '.join(self.supported_formats)}")
                return False
            
            print(f"📁 Processing file: {file_path}")
            
            # Load audio file
            audio_data, sample_rate = sf.read(file_path)
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
                print("🔄 Converted stereo to mono")
            
            # Resample to 16kHz if needed
            if sample_rate != 16000:
                from scipy.signal import resample
                num_samples = int(len(audio_data) * 16000 / sample_rate)
                audio_data = resample(audio_data, num_samples)
                sample_rate = 16000
                print(f"🔄 Resampled to 16kHz")
            
            # Normalize audio
            audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Save as WAV
            target_path = self.audio_samples_dir / target_name
            sf.write(target_path, audio_data, sample_rate)
            
            print(f"✅ Voice file uploaded: {target_path}")
            print(f"   Duration: {len(audio_data) / sample_rate:.1f} seconds")
            print(f"   Sample rate: {sample_rate} Hz")
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing file: {e}")
            return False
    
    def list_voice_files(self):
        """List available voice files"""
        print("📁 Available voice files:")
        
        voice_files = list(self.audio_samples_dir.glob("*.wav"))
        
        if not voice_files:
            print("   No voice files found")
            return []
        
        for i, file_path in enumerate(voice_files, 1):
            try:
                audio_data, sample_rate = sf.read(file_path)
                duration = len(audio_data) / sample_rate
                print(f"   {i}. {file_path.name} ({duration:.1f}s, {sample_rate}Hz)")
            except:
                print(f"   {i}. {file_path.name} (error reading)")
        
        return voice_files
    
    def validate_voice_file(self, file_path):
        """Validate voice file quality"""
        try:
            audio_data, sample_rate = sf.read(file_path)
            duration = len(audio_data) / sample_rate
            
            print(f"🔍 Validating voice file: {file_path}")
            print(f"   Duration: {duration:.1f} seconds")
            print(f"   Sample rate: {sample_rate} Hz")
            
            # Check duration
            if duration < 2.0:
                print("⚠️  Warning: File is very short (< 2 seconds)")
            elif duration > 30.0:
                print("⚠️  Warning: File is very long (> 30 seconds)")
            else:
                print("✅ Duration is good")
            
            # Check audio level
            max_level = np.max(np.abs(audio_data))
            if max_level < 0.1:
                print("⚠️  Warning: Audio level is very low")
            elif max_level > 0.95:
                print("⚠️  Warning: Audio level is very high (clipping possible)")
            else:
                print("✅ Audio level is good")
            
            # Check for silence
            silence_threshold = 0.01
            silent_samples = np.sum(np.abs(audio_data) < silence_threshold)
            silence_percentage = (silent_samples / len(audio_data)) * 100
            
            if silence_percentage > 50:
                print("⚠️  Warning: File contains a lot of silence")
            else:
                print("✅ Audio content is good")
            
            return True
            
        except Exception as e:
            print(f"❌ Error validating file: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Upload voice files for EchoShield")
    parser.add_argument("file", nargs="?", help="Path to voice file to upload")
    parser.add_argument("--name", default="my_voice.wav", help="Target filename")
    parser.add_argument("--list", action="store_true", help="List available voice files")
    parser.add_argument("--validate", help="Validate a voice file")
    
    args = parser.parse_args()
    
    uploader = VoiceUploader()
    
    if args.list:
        uploader.list_voice_files()
    elif args.validate:
        uploader.validate_voice_file(args.validate)
    elif args.file:
        uploader.upload_voice_file(args.file, args.name)
    else:
        print("🎤 EchoShield Voice Upload System")
        print("=" * 40)
        print("Upload clean audio files for voice identification")
        print("")
        print("Usage:")
        print("  python voice_upload.py <file_path>")
        print("  python voice_upload.py <file_path> --name custom_name.wav")
        print("  python voice_upload.py --list")
        print("  python voice_upload.py --validate <file_path>")
        print("")
        print("Supported formats: WAV, MP3, M4A, FLAC, OGG")
        print("Recommended: Clean 5-10 second recording of your voice")

if __name__ == "__main__":
    main()

