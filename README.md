# 🛡️ EchoShield

**Real-time Voice Isolation and Ambient Mode Trigger System**

EchoShield is a clean, focused AI project that provides real-time voice filtering and ambient mode triggering for Galaxy Buds 3 Pro. It isolates your voice while suppressing all other sounds, and automatically switches to ambient mode when wake words are detected.

## 🎯 What EchoShield Does

**The Core Problem**: When wearing noise-cancelling headphones, you can't hear your surroundings or other people talking to you. EchoShield solves this by:

1. **🎤 Voice Isolation**: Only lets YOUR voice pass through to your headphones
2. **🔇 Noise Filtering**: Blocks out background noise and other people's voices  
3. **🌊 Ambient Mode**: When someone says your wake word (like "Thayaa"), it automatically switches Galaxy Buds to ambient mode for 10 seconds

**Real-world Example**: You're working with Galaxy Buds 3 Pro, someone says "Thayaa, excuse me" → EchoShield detects this, switches to ambient mode, and you can hear them clearly.

## 🚀 Getting Started (TL;DR)

**Quick Test (Basic Voice Filtering):**
```bash
python run_simple.py
```

**Full EchoShield Core (Recommended):**
```bash
# Option 1: Record your voice sample live
python record_voice_sample.py

# Option 2: Upload a clean audio file (better quality)
python voice_upload.py your_voice_file.wav

# Then run EchoShield Core
python echoshield_core.py
```

**Test Normal Recording (Compare with EchoShield):**
```bash
python test_normal_recording.py
```

**That's it!** EchoShield Core will isolate your voice and trigger ambient mode on wake words.

## ✨ Features

### 🎤 Real-Time Voice Isolation
- **Voice Activity Detection**: Uses WebRTC VAD to detect speech
- **Voice Identification**: Uses Resemblyzer to identify and allow only your voice
- **Noise Reduction**: Applies noise reduction using noisereduce library
- **Real-time Processing**: Low-latency audio processing with sounddevice

### 🌊 Ambient Mode Trigger
- **Wake Word Detection**: Uses Vosk for real-time speech recognition
- **Customizable Wake Words**: Set your own wake words like "Thayaa", "Excuse me"
- **Visual & Audio Feedback**: Chime sounds and visual notifications
- **Parallel Processing**: Voice filtering and wake word detection run simultaneously

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd EchoShield

# Install dependencies
pip install -r requirements.txt
```

### 2. Test Installation

```bash
# Run the installation test to make sure everything works
python test_installation.py
```

### 3. Start Simple (Recommended First)

```bash
# Try the simple version first - just basic speech detection
python run_simple.py
```

This will:
- ✅ Detect when you're speaking
- ✅ Pass your voice through to headphones
- ✅ Block silence and background noise
- ❌ No voice identification (allows all speech)
- ❌ No wake word detection

### 4. Record Your Voice Sample (For Voice Identification)

```bash
# Create voice sample recording script
python main.py --create-voice-sample

# Record your voice (5 seconds)
python record_voice_sample.py
```

### 5. Run Full EchoShield

```bash
# Basic usage (voice filtering only)
python main.py

# With voice sample for voice identification
python main.py --voice-sample audio_samples/my_voice.wav

# With wake word detection (requires Vosk model)
python main.py --vosk-model vosk-model-small-en-us-0.15

# Custom wake words
python main.py --wake-words "thayaa" "excuse me" "hey echo"
```

### 6. Download Vosk Model (For Wake Word Detection)

```bash
# Download a small English model (50MB)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

## 📋 Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --voice-sample PATH        Path to your voice sample file (.wav)
  --vosk-model PATH          Path to Vosk model directory
  --wake-words WORDS         Wake words to detect (default: thayaa, excuse me, hey echo)
  --no-noise-reduction       Disable noise reduction
  --no-wake-word             Disable wake word detection
  --create-voice-sample      Create voice sample recording script
