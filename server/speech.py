import os
import wave
from piper import PiperVoice
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # bytes

current_dir = os.getcwd()

tts_model_path = os.path.join(current_dir, "voices", "en_US-lessac-medium.onnx")
tts_model = PiperVoice.load(tts_model_path)

stt_model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_file(filename: str) -> str:
    segments, _ = stt_model.transcribe(filename, language="en", beam_size=5)
    
    full_text = ""
    for segment in segments:
        full_text += segment.text + " "
    
    return full_text.strip()

def tts(text: str, dest: str):
    """
    Docstring for tts
    
    :param text: Description
    :type text: str
    :param dest: File of type .wav
    :type dest: str
    """
    with wave.open(dest, "wb") as file:
        file.setnchannels(CHANNELS)
        file.setsampwidth(SAMPLE_WIDTH)
        file.setframerate(SAMPLE_RATE)

        tts_model.synthesize_wav(text, file)