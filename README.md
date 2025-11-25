# EchoLingua - AI Pronunciation Coach

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)

**An intelligent voice-based pronunciation coaching system powered by advanced speech analysis and AI**

[Features](#features) • [Quick Start](#quick-start) • [How It Works](#how-it-works) • [Installation](#installation) • [Configuration](#configuration)

</div>

---

## 🎯 Overview

EchoLingua is a production-ready AI pronunciation coach that helps users improve their English pronunciation through real-time speech analysis and personalized feedback. The system combines cutting-edge speech recognition, phonetic analysis, and AI-powered coaching to provide professional-grade pronunciation training.

### Why EchoLingua?

- **🎙️ Voice-First Experience**: Entirely voice-driven interface with minimal console output
- **🔬 Advanced Analysis**: Phoneme-level accuracy detection and prosody evaluation
- **🤖 Intelligent Adaptation**: AI generates personalized practice sentences based on your errors
- **📊 Progress Tracking**: Comprehensive CSV logging of all practice sessions
- **🚀 Production Ready**: Clean, professional codebase with error handling and silent operations

---

## ✨ Features

### Core Capabilities

| Feature                          | Description                                                        |
| -------------------------------- | ------------------------------------------------------------------ |
| **Real-time Speech Recognition** | Powered by Deepgram's Nova-3 model for accurate transcription      |
| **Phoneme Analysis**             | Identifies specific sound errors using eSpeak phonetic engine      |
| **Prosody Evaluation**           | Analyzes pitch, rhythm, intonation, and speech patterns            |
| **AI Coaching**                  | GPT-powered feedback via Groq's LLaMA 3.3 70B model                |
| **Adaptive Learning**            | Dynamically generates practice sentences targeting your weak areas |
| **Session Metrics**              | Detailed CSV logs with timing, accuracy, and improvement tracking  |

### Technical Features

- **Streaming Audio Processing**: Low-latency speech-to-text and text-to-speech
- **Silence Detection**: Automatic recording stop when you finish speaking
- **Multiple Difficulty Levels**: Basic, Intermediate, Advanced, and Random modes
- **Error Pattern Recognition**: Tracks recurring pronunciation issues across sessions
- **Professional Voice Synthesis**: Natural-sounding speech output using Deepgram TTS

---

## 🧠 Understanding the Technology

### What are Phonemes?

**Phonemes** are the smallest units of sound in a language. For example:

- The word "cat" has 3 phonemes: /k/ /æ/ /t/
- The word "ship" has 3 phonemes: /ʃ/ /ɪ/ /p/

EchoLingua analyzes your pronunciation at the phoneme level to detect specific sound errors, such as:

- Confusing "th" (/θ/) with "f" or "s"
- Mixing up "l" and "r" sounds
- Incorrect vowel lengths (e.g., "ship" vs "sheep")

### What is Prosody?

**Prosody** refers to the rhythm, stress, and intonation patterns of speech. It includes:

- **Pitch Variation**: How your voice rises and falls (intonation)
- **Rhythm**: The timing and flow of speech
- **Stress**: Which syllables are emphasized
- **Pausing**: Natural breaks between words and phrases

Good prosody makes speech sound natural and engaging. EchoLingua analyzes these patterns to help you sound more like a native speaker.

### How the AI Coach Works

The system uses a multi-stage analysis pipeline:

```
Your Speech → Transcription → Phoneme Analysis → Prosody Analysis → AI Feedback
                    ↓               ↓                    ↓              ↓
              (Accuracy)    (Sound Errors)      (Rhythm/Pitch)   (Personalized)
```

The AI coach considers all these factors to:

1. Identify your specific pronunciation challenges
2. Explain what you're doing wrong and why
3. Provide actionable exercises to improve
4. Generate new practice sentences targeting your weak areas

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Microphone and speakers**
- **Deepgram API key** ([Get free credits](https://deepgram.com))
- **Groq API key** ([Get free access](https://console.groq.com))

### Installation

#### Windows

```bash
# Clone or download the repository
cd Echolingua

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install eSpeak NG for phoneme analysis
# Download from: https://github.com/espeak-ng/espeak-ng/releases
# Install espeak-ng-X64.msi
```

#### Linux

```bash
# Clone or download the repository
cd Echolingua

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install eSpeak
sudo apt-get update
sudo apt-get install espeak espeak-data libespeak-dev
```

#### macOS

```bash
# Clone or download the repository
cd Echolingua

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install eSpeak
brew install espeak
```

### Configuration

1. **Create environment file**:

   ```bash
   cp .env.example .env
   ```

2. **Add your API keys** to `.env`:

   ```
   DEEPGRAM_API_KEY=your_deepgram_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

---

## 📖 How to Use

### Basic Workflow

1. **Select Your Level**: Choose from Basic, Intermediate, Advanced, or Random
2. **Listen**: The AI coach speaks a practice sentence
3. **Speak**: Repeat the sentence after the beep
4. **Receive Feedback**: Get instant analysis and coaching
5. **Continue**: Press Enter for the next sentence or type 'exit' to quit

### Example Session

```
============================================================
🎓 ECHOLINGUA - AI PRONUNCIATION COACH
============================================================

Welcome! Select your practice level to begin.

📚 SELECT YOUR PRACTICE LEVEL:
============================================================
1. 🟢 Basic
2. 🟡 Intermediate
3. 🔴 Advanced
4. 🎲 Random
============================================================

Enter your choice (1-4): 2

✅ Starting intermediate level practice

Press Enter to begin...

============================================================
📝 The weather change is quite apparent today.

🎤 Recording...
✅ Recording complete

💬 Your 'th' sound is being pronounced as 'z'. Place your tongue
between your teeth and blow air gently for the correct 'th' sound.

▶️ Press Enter for next sentence (or type 'exit' to quit):
```

---

## ⚙️ Configuration

### Audio Settings

Edit `src/utils/config.py` to customize audio parameters:

```python
AUDIO_SAMPLE_RATE = 16000      # Recording quality
SILENCE_THRESHOLD = 500        # Sensitivity for silence detection
SILENCE_DURATION = 2.0         # Seconds of silence before stopping
MAX_RECORDING_DURATION = 30    # Maximum recording length
```

### Analysis Settings

```python
ENABLE_PHONEME_ANALYSIS = True  # Phoneme-level error detection
ENABLE_PROSODY_ANALYSIS = True  # Rhythm and intonation analysis
ENABLE_METRICS_LOGGING = True   # CSV session logging
```

### AI Models

```python
DEEPGRAM_STT_MODEL = "nova-3"              # Speech recognition
DEEPGRAM_TTS_MODEL = "aura-2-asteria-en"   # Voice synthesis
GROQ_MODEL = "llama-3.3-70b-versatile"     # AI coaching
```

---

## 📊 Session Metrics

Each practice session generates a detailed CSV log in the `logs/` directory with:

- Timestamp and interaction number
- Target sentence and your transcription
- Transcription accuracy percentage
- Phoneme error rate
- Fluency and prosody scores
- Pitch variation and pause frequency
- Pipeline timing breakdown (recording, transcription, analysis, feedback)
- Complete AI feedback

Use these logs to track your improvement over time!

---

## 🏗️ Project Structure

```
Echolingua/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── .env                            # API keys (create from .env.example)
├── data/
│   └── curriculum.csv              # Fallback sentence database
├── logs/                           # Session CSV logs
└── src/
    ├── core/
    │   ├── main.py                 # Application flow
    │   └── coach.py                # Main orchestration logic
    ├── services/
    │   ├── speech_to_text.py       # Deepgram STT integration
    │   ├── text_to_speech.py       # Deepgram TTS integration
    │   └── feedback_generator.py   # Groq AI coaching
    ├── analysis/
    │   ├── phoneme_analyzer.py     # eSpeak phoneme analysis
    │   └── prosody_analyzer.py     # Parselmouth prosody analysis
    └── utils/
        ├── config.py               # Configuration settings
        └── metrics_logger.py       # CSV logging
```

---

## 🔧 Troubleshooting

### Microphone Not Detected

**Solution**: Check system audio permissions and verify PyAudio installation:

```bash
python -c "import pyaudio; print('PyAudio OK')"
```

### Phoneme Analysis Not Working

**Solution**: Verify eSpeak installation:

```bash
# Windows
where espeak-ng

# Linux/Mac
which espeak
```

If not found, reinstall eSpeak and restart the application.

### API Errors

**Solution**:

- Verify API keys are correctly set in `.env`
- Check internet connection
- Ensure you have API credits remaining
- Test API keys:
  ```bash
  python -c "from src.utils import config; config.validate_config()"
  ```

### Audio Quality Issues

**Solution**: Adjust microphone settings:

- Speak 6-12 inches from the microphone
- Reduce background noise
- Adjust `SILENCE_THRESHOLD` in config.py if recording stops too early

---

## 🛠️ Technology Stack

| Component          | Technology         |
| ------------------ | ------------------ |
| Speech Recognition | Deepgram Nova-3    |
| Text-to-Speech     | Deepgram Aura-2    |
| AI Coaching        | Groq LLaMA 3.3 70B |
| Phoneme Analysis   | eSpeak NG          |
| Prosody Analysis   | Praat Parselmouth  |
| Audio Processing   | PyAudio            |
| Language           | Python 3.8+        |

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🤝 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

## 🎓 Educational Note

EchoLingua is designed as an educational tool and pronunciation practice system. While it provides valuable feedback and analysis, it's recommended to supplement with human coaching for advanced pronunciation refinement.

---

<div align="center">

**Made with ❤️ for language learners worldwide**

⭐ Star this repository if you find it helpful!

</div>
