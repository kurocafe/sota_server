import pyzbar.pyzbar as pyzbar
from PIL import Image

qr = pyzbar.decode(Image.open('test.jpg'))
print(qr)
print(qr[0].data)
print(qr[0].data.decode('utf-8'))
