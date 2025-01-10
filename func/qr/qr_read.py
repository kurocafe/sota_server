import pyzbar.pyzbar as pyzbar
from PIL import Image
import traceback
import os
import cv2
import numpy as np
from func.db.add_db import pull_user


# def decode_qr_code(image_path) -> str:
#     if not os.path.exists(image_path):
#         print(f"エラー: ファイル {image_path} が存在しません。")
#         return None

#     try:
#         with Image.open(image_path) as img:
#             qr = pyzbar.decode(img)
#             print(qr)  # デバッグ用
            
#             if qr:
#                 return qr[0].data.decode('utf-8')
#             else:
#                 print("画像内にQRコードが検出されませんでした。")
#                 return None
#     except Exception as e:
#         print(f"画像処理中にエラーが発生しました:")
#         traceback.print_exc()
#         return None


def preprocess_image(image_path):
    """
    画像を前処理してノイズを除去し、コントラストを調整する
    """
    # OpenCVで画像を読み込む
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # ノイズ除去 (Gaussian Blur)
    img = cv2.GaussianBlur(img, (5, 5), 0)
    
    return img

def decode_qr_code(image_path) -> str:
    if not os.path.exists(image_path):
        print(f"エラー: ファイル {image_path} が存在しません。")
        return None

    try:
        # 画像を前処理
        preprocessed_img = preprocess_image(image_path)

        # PIL形式に変換 (PyzbarがPillow画像を受け付けるため)
        pil_image = Image.fromarray(preprocessed_img)
        pil_image.save('./cv.jpg')

        # QRコードをデコード
        decoded_objects = pyzbar.decode(pil_image)

        # 結果を出力
        if decoded_objects:
            for obj in decoded_objects:
                print(f"QRコードの内容: {obj.data.decode('utf-8')}")
                user_id = obj.data.decode('utf-8')
                # pull_user(user_id)
                # return obj.data.decode('utf-8')
                return user_id 
        else:
            print("QRコードが検出されませんでした。")
            return None
    except Exception as e:
        print(f"画像処理中にエラーが発生しました:")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    decode_qr_code("/mnt/data1/home/nakaura/VSCode/llama/sota_server/tmp/qr_test.png")