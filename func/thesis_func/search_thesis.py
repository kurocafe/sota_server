import sqlite3
from rapidfuzz import process

# データベース接続
def connect_to_db():
    connection = sqlite3.connect('thesis_database.db')
    return connection

# データベースからすべての論文情報を取得
def fetch_all_theses():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('SELECT title, author, year, keywords, file_path FROM theses')
    rows = cursor.fetchall()
    connection.close()
    return rows

# キーワードで検索
def search_by_keyword(keyword, theses, limit=5):
    # 論文タイトルやキーワードの中から近いものを探す
    titles = [f"{row[0]} (Keywords: {row[3]})" for row in theses]
    results = process.extract(keyword, titles, limit=limit)
    return results

# 検索システム
def main():
    keyword = input("検索したいキーワードを入力してください: ")
    theses = fetch_all_theses()
    
    print(f"\nキーワード '{keyword}' に近い論文:")
    results = search_by_keyword(keyword, theses)
    for match, score, idx in results:
        title, author, year, keywords, file_path = theses[idx]
        print(f"\nスコア: {score:.2f}%")  # スコアを小数点以下2桁で表示
        print(f"タイトル: {title}")
        print(f"著者: {author}, 発表年: {year}")
        print(f"キーワード: {keywords}")
        print(f"ファイルパス: {file_path}")
        print(f"せっかくなので、詳細: {match}")

if __name__ == "__main__":
    main()
