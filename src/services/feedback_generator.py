from groq import Groq
from src.utils import config

class FeedbackGenerator:
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
    
    def generate_feedback(self, target_sentence, user_transcription, word_data=None, 
                         phoneme_data=None, prosody_data=None, error_history=None):
        try:
            if not user_transcription or user_transcription.strip() == "":
                return "I couldn't hear you clearly. Please try speaking a bit louder and closer to the microphone."
            
            similarity = self.calculate_similarity(target_sentence, user_transcription)
            similarity_score = round(similarity * 100, 2)
            
            # Check if pronunciation is perfect or near-perfect
            if similarity_score >= 98 and phoneme_data and phoneme_data.get('phoneme_error_rate', 0) < 2:
                return "Excellent! Your pronunciation is perfect. Let's try something more challenging to continue improving."
            
            phoneme_error_rate = 0
            phoneme_errors_desc = "No phoneme data available"
            if phoneme_data:
                phoneme_error_rate = phoneme_data.get('phoneme_error_rate', 0)
                common_errors = phoneme_data.get('common_errors', [])
                if common_errors:
                    error_descs = [err.get('description', '') for err in common_errors[:3]]
                    phoneme_errors_desc = "; ".join(error_descs)
                else:
                    phoneme_errors_desc = "No significant phoneme errors"
            
            prosody_summary = "No prosody data available"
            pitch_variation = 0
            
            if prosody_data and prosody_data.get('available'):
                pitch_variation = prosody_data.get('pitch', {}).get('variation', 0)
                
                from src.analysis.prosody_analyzer import ProsodyAnalyzer
                analyzer = ProsodyAnalyzer()
                prosody_summary = analyzer.get_prosody_summary(prosody_data)
                
                if not prosody_summary:
                    prosody_summary = "Prosody data incomplete - analysis not available"
            
            error_history_text = "No previous error patterns"
            if error_history and len(error_history) > 0:
                recent_errors = error_history[-5:]
                error_descriptions = [err.get('description', '') for err in recent_errors]
                error_history_text = "; ".join(error_descriptions)
            
            prompt = config.FEEDBACK_PROMPT_TEMPLATE.format(
                target_sentence=target_sentence,
                similarity_score=similarity_score,
                phoneme_error_rate=phoneme_error_rate,
                phoneme_errors=phoneme_errors_desc,
                prosody_summary=prosody_summary,
                pitch_variation=pitch_variation,
                error_history=error_history_text
            )
            
            response = self.client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional English pronunciation coach. Provide specific, actionable feedback without mentioning transcription text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=config.GROQ_TEMPERATURE,
                max_tokens=config.GROQ_MAX_TOKENS
            )
            
            if not response.choices or not response.choices[0].message.content:
                return self._fallback_feedback(similarity_score, phoneme_error_rate)
            
            feedback = response.choices[0].message.content.strip()
            
            return feedback
            
        except Exception as e:
            return "I had trouble analyzing your pronunciation. Let's try the next sentence."
    
    def _fallback_feedback(self, similarity_score, phoneme_error_rate):
        if similarity_score > 90 and phoneme_error_rate < 10:
            return "Excellent pronunciation! You're speaking very clearly. Let's try something more challenging."
        elif similarity_score > 70:
            return "Good effort! Focus on pronouncing each syllable clearly and maintaining a steady rhythm."
        else:
            return "Keep practicing! Pay attention to each word's pronunciation and try to speak more slowly and clearly."
    
    def generate_initial_sentence(self, difficulty_level):
        try:
            level_map = {
                'basic': 'beginner',
                'beginner': 'beginner',
                'intermediate': 'intermediate',
                'advanced': 'advanced',
                'random': 'intermediate'
            }
            
            mapped_level = level_map.get(difficulty_level.lower(), 'intermediate')
            
            prompt = config.INITIAL_SENTENCE_TEMPLATE.format(
                difficulty_level=mapped_level
            )
            
            response = self.client.chat.completions.create(
                model=config.GROQ_SENTENCE_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert English pronunciation curriculum designer. Generate engaging practice sentences for pronunciation training."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=config.GROQ_SENTENCE_TEMPERATURE,
                max_tokens=config.GROQ_SENTENCE_MAX_TOKENS
            )
            
            if response.choices and response.choices[0].message.content:
                new_sentence = response.choices[0].message.content.strip()
                new_sentence = new_sentence.strip('"').strip("'")
                return new_sentence
            else:
                return None
            
        except Exception as e:
            return None
    
    def generate_new_sentence(self, difficulty_level, error_patterns, recent_sentences, 
                             previous_feedback=None, last_metrics=None):
        try:
            if error_patterns:
                error_desc = "; ".join([err.get('description', '') for err in error_patterns[-5:]])
                problem_phonemes = ", ".join(set([err.get('expected_phoneme', '') for err in error_patterns[-3:] if err.get('expected_phoneme')]))
            else:
                error_desc = "No specific error patterns yet"
                problem_phonemes = "general pronunciation"
            
            focus_areas = "pronunciation clarity and accuracy"
            if previous_feedback:
                focus_keywords = []
                if "th" in previous_feedback.lower():
                    focus_keywords.append("'th' sounds")
                if "r" in previous_feedback.lower() or "l" in previous_feedback.lower():
                    focus_keywords.append("'r' and 'l' distinction")
                if "stress" in previous_feedback.lower() or "rhythm" in previous_feedback.lower():
                    focus_keywords.append("word stress and rhythm")
                if "pace" in previous_feedback.lower() or "speed" in previous_feedback.lower():
                    focus_keywords.append("speech pace")
                if "pitch" in previous_feedback.lower() or "intonation" in previous_feedback.lower():
                    focus_keywords.append("intonation")
                
                if focus_keywords:
                    focus_areas = ", ".join(focus_keywords)
            
            transcription_accuracy = 0
            phoneme_accuracy = 0
            if last_metrics:
                transcription_accuracy = last_metrics.get('transcription_accuracy', 0)
                phoneme_accuracy = 100 - last_metrics.get('phoneme_accuracy', 0)
            
            recent_list = "\n".join([f"- {s}" for s in recent_sentences[-3:]]) if recent_sentences else "None"
            
            feedback_context = previous_feedback if previous_feedback else "First practice attempt - establishing baseline"
            
            prompt = config.SENTENCE_GENERATION_TEMPLATE.format(
                difficulty_level=difficulty_level,
                previous_feedback=feedback_context,
                error_patterns=error_desc,
                problem_phonemes=problem_phonemes,
                transcription_accuracy=transcription_accuracy,
                phoneme_accuracy=phoneme_accuracy,
                focus_areas=focus_areas,
                recent_sentences=recent_list
            )
            
            response = self.client.chat.completions.create(
                model=config.GROQ_SENTENCE_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert English pronunciation curriculum designer. Generate practice sentences that target specific pronunciation challenges."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=config.GROQ_SENTENCE_TEMPERATURE,
                max_tokens=config.GROQ_SENTENCE_MAX_TOKENS
            )
            
            if response.choices and response.choices[0].message.content:
                new_sentence = response.choices[0].message.content.strip()
                new_sentence = new_sentence.strip('"').strip("'")
                return new_sentence
            else:
                return None
            
        except Exception as e:
            return None
    
    def calculate_similarity(self, target_sentence, user_transcription):
        target = target_sentence.lower().strip()
        transcript = user_transcription.lower().strip()
        
        distance = self._levenshtein_distance(target, transcript)
        max_len = max(len(target), len(transcript))
        
        if max_len == 0:
            return 1.0
        
        similarity = 1 - (distance / max_len)
        return similarity
    
    def _levenshtein_distance(self, s1, s2):
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def get_metrics(self, target_sentence, user_transcription):
        similarity = self.calculate_similarity(target_sentence, user_transcription)
        distance = self._levenshtein_distance(
            target_sentence.lower().strip(),
            user_transcription.lower().strip()
        )
        
        return {
            "similarity_score": round(similarity * 100, 2),
            "levenshtein_distance": distance,
            "target_length": len(target_sentence.split()),
            "transcript_length": len(user_transcription.split()),
            "perfect_match": target_sentence.lower().strip() == user_transcription.lower().strip()
        }
