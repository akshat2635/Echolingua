from phonemizer import phonemize
from phonemizer.backend import EspeakBackend
import difflib
import os
import sys
from src.utils import config

class PhonemeAnalyzer:
    def __init__(self):
        try:
            # Use manual path from config if provided
            if hasattr(config, 'ESPEAK_LIBRARY_PATH') and config.ESPEAK_LIBRARY_PATH:
                os.environ['PHONEMIZER_ESPEAK_LIBRARY'] = config.ESPEAK_LIBRARY_PATH
            
            # Try to set espeak library path for Windows
            elif sys.platform == 'win32':
                # Common Windows installation paths
                possible_paths = [
                    r'C:\Program Files\eSpeak NG\libespeak-ng.dll',
                    r'C:\Program Files (x86)\eSpeak NG\libespeak-ng.dll',
                    r'C:\Program Files\eSpeak\espeak.exe',
                    r'C:\Program Files (x86)\eSpeak\espeak.exe',
                ]
                
                # Check if any path exists and set PHONEMIZER_ESPEAK_LIBRARY
                for path in possible_paths:
                    if os.path.exists(path):
                        os.environ['PHONEMIZER_ESPEAK_LIBRARY'] = path
                        break
            
            self.backend = EspeakBackend('en-us', preserve_punctuation=False, with_stress=True)
            self.available = True
        except Exception as e:
            self.available = False
    
    def text_to_phonemes(self, text):
        if not self.available:
            return ""
        
        try:
            phonemes = phonemize(
                text,
                language='en-us',
                backend='espeak',
                strip=True,
                preserve_punctuation=False,
                with_stress=True
            )
            return phonemes
        except Exception as e:
            return ""
    
    def align_phonemes(self, target_phonemes, transcribed_phonemes):
        if not target_phonemes or not transcribed_phonemes:
            return {
                'alignment': [],
                'differences': [],
                'error_count': 0
            }
        
        matcher = difflib.SequenceMatcher(None, target_phonemes, transcribed_phonemes)
        alignment = []
        differences = []
        error_count = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                alignment.append({
                    'type': 'match',
                    'target': target_phonemes[i1:i2],
                    'transcribed': transcribed_phonemes[j1:j2]
                })
            elif tag == 'replace':
                alignment.append({
                    'type': 'substitution',
                    'target': target_phonemes[i1:i2],
                    'transcribed': transcribed_phonemes[j1:j2]
                })
                differences.append({
                    'error_type': 'substitution',
                    'expected': target_phonemes[i1:i2],
                    'actual': transcribed_phonemes[j1:j2],
                    'position': i1
                })
                error_count += 1
            elif tag == 'delete':
                alignment.append({
                    'type': 'deletion',
                    'target': target_phonemes[i1:i2],
                    'transcribed': ''
                })
                differences.append({
                    'error_type': 'deletion',
                    'expected': target_phonemes[i1:i2],
                    'actual': '',
                    'position': i1
                })
                error_count += 1
            elif tag == 'insert':
                alignment.append({
                    'type': 'insertion',
                    'target': '',
                    'transcribed': transcribed_phonemes[j1:j2]
                })
                differences.append({
                    'error_type': 'insertion',
                    'expected': '',
                    'actual': transcribed_phonemes[j1:j2],
                    'position': i1
                })
                error_count += 1
        
        return {
            'alignment': alignment,
            'differences': differences,
            'error_count': error_count
        }
    
    def calculate_phoneme_error_rate(self, target_text, transcribed_text):
        if not self.available:
            return {
                'phoneme_error_rate': 0.0,
                'target_phonemes': '',
                'transcribed_phonemes': '',
                'alignment': {},
                'common_errors': []
            }
        
        target_phonemes = self.text_to_phonemes(target_text)
        transcribed_phonemes = self.text_to_phonemes(transcribed_text)
        
        if not target_phonemes:
            return {
                'phoneme_error_rate': 0.0,
                'target_phonemes': '',
                'transcribed_phonemes': transcribed_phonemes,
                'alignment': {},
                'common_errors': []
            }
        
        alignment = self.align_phonemes(target_phonemes, transcribed_phonemes)
        
        total_phonemes = len(target_phonemes.replace(' ', ''))
        if total_phonemes > 0:
            per = (alignment['error_count'] / total_phonemes) * 100
        else:
            per = 0.0
        
        common_errors = self._identify_common_errors(alignment['differences'])
        
        return {
            'phoneme_error_rate': round(per, 2),
            'target_phonemes': target_phonemes,
            'transcribed_phonemes': transcribed_phonemes,
            'alignment': alignment,
            'common_errors': common_errors,
            'total_phoneme_errors': alignment['error_count'],
            'total_phonemes': total_phonemes
        }
    
    def _identify_common_errors(self, differences):
        error_patterns = []
        
        for diff in differences:
            error_type = diff['error_type']
            expected = diff.get('expected', '')
            actual = diff.get('actual', '')
            
            pattern = {
                'type': error_type,
                'expected_phoneme': expected,
                'actual_phoneme': actual,
                'description': self._describe_phoneme_error(expected, actual, error_type)
            }
            error_patterns.append(pattern)
        
        return error_patterns
    
    def _describe_phoneme_error(self, expected, actual, error_type):
        if error_type == 'substitution':
            confusions = {
                ('θ', 'f'): "Pronouncing 'th' as 'f' sound",
                ('θ', 's'): "Pronouncing 'th' as 's' sound",
                ('ð', 'd'): "Pronouncing voiced 'th' as 'd' sound",
                ('v', 'w'): "Confusing 'v' and 'w' sounds",
                ('l', 'r'): "Confusing 'l' and 'r' sounds",
                ('iː', 'ɪ'): "Confusing long 'ee' with short 'i' sound",
            }
            
            for (exp, act), desc in confusions.items():
                if exp in expected and act in actual:
                    return desc
            
            return f"Substituted '{expected}' with '{actual}'"
        
        elif error_type == 'deletion':
            return f"Omitted phoneme '{expected}'"
        
        elif error_type == 'insertion':
            return f"Added extra phoneme '{actual}'"
        
        return "Phoneme mismatch"
    
    def get_phoneme_summary(self, phoneme_data):
        if not self.available or not phoneme_data:
            return ""
        
        per = phoneme_data.get('phoneme_error_rate', 0)
        common_errors = phoneme_data.get('common_errors', [])
        
        summary_parts = []
        
        if per == 0:
            summary_parts.append("Perfect phoneme accuracy!")
        elif per < 10:
            summary_parts.append(f"Excellent phoneme accuracy ({100-per:.1f}%)")
        elif per < 25:
            summary_parts.append(f"Good phoneme accuracy ({100-per:.1f}%)")
        else:
            summary_parts.append(f"Phoneme accuracy needs improvement ({100-per:.1f}%)")
        
        if common_errors:
            error_descriptions = [err['description'] for err in common_errors[:3]]
            if error_descriptions:
                summary_parts.append("Common issues: " + ", ".join(error_descriptions))
        
        return " | ".join(summary_parts)
