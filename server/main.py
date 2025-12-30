import socket
import wave

HOST = "0.0.0.0"
PORT = 5000

SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # bytes

WAV_FILE = "recording.wav"

print("Server listening...")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    print("Connected:", addr)

    recording = False
    wf = None
    while True:
        data = conn.recv(1024)
        #print(f"Received {len(data)} bytes")
        if not data:
            break
        
        if data.startswith(b"START"):
            print("START recording")
            recording = True
            wf = wave.open(WAV_FILE, "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(SAMPLE_RATE)
           

        elif data.find(b"STOP") != -1:
            print("STOP recording")
            recording = False
            if wf:
                wf.close()
                wf = None
            print("Saved recording.wav")

        elif recording and wf:
            wf.writeframes(data)

