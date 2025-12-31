import os
import socket
import tempfile
import wave

import speech
from ai import ask_llama

HOST = "0.0.0.0"
PORT = 5005

if __name__ == "__main__":
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
                            wav_file.setnchannels(speech.CHANNELS)
                            wav_file.setsampwidth(speech.SAMPLE_WIDTH)
                            wav_file.setframerate(speech.SAMPLE_RATE)
                
                            wav_file.writeframes(b''.join(audio_bytes))

                        print("STOP recording -> saved WAV")
                        transcript = speech.transcribe_file(received_wav)
                        print("Received transcription: " + transcript.strip())

                        response = ask_llama(transcript)
                        print(f"\n>>> LLAMA SAYS: {response}\n")
                        speech.tts(response, os.path.join("audio_tests", "response_new.wav"))

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
