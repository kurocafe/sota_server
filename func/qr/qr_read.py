import pyzbar.pyzbar as pyzbar
from PIL import Image

def decode_qr_code(image_path) -> int:
    try :
        qr = pyzbar.decode(Image.open(image_path))
        print(qr)
        return qr[0].data.decode('utf-8')
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    decode_qr_code('/mnt/data1/home/nakaura/VSCode/llama/tmp/qr.png')