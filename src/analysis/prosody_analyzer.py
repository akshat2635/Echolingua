import parselmouth
from parselmouth.praat import call
import numpy as np
import wave
import struct

class ProsodyAnalyzer:
    def __init__(self):
        self.available = True
    
    def analyze_audio_file(self, audio_file):
        try:
            sound = parselmouth.Sound(audio_file)
            
            pitch_data = self._extract_pitch(sound)
            intensity_data = self._extract_intensity(sound)
            rhythm_data = self._extract_rhythm(sound)
            
            return {
                'pitch': pitch_data,
                'intensity': intensity_data,
                'rhythm': rhythm_data,
                'duration': sound.duration,
                'available': True
            }
        
        except Exception as e:
            return {
                'pitch': {},
                'intensity': {},
                'rhythm': {},
                'duration': 0,
                'available': False
            }
    
    def _extract_pitch(self, sound):
        try:
            pitch = call(sound, "To Pitch", 0.0, 75, 600)
            
            pitch_values = pitch.selected_array['frequency']
            pitch_values = pitch_values[pitch_values > 0]
            
            if len(pitch_values) == 0:
                return {
                    'mean': 0,
                    'std': 0,
                    'min': 0,
                    'max': 0,
                    'range': 0,
                    'variation': 0
                }
            
            mean_pitch = np.mean(pitch_values)
            std_pitch = np.std(pitch_values)
            min_pitch = np.min(pitch_values)
            max_pitch = np.max(pitch_values)
            pitch_range = max_pitch - min_pitch
            
            if mean_pitch > 0:
                variation_coefficient = (std_pitch / mean_pitch) * 100
            else:
                variation_coefficient = 0
            
            return {
                'mean': round(mean_pitch, 2),
                'std': round(std_pitch, 2),
                'min': round(min_pitch, 2),
                'max': round(max_pitch, 2),
                'range': round(pitch_range, 2),
                'variation': round(variation_coefficient, 2)
            }
        
        except Exception as e:
            return {'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'range': 0, 'variation': 0}
    
    def _extract_intensity(self, sound):
        try:
            intensity = call(sound, "To Intensity", 75, 0.0, True)
            
            intensity_array = intensity.values[0]
            intensity_array = intensity_array[intensity_array > 0]
            
            if len(intensity_array) == 0:
                return {
                    'mean': 0,
                    'std': 0,
                    'min': 0,
                    'max': 0,
                    'range': 0
                }
            
            mean_intensity = np.mean(intensity_array)
            std_intensity = np.std(intensity_array)
            min_intensity = np.min(intensity_array)
            max_intensity = np.max(intensity_array)
            intensity_range = max_intensity - min_intensity
            
            return {
                'mean': round(mean_intensity, 2),
                'std': round(std_intensity, 2),
                'min': round(min_intensity, 2),
                'max': round(max_intensity, 2),
                'range': round(intensity_range, 2)
            }
        
        except Exception as e:
            return {'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'range': 0}
    
    def _extract_rhythm(self, sound):
        try:
            intensity = call(sound, "To Intensity", 75, 0.0, True)
            
            intensity_array = intensity.values[0]
            intensity_array = intensity_array[intensity_array > 0]
            
            if len(intensity_array) == 0:
                return {
                    'pause_count': 0,
                    'mean_pause_duration': 0,
                    'total_pause_time': 0,
                    'pause_frequency': 0,
                    'error': True
                }
            
            silence_threshold = np.mean(intensity_array) - np.std(intensity_array)
            
            is_silent = intensity_array < silence_threshold
            
            pause_count = 0
            pause_durations = []
            in_pause = False
            pause_start_idx = 0
            
            for i, silent in enumerate(is_silent):
                if silent and not in_pause:
                    in_pause = True
                    pause_start_idx = i
                elif not silent and in_pause:
                    in_pause = False
                    pause_duration = (i - pause_start_idx) * (sound.duration / len(intensity_array))
                    if pause_duration > 0.1:
                        pause_count += 1
                        pause_durations.append(pause_duration)
            
            if pause_durations:
                mean_pause = np.mean(pause_durations)
                total_pause_time = np.sum(pause_durations)
            else:
                mean_pause = 0
                total_pause_time = 0
            
            if sound.duration > 0:
                pause_frequency = pause_count / sound.duration
            else:
                pause_frequency = 0
            
            return {
                'pause_count': pause_count,
                'mean_pause_duration': round(mean_pause, 3),
                'total_pause_time': round(total_pause_time, 3),
                'pause_frequency': round(pause_frequency, 3)
            }
        
        except Exception as e:
            return {
                'pause_count': 0,
                'mean_pause_duration': 0,
                'total_pause_time': 0,
                'pause_frequency': 0,
                'error': True
            }
    
    def compare_prosody(self, target_prosody, user_prosody):
        if not target_prosody.get('available') or not user_prosody.get('available'):
            return {
                'pitch_match': 0,
                'rhythm_match': 0,
                'overall_score': 0,
                'feedback': []
            }
        
        feedback = []
        
        pitch_diff = abs(target_prosody['pitch']['mean'] - user_prosody['pitch']['mean'])
        pitch_variation_diff = abs(target_prosody['pitch']['variation'] - user_prosody['pitch']['variation'])
        
        if pitch_variation_diff < 10:
            pitch_match = 100
            feedback.append("Excellent pitch variation")
        elif pitch_variation_diff < 25:
            pitch_match = 75
            feedback.append("Good pitch variation, could be more expressive")
        else:
            pitch_match = 50
            feedback.append("Try to match the pitch variation of the target")
        
        pause_freq_diff = abs(
            target_prosody['rhythm'].get('pause_frequency', 0) - 
            user_prosody['rhythm'].get('pause_frequency', 0)
        )
        
        if pause_freq_diff < 0.1:
            rhythm_match = 100
            feedback.append("Perfect rhythm and pacing")
        elif pause_freq_diff < 0.2:
            rhythm_match = 75
            feedback.append("Good rhythm, minor timing differences")
        else:
            rhythm_match = 50
            feedback.append("Work on matching the rhythm and pacing")
        
        overall_score = (pitch_match + rhythm_match) / 2
        
        return {
            'pitch_match': round(pitch_match, 2),
            'rhythm_match': round(rhythm_match, 2),
            'overall_score': round(overall_score, 2),
            'feedback': feedback,
            'pitch_difference': round(pitch_diff, 2),
            'pause_frequency_difference': round(pause_freq_diff, 2)
        }
    
    def get_prosody_summary(self, prosody_data):
        if not prosody_data.get('available'):
            return ""
        
        pitch = prosody_data.get('pitch', {})
        rhythm = prosody_data.get('rhythm', {})
        
        if not pitch:
            return ""
        
        summary_parts = []
        
        variation = pitch.get('variation', 0)
        if variation > 0:
            if variation > 15:
                summary_parts.append("Expressive intonation")
            elif variation > 8:
                summary_parts.append("Moderate intonation")
            elif variation > 0:
                summary_parts.append("Flat intonation")
        
        pause_freq = rhythm.get('pause_frequency', 0)
        has_rhythm_error = rhythm.get('error', False)
        
        if not has_rhythm_error and pause_freq > 0:
            if pause_freq > 0.5:
                summary_parts.append("Frequent pauses")
            elif pause_freq > 0.2:
                summary_parts.append("Natural pausing")
        
        return " | ".join(summary_parts) if summary_parts else ""
