import ollama

LLAMA_MODEL = "llama3.2"

def ask_llama(text: str) -> str:
    """Sends text to local Llama and prints response"""
    response = ollama.chat(model=LLAMA_MODEL, messages=[
        {
            'role': 'system', 
            'content': 'You are a helpful voice assistant.\
                        1. Provide extremely concise, direct answers (1-2 sentences max).\
                        2. Do NOT use markdown, asterisks (*), bold (**), or special characters.\
                        3. Do NOT use lists or bullet points. Speak in natural, flowing paragraphs.\
                        4. Do NOT output code blocks or visual formatting.\
                        5. If the answer requires a list, describe it verbally (e.g., "First... then... finally...").'
        },
        {
            'role': 'user', 
            'content': text
        },
    ])
    
    return response['message']['content']