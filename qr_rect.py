from pyzbar.pyzbar import decode
from PIL import Image
import cv2
import numpy as np
import os

def preprocess_image(image_path):
    """
    画像を前処理してノイズを除去し、コントラストを調整する
    """
    # OpenCVで画像を読み込む
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # ノイズ除去 (Gaussian Blur)
    img = cv2.GaussianBlur(img, (5, 5), 0)
    
    return img

def decode_qr_code(image_path):
    """
    QRコードを読み取る関数
    """
    # 画像を前処理
    preprocessed_img = preprocess_image(image_path)

    # PIL形式に変換 (PyzbarがPillow画像を受け付けるため)
    pil_image = Image.fromarray(preprocessed_img)
    pil_image.save('./cv.jpg')

    # QRコードをデコード
    decoded_objects = decode(pil_image)

    # 結果を出力
    if decoded_objects:
        for obj in decoded_objects:
            print(f"QRコードの内容: {obj.data.decode('utf-8')}")
    else:
        print("QRコードが検出されませんでした。")

# 実行
image_path = './tmp/qr.jpg'  # 読み取るQRコード画像のパス
print(os.path.exists(image_path))
decode_qr_code(image_path)