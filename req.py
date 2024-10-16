import requests

url = "http://150.59.20.116:8000"
data = {
    "user_message": "こんにちは！"
}

response = requests.post(url + "/generate", json=data)

print(response.json())

message = response.json().get('response')
print(message)

response2 = requests.get(url + "/tts", message)
file_path = "output.wav"
with open(file_path, "wb") as f:
    print("write")
    print(response2.content)
    f.write(response2)