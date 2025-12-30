import os
import socket
import tempfile
import wave

from voice import transcribe_file, ask_llama
from tts import tts

HOST = "0.0.0.0"
PORT = 5005

SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # bytes

if __name__ == "__main__":
#     text = transcribe_file("test2.mp3")
#     response = ask_llama(text)
#     tts(response, "response.wav")
    print("Server listening...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((HOST, PORT))
            s.settimeout(1)

            client_addr: str | None = None
            received_wav: str | None = None
            audio_bytes: list[bytes] = []

            while True:
                try:
                    data, client_addr = s.recvfrom(256)
                    if not data:
                        break

                    if data.startswith(b"START"):
                        print("START recording")
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, mode='wb') as f:
                            received_wav = f.name

                    elif data.find(b"STOP") != -1 and received_wav:
                        with wave.open(received_wav, 'wb') as wav_file:
                            wav_file.setnchannels(CHANNELS)
                            wav_file.setsampwidth(SAMPLE_WIDTH)
                            wav_file.setframerate(SAMPLE_RATE)
                
                            wav_file.writeframes(b''.join(audio_bytes))

                        print("STOP recording -> saved WAV")
                        transcript = transcribe_file(received_wav)
                        print("Received transcription: " + transcript.strip())

                        os.remove(received_wav)
                        received_wav = None
                        audio_bytes = []

                    elif received_wav:
                        audio_bytes.append(data)
                except socket.timeout:
                    continue
    except KeyboardInterrupt:
        print("\nServer stopped by user")

        if received_wav:
            os.remove(received_wav)
