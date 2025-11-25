import pyaudio
import wave
import io
import time
from deepgram import DeepgramClient
from src.utils import config

class SpeechToText:
    def __init__(self):
        self.deepgram = DeepgramClient(api_key=config.DEEPGRAM_API_KEY)
        self.audio = pyaudio.PyAudio()
        
    def record_audio(self, duration=None, output_file="temp_recording.wav", play_beep=True):
        if play_beep:
            from src.services.text_to_speech import TextToSpeech
            tts = TextToSpeech()
            tts.play_beep()
            tts.cleanup()
            time.sleep(0.1)
        
        print("🎤 Recording...")
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=config.AUDIO_CHANNELS,
            rate=config.AUDIO_SAMPLE_RATE,
            input=True,
            frames_per_buffer=config.AUDIO_CHUNK_SIZE
        )
        
        frames = []
        start_time = time.time()
        silence_start = None
        recording = True
        speech_detected = False
        waiting_for_speech = True
        
        try:
            while recording:
                data = stream.read(config.AUDIO_CHUNK_SIZE, exception_on_overflow=False)
                frames.append(data)
                
                elapsed_time = time.time() - start_time
                
                audio_chunk = int.from_bytes(data[:2], byteorder='little', signed=True)
                is_speech = abs(audio_chunk) > config.SILENCE_THRESHOLD
                
                if waiting_for_speech:
                    if is_speech:
                        speech_detected = True
                        waiting_for_speech = False
                        silence_start = None
                    elif elapsed_time > config.MIN_SPEECH_DELAY:
                        print("\n⏰ No speech detected, stopping...")
                        recording = False
                        continue
                
                if speech_detected:
                    if not is_speech:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > config.SILENCE_DURATION:
                            recording = False
                    else:
                        silence_start = None
                
                if duration and elapsed_time > duration:
                    recording = False
                    
        except KeyboardInterrupt:
            print("\n⏹️  Recording stopped by user")
        finally:
            stream.stop_stream()
            stream.close()
        
        print("✅ Recording complete")
        
        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(config.AUDIO_CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(config.AUDIO_SAMPLE_RATE)
            wf.writeframes(b''.join(frames))
        
        return output_file
    
    def transcribe_audio(self, audio_file):
        try:
            transcription_start = time.time()
            
            with open(audio_file, 'rb') as audio:
                buffer_data = audio.read()
            
            response = self.deepgram.listen.v1.media.transcribe_file(
                request=buffer_data,
                model=config.DEEPGRAM_STT_MODEL,
                language=config.DEEPGRAM_STT_LANGUAGE,
                smart_format=True,
                punctuate=True,
                diarize=False,
                utterances=False
            )
            
            transcription_time = time.time() - transcription_start
            
            alternative = response.results.channels[0].alternatives[0]
            transcript = alternative.transcript
            
            words = []
            if hasattr(alternative, 'words') and alternative.words:
                for word in alternative.words:
                    words.append({
                        'word': word.word,
                        'confidence': word.confidence if hasattr(word, 'confidence') else 1.0,
                        'start': word.start if hasattr(word, 'start') else 0,
                        'end': word.end if hasattr(word, 'end') else 0
                    })
            
            return {
                'transcript': transcript,
                'words': words,
                'confidence': alternative.confidence if hasattr(alternative, 'confidence') else 1.0,
                'processing_time': transcription_time
            }
            
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            return {'transcript': '', 'words': [], 'confidence': 0.0, 'processing_time': 0}
    
    def transcribe_streaming(self, duration=None, play_beep=True):
        if play_beep:
            from src.services.text_to_speech import TextToSpeech
            tts = TextToSpeech()
            tts.play_beep()
            tts.cleanup()
            time.sleep(0.1)
        
        print("🎤 Recording...")
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=config.AUDIO_CHANNELS,
            rate=config.AUDIO_SAMPLE_RATE,
            input=True,
            frames_per_buffer=config.AUDIO_CHUNK_SIZE
        )
        
        frames = []
        start_time = time.time()
        silence_start = None
        recording = True
        speech_detected = False
        waiting_for_speech = True
        
        try:
            while recording:
                data = stream.read(config.AUDIO_CHUNK_SIZE, exception_on_overflow=False)
                frames.append(data)
                
                elapsed_time = time.time() - start_time
                
                audio_chunk = int.from_bytes(data[:2], byteorder='little', signed=True)
                is_speech = abs(audio_chunk) > config.SILENCE_THRESHOLD
                
                if waiting_for_speech:
                    if is_speech:
                        speech_detected = True
                        waiting_for_speech = False
                        silence_start = None
                    elif elapsed_time > config.MIN_SPEECH_DELAY:
                        print("\n⏰ No speech detected, stopping...")
                        recording = False
                        continue
                
                if speech_detected:
                    if not is_speech:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > config.SILENCE_DURATION:
                            recording = False
                    else:
                        silence_start = None
                
                if duration and elapsed_time > duration:
                    recording = False
                    
        except KeyboardInterrupt:
            print("\n⏹️  Recording stopped")
        finally:
            stream.stop_stream()
            stream.close()
        
        print("✅ Recording complete")
        
        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, 'wb') as wf:
            wf.setnchannels(config.AUDIO_CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(config.AUDIO_SAMPLE_RATE)
            wf.writeframes(b''.join(frames))
        
        audio_buffer.seek(0)
        buffer_data = audio_buffer.read()
        
        try:
            transcription_start = time.time()
            
            response = self.deepgram.listen.v1.media.transcribe_file(
                request=buffer_data,
                model=config.DEEPGRAM_STT_MODEL,
                language=config.DEEPGRAM_STT_LANGUAGE,
                smart_format=True,
                punctuate=True,
                diarize=False,
                utterances=False
            )
            
            transcription_time = time.time() - transcription_start
            
            alternative = response.results.channels[0].alternatives[0]
            transcript = alternative.transcript
            
            words = []
            if hasattr(alternative, 'words') and alternative.words:
                for word in alternative.words:
                    words.append({
                        'word': word.word,
                        'confidence': word.confidence if hasattr(word, 'confidence') else 1.0,
                        'start': word.start if hasattr(word, 'start') else 0,
                        'end': word.end if hasattr(word, 'end') else 0
                    })
            
            return {
                'transcript': transcript,
                'words': words,
                'confidence': alternative.confidence if hasattr(alternative, 'confidence') else 1.0,
                'processing_time': transcription_time
            }
            
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            return {'transcript': '', 'words': [], 'confidence': 0.0, 'processing_time': 0}
    
    def record_and_transcribe(self, duration=None, streaming=False):
        if streaming:
            return self.transcribe_streaming(duration)
        else:
            audio_file = self.record_audio(duration)
            result = self.transcribe_audio(audio_file)
            return result
    
    def cleanup(self):
        self.audio.terminate()
