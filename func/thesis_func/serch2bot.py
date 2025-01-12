import sqlite3
from rapidfuzz import process
import discord  # Discord用のライブラリ
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
ChannelId = int(os.getenv("TEST_CHANNEL"))

# Discord ボットの設定
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# データベース接続（変更なし）
def connect_to_db():
    connection = sqlite3.connect('thesis_database.db')
    return connection

# データベースからすべての論文情報を取得（変更なし）
def fetch_all_theses():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('SELECT title, author, year, keywords, file_path FROM theses')
    rows = cursor.fetchall()
    connection.close()
    return rows

# キーワードで検索（変更なし）
def search_by_keyword(keyword, theses, limit=5):
    titles = [f"{row[0]} (Keywords: {row[3]})" for row in theses]
    results = process.extract(keyword, titles, limit=limit)
    return results

# 既存の関数はそのまま

def send_results_to_discord(results, bot_token, channel_id, theses):
    """
    検索結果をDiscordチャンネルに送信
    
    :param results: 検索結果のリスト
    :param bot_token: Discordボットのトークン
    :param channel_id: 送信先のチャンネルID
    """
    

    @bot.event
    async def on_ready():
        channel = bot.get_channel(channel_id)
        print(f"log: {channel}")
        for match, score, idx in results:
            title, author, year, keywords, file_path = theses[idx]
            
            # メッセージを作成
            message = f"""
📄 検索結果:
スコア: {score:.2f}%
タイトル: {title}
著者: {author}
発表年: {year}
キーワード: {keywords}
ファイルパス: {file_path}
"""
            await channel.send(message)
            
            # ファイルがあれば添付
            if file_path:
                try:
                    await channel.send(file=discord.File(file_path))
                except Exception as e:
                    await channel.send(f"ファイル送信エラー: {e}")
        
        await bot.close()

    bot.run(bot_token)

# メイン関数を修正
def main():
    keyword = input("検索したいキーワードを入力してください: ")
    theses = fetch_all_theses()
    
    print(f"\nキーワード '{keyword}' に近い論文:")
    results = search_by_keyword(keyword, theses)
    
    # コンソールに表示
    for match, score, idx in results:
        title, author, year, keywords, file_path = theses[idx]
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
        send_results_to_discord(results, bot_token, channel_id, theses)

if __name__ == "__main__":
    main()