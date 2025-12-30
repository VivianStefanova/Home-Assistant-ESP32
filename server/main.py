import socket
from voice import transcribe_file, ask_llama
from tts import tts

IP = "127.0.0.1"
PORT = 5005

if __name__ == "__main__":
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.bind((IP, PORT))

    # data, addr = s.recv(1024)
    text = transcribe_file("test2.mp3")
    response = ask_llama(text)
    tts(response, "response.wav")
