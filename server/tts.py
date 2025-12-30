import os
import wave
from piper import PiperVoice

current_dir = os.getcwd()

tts_model_path = os.path.join(current_dir, "voices", "en_US-lessac-medium.onnx")
voice = PiperVoice.load(tts_model_path)

def tts(text: str, dest: str):
    """
    Docstring for tts
    
    :param text: Description
    :type text: str
    :param dest: File of type .wav
    :type dest: str
    """
    with wave.open(dest, "wb") as file:
        voice.synthesize_wav(text, file)