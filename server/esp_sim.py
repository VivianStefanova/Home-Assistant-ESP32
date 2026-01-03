import os
import socket
import sys
import time
import wave

import speech

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005
CHUNK_SIZE = 512

def is_command(data: bytes) -> bool:
    commands = [b"LED ON", b"LED OFF", b"LED R", b"LED G", b"LED B", b"NONE"]
    return any(data.startswith(cmd) for cmd in commands)

def emulate_esp32():
    input_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join("audio_tests", "date.wav")

    with wave.open(input_file, 'rb') as wf:
        if wf.getframerate() != 16000:
            print(f"WARNING: Input file is {wf.getframerate()}Hz. Server expects 16000Hz.")
            print("The audio might sound fast (chipmunk) or slow (demon) on the other side.")

        print(f"Connecting to {SERVER_IP}:{SERVER_PORT}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        print(">> Sending START")
        sock.sendto(b"START", (SERVER_IP, SERVER_PORT))
        time.sleep(0.1)

        print(">> Streaming Audio...")
        bytes_sent = 0
        
        bytes_per_sec = wf.getframerate() * wf.getsampwidth()
        delay = CHUNK_SIZE / bytes_per_sec

        while True:
            data = wf.readframes(CHUNK_SIZE // (wf.getsampwidth() * wf.getnchannels()))
            if not data:
                break
            
            sock.sendto(data, (SERVER_IP, SERVER_PORT))
            bytes_sent += len(data)
            
            #time.sleep(delay)
            
            sys.stdout.write(f"\rSent {bytes_sent} bytes...")
            sys.stdout.flush()

        print("\n>> Finished streaming file.")

        # Send a few STOP packets just to be safe (UDP is unreliable)
        for _ in range(10):
            sock.sendto(b"STOP", (SERVER_IP, SERVER_PORT))
        
        print(">> Sent STOP. Done.")
        sock.settimeout(1)

        received_wav: str | None = None
        audio_bytes: list[bytes] = []

        while True:
            try:
                data, _ = sock.recvfrom(CHUNK_SIZE)
                print(f"Received {len(data)} bytes")
                if not data:
                    break

                if is_command(data):
                    print(data.decode())

                    if not received_wav:
                        received_wav = os.path.join("audio_tests", "response.wav")

                elif data.find(b"STOP") != -1 and received_wav:
                    with wave.open(received_wav, 'wb') as wav_file:
                        wav_file.setnchannels(speech.CHANNELS)
                        wav_file.setsampwidth(speech.SAMPLE_WIDTH)
                        wav_file.setframerate(speech.SAMPLE_RATE)
            
                        wav_file.writeframes(b''.join(audio_bytes))

                    print("STOP recording -> saved WAV")
                    break

                elif received_wav:
                    audio_bytes.append(data)
            except socket.timeout:
                continue

        sock.close()

if __name__ == "__main__":
    emulate_esp32()