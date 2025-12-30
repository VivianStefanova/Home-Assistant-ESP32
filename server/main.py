import socket

# from voice import transcribe_file, ask_llama
# from tts import tts

# IP = "127.0.0.1"
# PORT = 5005

# if __name__ == "__main__":
#     # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     # s.bind((IP, PORT))

#     # data, addr = s.recv(1024)
#     text = transcribe_file("test2.mp3")
#     response = ask_llama(text)
#     tts(response, "response.wav")

import wave
from faster_whisper import WhisperModel

HOST = "0.0.0.0"
PORT = 5000

SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # bytes

WAV_FILE = "recording.wav"

# Load Whisper model once
model = WhisperModel("small", device="cpu")  # use "cuda" if you have GPU

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

                 # TRANSCRIBE with Whisper
                print("Transcribing...")
                segments, info = model.transcribe(WAV_FILE)
                transcript = ""
                for segment in segments:
                    transcript += segment.text + " "
                #print("Transcript:", transcript.strip())
                with open("transcript.txt", "w", encoding="utf-8") as f:
                    f.write(transcript.strip())
                print("Transcription saved to transcript.txt")    

            elif recording and wf:
                wf.writeframes(data)

except KeyboardInterrupt:
    print("\nServer stopped by user")
    if wf:
        wf.close()
