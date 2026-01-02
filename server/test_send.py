import os
import socket

from main import send_wav

HOST = "0.0.0.0"
PORT = 5005
CHUNK_SIZE = 256
INPUT_FILE = os.path.join("audio_tests", "repeat.wav")

if __name__ == "__main__":
    print("Server listening...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((HOST, PORT))
            s.settimeout(1)

            received_wav: bool = False
            while True:
                try:
                    data, client_addr = s.recvfrom(CHUNK_SIZE)
                    if not data:
                        break

                    if data.startswith(b"START"):
                        print("START recording")
                        received_wav = True

                    elif data.find(b"STOP") != -1 and received_wav:
                        print("STOP recording")

                        send_wav(s, client_addr, INPUT_FILE)

                        received_wav = False
                except socket.timeout:
                    continue
    except KeyboardInterrupt:
        print("\nServer stopped by user")
