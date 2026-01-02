import ollama

LLAMA_MODEL = "llama3.2"

messages: list[dict] = [{
    'role': 'system', 
    'content': '''You are a helpful voice assistant.
                1. Provide extremely concise, direct answers (1-2 sentences max) and aim to provide responses of less than 20 words.
                2. Do NOT use markdown, asterisks (*), bold (**), or special characters.
                3. Do NOT use lists or bullet points. Speak in natural, flowing paragraphs.
                4. Do NOT output code blocks or visual formatting.
                5. If the answer requires a list, describe it verbally (e.g., "First... then... finally...").'''
}]

def ask_llama(text: str) -> str:
    """Sends text to local Llama and prints response"""
    global messages

    messages.append({'role': 'user', 'content': text})
    response = ollama.chat(model=LLAMA_MODEL, messages=messages, keep_alive=-1)
    messages.append({'role': 'assistant', 'content': response['message']['content']})

    if len(messages) > 10:
        # Keep the context window manageable by removing older messages
        messages = [messages[0]] + messages[-9:]
    
    return response['message']['content']