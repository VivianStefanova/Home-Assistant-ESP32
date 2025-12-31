import os
import socket
import sys
import time
import wave

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005
INPUT_FILE = os.path.join("audio_tests", "response_new.wav")
CHUNK_SIZE = 256

def emulate_esp32():
    with wave.open(INPUT_FILE, 'rb') as wf:
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
        for _ in range(3):
            sock.sendto(b"STOP", (SERVER_IP, SERVER_PORT))
            time.sleep(0.01)
        
        print(">> Sent STOP. Done.")
        sock.close()

if __name__ == "__main__":
    emulate_esp32()