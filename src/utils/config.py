import os
from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_CHUNK_SIZE = 8000
AUDIO_FORMAT = 'wav'

ENABLE_STREAMING = True
STREAMING_TTS = True
STREAMING_STT = True

MAX_RECORDING_DURATION = 30
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 2.0
MIN_SPEECH_DELAY = 5.0

DEEPGRAM_TTS_MODEL = "aura-2-asteria-en"
DEEPGRAM_TTS_ENCODING = "linear16"
DEEPGRAM_TTS_CONTAINER = "wav"
DEEPGRAM_TTS_SAMPLE_RATE = 48000

DEEPGRAM_STT_MODEL = "nova-3"
DEEPGRAM_STT_LANGUAGE = "en-US"

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_TEMPERATURE = 0.7
GROQ_MAX_TOKENS = 2048

CURRICULUM_FILE = "data/curriculum.csv"

PRACTICE_CATEGORIES = {
    'basic': 'beginner',
    'intermediate': 'intermediate',
    'advanced': 'advanced',
    'random': None
}

ENABLE_PHONEME_ANALYSIS = True
ENABLE_PROSODY_ANALYSIS = True
ENABLE_METRICS_LOGGING = True
METRICS_LOG_DIR = "logs"

# Espeak Configuration (for phoneme analysis)
# Set this to the full path of your espeak installation if auto-detection fails
# Examples:
#   Windows: r'C:\Program Files\eSpeak NG\libespeak-ng.dll'
#   Linux: '/usr/bin/espeak' or '/usr/bin/espeak-ng'
#   Mac: '/usr/local/bin/espeak' or '/opt/homebrew/bin/espeak'
ESPEAK_LIBRARY_PATH = None  # Set to None for auto-detection

FEEDBACK_PROMPT_TEMPLATE = """You are a professional English pronunciation coach with expertise in phonetics and speech therapy. 
Your role is to identify pronunciation errors and provide constructive, actionable feedback.

**Target Sentence:** "{target_sentence}"

**Analysis Data:**
- Transcription Match: {similarity_score}%
- Phoneme Error Rate: {phoneme_error_rate}%
- Common Phoneme Issues: {phoneme_errors}
- Prosody Analysis: {prosody_summary}
- Pitch Variation: {pitch_variation}%

**Error History (Recent Patterns):**
{error_history}

**Your Task:**
As a professional coach, provide feedback that:
1. **Identifies specific pronunciation errors** - Point to which sounds/words need work (do NOT mention the transcription text)
2. **Explains the phonetic issue** - What's happening with tongue, lips, airflow, or stress in simple and concise terms
3. **Provides practice techniques** - Concrete exercises or tips
4. **Includes practice words** - 2-3 related words to practice the same sound pattern

**Tone:** Encouraging yet professional. Focus on ONE main issue per feedback.
**Length:** 1-2 sentences maximum. Be concise and actionable.

Remember: The user doesn't see the transcription - coach them on what you hear they're struggling with based on the analysis."""

SENTENCE_GENERATION_TEMPLATE = """You are an English pronunciation curriculum designer.

**Current Difficulty Level:** {difficulty_level}

**Previous Coaching Feedback:**
{previous_feedback}

**Student's Recent Error Patterns:**
{error_patterns}

**Problematic Phonemes/Sounds:**
{problem_phonemes}

**Performance Context:**
- Transcription Accuracy: {transcription_accuracy}%
- Phoneme Accuracy: {phoneme_accuracy}%
- Needs work on: {focus_areas}

**Task:** Generate ONE practice sentence that:
1. Directly addresses the issues mentioned in the coaching feedback
2. Targets the student's specific pronunciation weaknesses
3. Contains words with the problematic phonemes: {problem_phonemes}
4. Matches the difficulty level ({difficulty_level})
5. Is natural and conversational (10-15 words)
6. Gradually increases difficulty to challenge the student

**Previous sentences practiced:**
{recent_sentences}

Generate a NEW sentence (different from previous ones) that helps the student improve on their weak areas.

Return ONLY the sentence, nothing else."""

GROQ_SENTENCE_MODEL = "llama-3.3-70b-versatile"
GROQ_SENTENCE_TEMPERATURE = 0.8
GROQ_SENTENCE_MAX_TOKENS = 2048

INITIAL_SENTENCE_TEMPLATE = """You are an English pronunciation curriculum designer creating the FIRST practice sentence for a student.

**Student's Level:** {difficulty_level}

**Task:** Generate ONE practice sentence that:
1. Is appropriate for a {difficulty_level} level student
2. Serves as a good warm-up and baseline assessment
3. Contains common pronunciation challenges for {difficulty_level} level:
   - Beginner: Basic sounds like 'th', 'r', 'l', simple vowels
   - Intermediate: Consonant clusters, vowel distinctions, word stress
   - Advanced: Complex clusters, weak forms, connected speech, intonation
4. Is natural and conversational (10-15 words)
5. Is engaging and interesting to practice

**Focus Areas by Level:**
- Beginner: Clear individual sounds, simple words
- Intermediate: Word combinations, rhythm patterns
- Advanced: Natural speech flow, stress timing, intonation patterns

Generate a NEW, interesting sentence that will serve as an excellent first practice sentence.

Return ONLY the sentence, nothing else."""

def validate_config():
    if not DEEPGRAM_API_KEY:
        raise ValueError("DEEPGRAM_API_KEY is not set. Please check your .env file.")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set. Please check your .env file.")
    return True
