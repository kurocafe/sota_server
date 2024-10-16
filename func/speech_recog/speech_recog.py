import numpy as np
import soundfile as sf
import whisper
from io import BytesIO
import librosa

model = None

def load_model(model_name="medium"):
    global model
    if model is None:
        model = whisper.load_model(model_name)

def open_wav(wav_path: str):
    with open(wav_path, "rb") as f:
        bytes = f.read()
    wav_stream = BytesIO(bytes)
    audio_array, sample_rate = sf.read(wav_stream)
    audio_fp32 = audio_array.astype(np.float32)
    return audio_fp32, sample_rate

def remove_silence(audio, sample_rate, min_silence_duration=0.5, silence_threshold=-25):
    frame_length = int(sample_rate * min_silence_duration)
    hop_length = frame_length // 4

    # 無音部分を検出
    non_silent = librosa.effects.split(
        audio, 
        top_db=-silence_threshold, 
        frame_length=frame_length,
        hop_length=hop_length
    )
    
    # 無音でない部分を結合
    audio_without_silence = []
    for start, end in non_silent:
        audio_without_silence.extend(audio[start:end])
    
    return np.array(audio_without_silence)

def speech_recog(wav_path: str, model_name="medium"):
    global model

    audio_fp32, sample_rate = open_wav(wav_path=wav_path)
    
    audio_without_silence = remove_silence(audio_fp32, sample_rate)
    
    load_model(model_name=model_name)
    result = model.transcribe(audio_without_silence, language="ja", fp16=False)
    return result["text"]
    
if __name__ == "__main__":
    import os
    import torch
    print("cuda:", torch.cuda.is_available())
    path = "./tmp/test.wav"
    if not os.path.exists(path):
        exit()
    print(speech_recog(wav_path=path))
