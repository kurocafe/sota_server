import sqlite3
import asyncio
from rapidfuzz import process
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
ChannelId = int(os.getenv("TEST_CHANNEL"))

# データベース接続（変更なし）
def connect_to_db():
    connection = sqlite3.connect('./func/thesis_func/thesis_database.db')
    return connection

# データベースからすべての論文情報を取得（変更なし）
def fetch_all_theses():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('SELECT title, author, year, purpose, method, results, conclusion, keywords, file_path FROM theses')
    rows = cursor.fetchall()
    connection.close()
    return rows

# キーワードで検索（変更なし）
def search_by_keyword(keyword, theses, limit=5):
    titles = [f"{row[0]} (Keywords: {row[3]})" for row in theses]
    results = process.extract(keyword, titles, limit=limit)
    return results

# 既存の関数はそのまま
# bot.is_ready = False

def send_results_to_discord(result, bot_token, theses, channel_id=0, user_id=0):
    """
    検索結果をDiscordチャンネルに送信
    
    :param results: 検索結果のリスト
    :param bot_token: Discordボットのトークン
    :param channel_id: 送信先のチャンネルID
    """
    def on_ready():
        if user_id != 0:
            print(f"ゆーざーあいでぃー：{user_id}")
            # user = bot.get_user(user_id)
            # print(f"log: {user}")
            for match, score, idx in result:
                try:
                    
                    title, author, year, purpose, method, results, conclusion, keywords, file_path = theses[idx]
                    
                    # メッセージを作成
                    message = f"""
📄 検索結果:
スコア: {score:.2f}%
## タイトル 
> **{title}**
## 著者
> {author}
## 発表年
> {year}
## 目的
> {purpose}
## 方法 
> {method}
## 結果
> {results}
## 結論 
> **{conclusion}**
## キーワード 
> {keywords}
## ファイルパス
> {file_path}
"""
                    import subprocess

                    subprocess.run(['/mnt/data1/home/nakaura/anaconda3/envs/llama/bin/python', 'send_bot.py', message, str(user_id), file_path])
                except Exception as e:
                    print(f"ERROR: {e}")
                    continue
    
    on_ready()
    
def search_from_db(keyword, user_id):
    try:
        theses = fetch_all_theses()
        result = search_by_keyword(keyword, theses, limit=3)
        
        # コンソールに表示
        for match, score, idx in result:
            title, author, year, purpose, method, results, conclusion, keywords, file_path = theses[idx]
            print(f"\nスコア: {score:.2f}%")
            print(f"タイトル: {title}")
            # ... 他の情報表示
        
        send_results_to_discord(result, TOKEN, theses, user_id=user_id)
    except Exception as e:
        print(f"その他エラー：{e}")
        raise
    

# メイン関数を修正
def main():
    keyword = input("検索したいキーワードを入力してください: ")
    theses = fetch_all_theses()
    
    print(f"\nキーワード '{keyword}' に近い論文:")
    result = search_by_keyword(keyword, theses, limit=3)
    
    # コンソールに表示
    for match, score, idx in result:
        title, author, year, purpose, method, results, conclusion, keywords, file_path = theses[idx]
        print(f"\nスコア: {score:.2f}%")
        print(f"タイトル: {title}")
        # ... 他の情報表示
    
    # Discordに送信するかユーザーに確認
    send_to_discord = input("これらの結果をDiscordに送信しますか？ (y/n): ")
    if send_to_discord.lower() == 'y':
        # bot_token = input("Discordボットのトークンを入力: ")
        bot_token = TOKEN
        # channel_id = int(input("送信先チャンネルIDを入力: "))
        channel_id = ChannelId
        send_results_to_discord(result, bot_token, theses, channel_id=0, user_id=821611534961606706)

if __name__ == "__main__":
    main()