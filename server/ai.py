import json
import ollama

LLAMA_MODEL = "llama3.2"

messages: list[dict] = [{
    'role': 'system', 
    'content': '''
            You are a Voice Assistant JSON Generator. You control a smart light. 
            You must output ONLY valid JSON. Do not output markdown or plain text.

            Valid Commands:
            - "LED ON" (Turn light on/white)
            - "LED OFF" (Turn light off)
            - "LED R" (Turn light red)
            - "LED G" (Turn light green)
            - "LED B" (Turn light blue)

            Output Format:
            {
            "command": "COMMAND_OR_NONE",
            "content": "SPOKEN_RESPONSE"
            }

            Rules:
            1. "command": Use one of the valid commands above. If no command applies, use "NONE".
            2. "content": The text to speak. Keep it under 20 words. No special chars (*, #). Natural speech only.
            3. If a command is executed, the 'content' should be a brief confirmation (e.g., "Okay, turning it blue.").

            Examples:
            User: "Turn on the light"
            Output: {"command": "LED ON", "content": "Light turned on."}

            User: "Make it red please"
            Output: {"command": "LED R", "content": "Changing color to red."}

            User: "Who is the president of France?"
            Output: {"command": "NONE", "content": "The president of France is Emmanuel Macron."}
            '''
}]

def ask_llama(text: str) -> dict[str, str]:
    """Sends text to local Llama and prints response"""
    global messages

    messages.append({'role': 'user', 'content': text})

    response = ollama.chat(
        model=LLAMA_MODEL,
        messages=messages,
        format='json',
        keep_alive=-1
    )

    json_string = response['message']['content']
    messages.append({"role": "assistant", "content": json_string})

    if len(messages) > 10:
        # Keep the context window manageable by removing older messages
        messages = [messages[0]] + messages[-9:]

    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        print("Error: Llama failed to produce valid JSON.")
        return {"command": "NONE", "content": "I had a system error."}