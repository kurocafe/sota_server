import requests

url = 'https://example.com/get_file'
response = requests.get(url)

if response.status_code == 200:
    # ファイルの内容を取得
    file_content = response.content
    
    # ファイルを保存
    with open('downloaded_file.txt', 'wb') as f:
        f.write(file_content)
    print('File downloaded successfully')
else:
    print('File download failed')