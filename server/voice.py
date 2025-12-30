from faster_whisper import WhisperModel
import ollama

LLAMA_MODEL = "llama3.2"
model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_file(filename: str) -> str:
    segments, _ = model.transcribe(filename, language="en", beam_size=5)
    
    full_text = ""
    for segment in segments:
        full_text += segment.text + " "
    
    return full_text.strip()

def ask_llama(text: str) -> str:
    """Sends text to local Llama and prints response"""
    print(f"\n[Sending to {LLAMA_MODEL}...] '{text}'")
    
    response = ollama.chat(model=LLAMA_MODEL, messages=[
        {
            'role': 'system', 
            'content': 'You are a helpful voice assistant. Keep answers short and concise.'
        },
        {
            'role': 'user', 
            'content': text
        },
    ])
    
    ai_reply = response['message']['content']
    print(f"\n>>> LLAMA SAYS: {ai_reply}\n")
    return ai_reply