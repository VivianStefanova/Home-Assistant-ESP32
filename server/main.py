import socket
import wave

HOST = "0.0.0.0"
PORT = 5000

SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # bytes

WAV_FILE = "recording.wav"

print("Server listening...")


try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print("Server listening...")
        conn, addr = s.accept()
        print("Connected:", addr)

        recording = False
        wf = None

        while True:
            data = conn.recv(1024)
            if not data:
                break

            if data.startswith(b"START"):
                recording = True
                wf = wave.open(WAV_FILE, "wb")
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(SAMPLE_WIDTH)
                wf.setframerate(SAMPLE_RATE)
                print("START recording")

            elif data.find(b"STOP") != -1:
                if wf:
                    wf.close()
                    wf = None
                recording = False
                print("STOP recording -> saved WAV")

            elif recording and wf:
                wf.writeframes(data)

except KeyboardInterrupt:
    print("\nServer stopped by user")
    if wf:
        wf.close()
