import qrcode
usr_id = 821611534961606706


def qr_generate(usr_id: int):
    qr_str = usr_id
    qr_path = "./qr.png"
    
    # QRCodeオブジェクトを作成する
    qr = qrcode.QRCode(
        version=None, # QRコードのバージョン (1~40)
        error_correction=qrcode.constants.ERROR_CORRECT_H, # 誤り訂正レベル (L：約7%,M：約15%,Q:約25%,H:約30%)
        box_size=15, # 1セルのサイズ（ピクセル）(デフォルト10)
        border=2, # 白マージンのサイズ（セル数）(デフォルト4)
    )
    
    # データを与える
    qr.add_data(qr_str)
    
    # QRコードをエンコードする
    qr.make(fit=True)
    
    # QR画像を出力する
    img = qr.make_image()
    
    # QR画像を保存する
    img.save(qr_path)


if __name__ == '__main__':
    # qr_str = "https://www.google.co.jp/"
    # サーバーからOKもらうまで送り続ける
    qr_str = usr_id
    qr_file_name = "qr_test.png"
    
    # QRCodeオブジェクトを作成する
    qr = qrcode.QRCode(
        version=None, # QRコードのバージョン (1~40)
        error_correction=qrcode.constants.ERROR_CORRECT_H, # 誤り訂正レベル (L：約7%,M：約15%,Q:約25%,H:約30%)
        box_size=15, # 1セルのサイズ（ピクセル）(デフォルト10)
        border=2, # 白マージンのサイズ（セル数）(デフォルト4)
    )
    
    # データを与える
    qr.add_data(qr_str)
    
    # QRコードをエンコードする
    qr.make(fit=True)
    
    # QR画像を出力する
    img = qr.make_image()
    
    # QR画像を保存する
    img.save(qr_file_name)