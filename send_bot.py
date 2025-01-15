import discord
import sys
from discord.ext import commands
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
TOKEN = os.getenv("TOKEN")
ChannelId = int(os.getenv("TEST_CHANNEL"))

# Discord ボットの設定
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


# Bot起動
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# メイン関数（引数からメッセージ、user_id、file_pathを取得して送信）
def main():
    if len(sys.argv) < 3:
        print("メッセージ、user_id、またはfile_pathが指定されていません。")
        sys.exit(1)

    message = sys.argv[1]
    user_id = int(sys.argv[2])
    file_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    # メッセージ送信関数
    @bot.event
    async def on_ready():
        # Botが起動していることを確認
        await bot.wait_until_ready()
        
        if user_id:
            user = await bot.fetch_user(user_id)
            if user:
                await user.send(message)
                if file_path:
                    try:
                        await user.send(file=discord.File(f"./func/thesis_func/{file_path}"))
                    except Exception as e:
                        await user.send(f"ファイル送信エラー: {e}")
            else:
                print(f"ユーザーID {user_id} が見つかりませんでした。")
        else:
            # user_idが指定されていない場合はチャンネルにメッセージを送信
            channel = bot.get_channel(ChannelId)
            if channel:
                await channel.send(message)
                if file_path:
                    try:
                        await channel.send(file=discord.File(f"./func/thesis_func/{file_path}"))
                    except Exception as e:
                        await channel.send(f"ファイル送信エラー: {e}")
            else:
                print("チャンネルが見つかりませんでした。")
        
        await bot.close()
    # メッセージ送信
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