```

## 🏗️ Architecture

```
EchoShield/
├── main.py                  # Main application entry point
├── voice_filter/
│   ├── mic_stream.py        # Audio stream handling
│   └── vad_filter.py        # Voice activity detection & identification
├── wake_word/
│   └── detector.py          # Wake word detection & ambient mode
├── utils/
│   └── audio_tools.py       # Audio utility functions
├── audio_samples/           # Voice samples directory
└── requirements.txt         # Python dependencies
```

## 🔧 How It Works

### Audio Processing Pipeline
1. **🎤 Input**: Captures microphone audio in real-time
2. **🔍 Speech Detection**: Uses WebRTC VAD to detect when someone is speaking
3. **🧠 Voice Identification**: Uses Resemblyzer to check if it's YOUR voice
4. **🔇 Noise Reduction**: Cleans up background noise (optional)
5. **📢 Output**: Sends filtered audio to your headphones

### Wake Word Detection
1. **📝 Speech Recognition**: Uses Vosk to convert speech to text
2. **🎯 Pattern Matching**: Looks for your wake words ("Thayaa", "Excuse me")
3. **🌊 Ambient Trigger**: When detected, temporarily allows all audio through
4. **⏰ Auto-Reset**: Returns to voice filtering after 5 seconds

### Why We Built Different Versions

**`run_simple.py`** - Lightweight version:
- ✅ Basic speech detection only
- ✅ No CPU-intensive processing
- ✅ Perfect for testing and low-power devices

**`main.py`** - Full version:
- ✅ Voice identification (only YOUR voice passes through)
- ✅ Noise reduction
- ✅ Wake word detection (with Vosk model)
- ⚠️ Requires more CPU power

### Performance Optimizations We Made

1. **Increased Frame Size**: 30ms → 60ms (reduces CPU load)
2. **Simplified Processing**: Disabled heavy noise reduction by default
3. **Reduced Wake Word Frequency**: Process every 3 seconds instead of 2
4. **Filtered Status Messages**: Only show important errors, not overflow warnings

## ⚙️ Configuration

### Voice Identification
- **Similarity Threshold**: 0.7 (adjustable in `vad_filter.py`)
- **Buffer Size**: 2 seconds for voice identification
- **Sample Rate**: 16kHz (required for WebRTC VAD)

### Wake Word Detection
- **Buffer Size**: 5 seconds for speech recognition
- **Processing**: 2-second chunks for real-time performance
- **Model**: Vosk small English model (50MB)

## 🐛 Troubleshooting

### Common Issues We've Fixed

1. **"Input overflow" errors** ✅ FIXED
   - **Problem**: Audio processing was too intensive
   - **Solution**: Optimized audio pipeline and simplified processing
   - **Use**: `python run_simple.py` for lightweight version

2. **WebRTC VAD errors** ✅ FIXED
   - **Problem**: "Error while processing frame" from WebRTC VAD
   - **Solution**: Fixed frame size compatibility and added error handling
   - **Use**: All versions now work with proper frame sizes

3. **High CPU usage** ✅ FIXED
   - **Problem**: Too much real-time processing
   - **Solution**: Optimized audio pipeline and reduced processing frequency
   - **Use**: `python main.py --no-noise-reduction` to disable heavy processing

4. **Wake word detection not working**
   - **Problem**: No Vosk model or processing overload
   - **Solution**: Download Vosk model and use optimized settings
   - **Use**: `python main.py --vosk-model vosk-model-small-en-us-0.15`

5. **Voice identification not working**
   - **Problem**: No voice sample or poor quality
   - **Solution**: Record clear 5+ second voice sample
   - **Use**: `python record_voice_sample.py` then `python main.py --voice-sample audio_samples/my_voice.wav`

### Performance Issues

**If you experience problems:**

1. **Start with simple mode**: `python run_simple.py`
2. **Disable heavy features**: `python main.py --no-noise-reduction --no-wake-word`
3. **Use larger frames**: The system automatically uses 60ms frames for stability

### Dependencies Issues

```bash
# If you get import errors
pip install --upgrade -r requirements.txt

# For macOS audio issues
brew install portaudio

# Test everything works
python test_installation.py
```

### What Each Mode Does

| Mode | Speech Detection | Voice ID | Wake Words | Galaxy Buds | Recording |
|------|------------------|----------|------------|-------------|-----------|
| `run_simple.py` | ✅ | ❌ | ❌ | ❌ | ❌ |
| `main.py` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `echoshield_core.py` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `test_normal_recording.py` | ❌ | ❌ | ❌ | ❌ | ✅ |
| `voice_upload.py` | ❌ | ❌ | ❌ | ❌ | ❌ |

### Voice Sample Options

**Option 1: Live Recording**
```bash
python record_voice_sample.py
```

**Option 2: Upload Clean Audio File (Recommended)**
```bash
# Upload any audio file (WAV, MP3, M4A, FLAC, OGG)
python voice_upload.py your_voice_file.wav

# List available voice files
python voice_upload.py --list

# Validate a voice file
python voice_upload.py --validate your_voice_file.wav
```

**Benefits of Upload:**
- ✅ Higher quality (no background noise)
- ✅ Multiple formats supported
- ✅ Automatic conversion to 16kHz
- ✅ Quality validation
- ✅ Better voice identification accuracy

## 🎧 Galaxy Buds 3 Pro Integration

EchoShield Core integrates with your Galaxy Buds 3 Pro to automatically switch between modes:

### **How It Works:**
1. **Normal Mode**: Noise cancellation active, only your voice passes through
2. **Wake Word Detected**: Automatically switches to ambient mode
3. **Ambient Mode**: You can hear surroundings clearly (like Galaxy Buds' siren detection)
4. **Auto-Return**: Returns to noise cancellation after 10 seconds

### **Wake Words:**
- "Thayaa"
- "Excuse me" 
- "Hey echo"

### **Real-time Recording:**
- Automatically starts recording when wake word detected
- Saves audio recordings for testing and analysis
- Timestamped files in `recordings/` directory
- Compare with `test_normal_recording.py` to see the difference

## 🔮 Future Enhancements

- [ ] Whisper integration for better accuracy
- [ ] Custom chime sounds
- [ ] GUI interface
- [ ] Multiple voice profiles
- [ ] Real-time audio visualization
- [ ] Mobile app integration

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ for personal AI projects**