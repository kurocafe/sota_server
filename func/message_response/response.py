import ollama

from ctypes import *
model_file='''
FROM ./Llama-3-ELYZA-JP-8B-q4_k_m.gguf
SYSTEM あなたは優しいおしとやかな女性です。描写はいらないです。セリフだけ送ってください。
TEMPLATE """{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>

{{ .Response }}<|eot_id|>"""
PARAMETER stop "<|start_header_id|>"
PARAMETER stop "<|end_header_id|>"
PARAMETER stop "<|eot_id|>"
PARAMETER stop "<|reserved_special_token"
'''


def load_model(model_file):
    print('OLLAMA')
    # createしたらどっかに保存されるので2回目以降は作らなくてもいい
    ollama.create(model='llama3_soft', modelfile=model_file)

    
def create_text(messages: list, text2) -> str:
    print(ollama.show(model="llama3_soft"))
    usr_message = {'role': 'user', 'content': text2}
    messages.append(usr_message)
    if 40 < len(messages):
        messages.pop(1)
    print(messages)
    response = ollama.chat(model='llama3_soft', messages=messages)
    text = response['message']['content']
    new_message = {'role': 'assistant', 'content': text}
    if 10 < len(messages):
        messages.pop(1)
    messages.append(new_message)
    
    return text

if __name__ == "__main__":
    load_model(model_file=model_file)
    print(create_text([], text2="ハローワーク行け"))