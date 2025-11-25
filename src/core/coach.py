import csv
import random
import time
import os
from enum import Enum
from src.services.speech_to_text import SpeechToText
from src.services.text_to_speech import TextToSpeech
from src.services.feedback_generator import FeedbackGenerator
from src.analysis.phoneme_analyzer import PhonemeAnalyzer
from src.analysis.prosody_analyzer import ProsodyAnalyzer
from src.utils.metrics_logger import MetricsLogger
from src.utils import config

class CoachState(Enum):
    PROVIDING_TASK = "providing_task"
    LISTENING = "listening"
    EVALUATING = "evaluating"
    FINISHED = "finished"

class PronunciationCoach:
    def __init__(self, category='random'):
        self.state = CoachState.PROVIDING_TASK
        self.category = category
        self.difficulty = config.PRACTICE_CATEGORIES.get(category, None)
        
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.feedback_gen = FeedbackGenerator()
        
        self.phoneme_analyzer = PhonemeAnalyzer() if config.ENABLE_PHONEME_ANALYSIS else None
        self.prosody_analyzer = ProsodyAnalyzer() if config.ENABLE_PROSODY_ANALYSIS else None
        
        self.metrics_logger = MetricsLogger(config.METRICS_LOG_DIR) if config.ENABLE_METRICS_LOGGING else None
        if self.metrics_logger:
            self.metrics_logger.set_category(category)
        
        self.curriculum = []
        self.current_sentence = None
        self.current_sentence_text = None
        self.practiced_sentences = []
        self.error_history = []
        self.use_llm_sentences = True
        self.last_feedback = None
        self.last_metrics = None
        self.next_sentence = None
        self.is_first_sentence = True
        
        self.session_stats = {
            "sentences_practiced": 0,
            "perfect_matches": 0,
            "total_similarity": 0,
            "start_time": time.time(),
            "attempts": []
        }
        
        self.load_curriculum()
    
    def load_curriculum(self):
        try:
            with open(config.CURRICULUM_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.curriculum = list(reader)
        except Exception as e:
            pass
            self.curriculum = [
                {
                    "difficulty": "beginner",
                    "phonetic_focus": "th_sound",
                    "sentence": "The three thin thieves thought through their plan."
                }
            ]
    
    def get_next_sentence(self):
        if self.is_first_sentence:
            self.is_first_sentence = False
            new_sentence = self.feedback_gen.generate_initial_sentence(
                difficulty_level=self.category if self.category else "intermediate"
            )
            
            if not new_sentence:
                return self._get_sentence_from_db()
            
            return new_sentence
        
        new_sentence = self.feedback_gen.generate_new_sentence(
            difficulty_level=self.difficulty if self.difficulty else "intermediate",
            error_patterns=self.error_history,
            recent_sentences=self.practiced_sentences,
            previous_feedback=self.last_feedback,
            last_metrics=self.last_metrics
        )
        
        if not new_sentence:
            return self._get_sentence_from_db()
        
        return new_sentence
    
    def _get_sentence_from_db(self):
        if self.difficulty:
            filtered = [s for s in self.curriculum if s['difficulty'] == self.difficulty]
            sentence_data = random.choice(filtered) if filtered else random.choice(self.curriculum)
        else:
            sentence_data = random.choice(self.curriculum)
        
        self.current_sentence = sentence_data
        return sentence_data['sentence']
    
    def provide_task(self):
        self.state = CoachState.PROVIDING_TASK
        print("\n" + "="*60)
        
        if self.next_sentence:
            self.current_sentence_text = self.next_sentence
            self.next_sentence = None
        else:
            self.current_sentence_text = self.get_next_sentence()
        
        print(f"📝 {self.current_sentence_text}")
        
        task_prompt = f"Repeat this sentence after the beep: {self.current_sentence_text}"
        self.tts.speak(task_prompt, streaming=config.STREAMING_TTS)
        
        self.practiced_sentences.append(self.current_sentence_text)
        
        time.sleep(1)
        return self.current_sentence_text
    
    def listen(self):
        self.state = CoachState.LISTENING
        
        result = self.stt.record_and_transcribe(
            duration=config.MAX_RECORDING_DURATION,
            streaming=config.STREAMING_STT
        )
        
        return result
    
    def evaluate(self, target_sentence, transcription_result, audio_file="temp_recording.wav", recording_time=0):
        self.state = CoachState.EVALUATING
        
        transcription_time = 0
        analysis_start = time.time()
        
        if isinstance(transcription_result, dict):
            user_transcription = transcription_result.get('transcript', '')
            word_data = transcription_result.get('words', [])
            overall_confidence = transcription_result.get('confidence', 0.0)
            transcription_time = transcription_result.get('processing_time', 0)
        else:
            user_transcription = transcription_result
            word_data = []
            overall_confidence = 1.0
        
        basic_metrics = self.feedback_gen.get_metrics(target_sentence, user_transcription)
        
        phoneme_data = None
        if self.phoneme_analyzer and self.phoneme_analyzer.available:
            phoneme_data = self.phoneme_analyzer.calculate_phoneme_error_rate(
                target_sentence, user_transcription
            )
            
            if phoneme_data.get('common_errors'):
                self.error_history.extend(phoneme_data['common_errors'])
        
        prosody_data = None
        if self.prosody_analyzer and self.prosody_analyzer.available and os.path.exists(audio_file):
            prosody_data = self.prosody_analyzer.analyze_audio_file(audio_file)
            if not prosody_data or not prosody_data.get('available'):
                prosody_data = None
        
        analysis_time = time.time() - analysis_start
        
        feedback_start = time.time()
        feedback = self.feedback_gen.generate_feedback(
            target_sentence=target_sentence,
            user_transcription=user_transcription,
            word_data=word_data,
            phoneme_data=phoneme_data,
            prosody_data=prosody_data,
            error_history=self.error_history[-10:]
        )
        feedback_time = time.time() - feedback_start
        
        fluency_score = 0
        prosody_score = 0
        pause_frequency = 0
        pitch_variation = 0
        
        if prosody_data and prosody_data.get('available'):
            pause_frequency = prosody_data['rhythm'].get('pause_frequency', 0)
            pitch_variation = prosody_data['pitch'].get('variation', 0)
            
            pause_score = max(0, 100 - pause_frequency * 50)
            fluency_score = pause_score
            
            if pitch_variation > 15:
                prosody_score = 100
            elif pitch_variation > 10:
                prosody_score = 80
            elif pitch_variation > 5:
                prosody_score = 60
            else:
                prosody_score = 40
        
        if self.metrics_logger:
            interaction_data = {
                'target_sentence': target_sentence,
                'user_transcription': user_transcription,
                'transcription_accuracy': basic_metrics['similarity_score'],
                'phoneme_accuracy': phoneme_data.get('phoneme_error_rate', 0) if phoneme_data else 0,
                'fluency_score': fluency_score,
                'prosody_score': prosody_score,
                'pause_frequency': pause_frequency,
                'pitch_variation': pitch_variation,
                'overall_confidence': overall_confidence,
                'feedback': feedback
            }
            
            timings = {
                'recording': recording_time,
                'transcription': transcription_time,
                'analysis': analysis_time,
                'feedback': feedback_time,
                'total': recording_time + transcription_time + analysis_time + feedback_time
            }
            
            self.metrics_logger.log_interaction(interaction_data, timings)
        
        self.session_stats["sentences_practiced"] += 1
        self.session_stats["total_similarity"] += basic_metrics["similarity_score"]
        if basic_metrics["perfect_match"]:
            self.session_stats["perfect_matches"] += 1
        
        self.session_stats["attempts"].append({
            "target": target_sentence,
            "transcription": user_transcription,
            "similarity": basic_metrics["similarity_score"],
            "feedback": feedback
        })
        
        print(f"\n💬 {feedback}")
        self.tts.speak(feedback, streaming=config.STREAMING_TTS)
        
        self.last_feedback = feedback
        self.last_metrics = {
            'transcription_accuracy': basic_metrics['similarity_score'],
            'phoneme_accuracy': phoneme_data.get('phoneme_error_rate', 0) if phoneme_data else 0,
            'fluency_score': fluency_score,
            'prosody_score': prosody_score
        }
        
        self.next_sentence = self.get_next_sentence()
        
        return feedback, basic_metrics
    
    def run_iterative_practice(self):
        iteration = 0
        
        try:
            while True:
                iteration += 1
                
                target_sentence = self.provide_task()
                
                recording_start = time.time()
                transcription_result = self.listen()
                recording_time = time.time() - recording_start
                
                feedback, metrics = self.evaluate(target_sentence, transcription_result, 
                                                  recording_time=recording_time)
                
                print("\n" + "-"*60)
                continue_choice = input("\n▶️ Press Enter for next sentence (or type 'exit' to quit): ").strip().lower()
                if continue_choice in ['exit', 'quit', 'q']:
                    print("\n👋 Ending practice session...")
                    break
        
        except KeyboardInterrupt:
            print("\n\n⏸️  Practice interrupted by user")
        
        print("\n✅ Practice session completed!")
    
    def get_session_summary(self):
        if self.metrics_logger:
            return self.metrics_logger.get_session_summary()
        
        if self.session_stats["sentences_practiced"] > 0:
            avg_similarity = self.session_stats["total_similarity"] / self.session_stats["sentences_practiced"]
        else:
            avg_similarity = 0
        
        return {
            "total_sentences": self.session_stats["sentences_practiced"],
            "perfect_matches": self.session_stats["perfect_matches"],
            "average_similarity": round(avg_similarity, 2),
            "attempts": self.session_stats["attempts"]
        }
    
    def print_session_summary(self):
        if self.metrics_logger:
            self.metrics_logger.print_summary()
        else:
            summary = self.get_session_summary()
            
            print("\n" + "="*60)
            print("📈 SESSION SUMMARY")
            print("="*60)
            print(f"Category: {self.category}")
            print(f"Total sentences practiced: {summary['total_sentences']}")
            print(f"Perfect matches: {summary['perfect_matches']}")
            print(f"Average similarity: {summary['average_similarity']}%")
            
            if summary['total_sentences'] > 0:
                success_rate = (summary['perfect_matches'] / summary['total_sentences']) * 100
                print(f"Success rate: {success_rate:.1f}%")
            
            print("="*60)
    
    def cleanup(self):
        self.state = CoachState.FINISHED
        self.stt.cleanup()
        self.tts.cleanup()
