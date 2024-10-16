from style_bert_vits2.nlp import bert_models
from style_bert_vits2.constants import Languages
from style_bert_vits2.tts_model import TTSModel

from torch.nn.utils.parametrizations import weight_norm

from pathlib import Path
from huggingface_hub import hf_hub_download

# from IPython.display import Audio, display
import soundfile as sf

PATH = "./tmp/output.wav"

chara_dict = {0: {"name":"miyako", "model_file": "miyako/miyako_e100_s13400.safetensors"},
              1: {"name":"tsukuyomi_test", "model_file": "tsukuyomi_test/tsukuyomi_test_e100_s10400.safetensors"},
              2: {"name":"Yuuka", "model_file": "Yuuka/Yuuka_e100_s14400.safetensors"},
              3: {"name":"Asuna", "model_file": "Asuna/Asuna_e100_s9700.safetensors"}
}

model_dict = {
    
}


def load_models()-> None: 
    bert_models.load_model(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")
    bert_models.load_tokenizer(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")

# model_file = "jvnv-F1-jp/jvnv-F1-jp_e160_s14000.safetensors"
# config_file = "jvnv-F1-jp/config.json"
# style_file = "jvnv-F1-jp/style_vectors.npy"

# for file in [model_file, config_file, style_file]:
#     print(file)
#     hf_hub_download("litagin/style_bert_vits2_jvnv", file, local_dir="model_assets")
def sbt2_voice(text :str, chara_id :int = 0)-> str:
    load_models()
    # model_file = "tsukuyomi_test/tsukuyomi_test_e100_s10400.safetensors"
    # config_file = "tsukuyomi_test/config.json"
    # style_file = "tsukuyomi_test/style_vectors.npy"
    
    if chara_id not in model_dict:        
        chara = chara_dict[chara_id]
        name = chara["name"]
        model_file = chara["model_file"]
        config_file = f"{name}/config.json"
        style_file = f"{name}/style_vectors.npy"
        
        assets_root = Path("model_assets")

        model = TTSModel(
            model_path=assets_root / model_file,
            config_path=assets_root / config_file,
            style_vec_path=assets_root / style_file,
            device="cuda",
        )
        model_dict[chara_id] = model
    
    model = model_dict[chara_id]

    sr, audio = model.infer(text=text)
    sf.write(PATH, audio, sr)
    # display(Audio(PATH))
    
    return PATH

if __name__ == '__main__':
    sbt2_voice("録音テストを始めるよ")
