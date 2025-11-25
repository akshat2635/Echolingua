import io
import math
from deepgram import DeepgramClient
import pyaudio
import wave
import struct
from src.utils import config

class TextToSpeech:
    def __init__(self):
        self.deepgram = DeepgramClient(api_key=config.DEEPGRAM_API_KEY)
        self.audio = pyaudio.PyAudio()
    
    def play_beep(self, frequency=800, duration=0.2):
        try:
            sample_rate = 16000
            num_samples = int(sample_rate * duration)
            
            samples = []
            for i in range(num_samples):
                value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
                samples.append(struct.pack('h', value))
            
            beep_data = b''.join(samples)
            
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                output=True
            )
            
            stream.write(beep_data)
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            pass
    
    def text_to_speech(self, text, output_file="temp_tts.wav"):
        try:
            response = self.deepgram.speak.v1.audio.generate(
                text=text,
                model=config.DEEPGRAM_TTS_MODEL,
                encoding=config.DEEPGRAM_TTS_ENCODING,
                container=config.DEEPGRAM_TTS_CONTAINER,
                sample_rate=config.DEEPGRAM_TTS_SAMPLE_RATE
            )
            
            with open(output_file, "wb") as f:
                for chunk in response:
                    f.write(chunk)
            
            return output_file
            
        except Exception as e:
            print(f"❌ Error during text-to-speech: {e}")
            return None
    
    def speak_streaming(self, text):
        try:
            response = self.deepgram.speak.v1.audio.generate(
                text=text,
                model=config.DEEPGRAM_TTS_MODEL,
                encoding=config.DEEPGRAM_TTS_ENCODING,
                container=config.DEEPGRAM_TTS_CONTAINER,
                sample_rate=config.DEEPGRAM_TTS_SAMPLE_RATE
            )
            
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=config.DEEPGRAM_TTS_SAMPLE_RATE,
                output=True,
                frames_per_buffer=4096
            )
            
            buffer = b''
            min_buffer_size = 16384
            header_skipped = False
            playback_started = False
            
            for chunk in response:
                if chunk and len(chunk) > 0:
                    buffer += chunk
                    
                    if not header_skipped and len(buffer) > 44:
                        if buffer[:4] == b'RIFF' and buffer[8:12] == b'WAVE':
                            data_pos = buffer.find(b'data')
                            if data_pos != -1:
                                buffer = buffer[data_pos + 8:]
                        header_skipped = True
                    
                    if not playback_started and len(buffer) >= min_buffer_size:
                        playback_started = True
                    
                    if playback_started:
                        while len(buffer) >= 8192:
                            chunk_to_play = buffer[:4096]
                            buffer = buffer[4096:]
                            stream.write(chunk_to_play)
            
            if len(buffer) > 0:
                chunk_size = 4096
                for i in range(0, len(buffer), chunk_size):
                    stream.write(buffer[i:i+chunk_size])
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"❌ Error during streaming text-to-speech: {e}")
    
    def play_audio(self, audio_file):
        try:
            with wave.open(audio_file, 'rb') as wf:
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                chunk_size = 1024
                data = wf.readframes(chunk_size)
                
                while data:
                    stream.write(data)
                    data = wf.readframes(chunk_size)
                
                stream.stop_stream()
                stream.close()
                
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
    
    def speak(self, text, streaming=True):
        if streaming:
            self.speak_streaming(text)
        else:
            audio_file = self.text_to_speech(text)
            if audio_file:
                self.play_audio(audio_file)
    
    def cleanup(self):
        self.audio.terminate()
