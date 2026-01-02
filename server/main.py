import os
import socket
import tempfile
import wave

import speech
from ai import ask_llama

HOST = "0.0.0.0"
PORT = 5005
CHUNK_SIZE = 256

def send_wav(sock: socket.socket, addr: tuple[str, int], filename: str):
     with wave.open(filename, 'rb') as wf:
        sock.sendto(b"START", addr)
        print(">> Streaming Audio...")

        while True:
            data = wf.readframes(CHUNK_SIZE // (wf.getsampwidth() * wf.getnchannels()))
            if not data:
                break
            
            s.sendto(data, addr)

        # Send a few STOP packets just to be safe (UDP is unreliable)
        for _ in range(3):
            s.sendto(b"STOP", addr)
        
        print("\n>> Finished streaming file.")

if __name__ == "__main__":
    print("Server listening...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((HOST, PORT))
            s.settimeout(1)

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
                        os.remove(received_wav)
                        received_wav = None

                        response = ask_llama(transcript)
                        print(f"\n>>> LLAMA SAYS: {response}\n")

                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, mode='wb') as f:
                            response_wav = f.name

                        speech.tts(response, response_wav)
                        send_wav(s, client_addr, response_wav)
                        os.remove(response_wav)

                        audio_bytes = []

                    elif received_wav:
                        audio_bytes.append(data)
                except socket.timeout:
                    continue
    except KeyboardInterrupt:
        print("\nServer stopped by user")

        if received_wav:
            os.remove(received_wav)
