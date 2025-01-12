import os
import pdfplumber
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# 環境変数からAPIキーをロード
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# データベースとテーブルを初期化
def initialize_database():
    connection = sqlite3.connect('thesis_database.db')
    cursor = connection.cursor()
    # テーブルが存在しない場合は作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS theses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        year INTEGER,
        purpose TEXT,
        method TEXT,
        results TEXT,
        conclusion TEXT,
        keywords TEXT,
        file_path TEXT UNIQUE
    )
    ''')
    connection.commit()
    connection.close()

# ファイルリストを取得
def list_files(base_dir):
    thesis_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            thesis_files.append(os.path.join(root, file))
    return thesis_files

# PDFからテキストを抽出
def extract_text_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None

# フォーマットに沿った要約を生成
def summarize_text(text):
    prompt = f"""
以下の論文を日本語で要約し、指定されたフォーマットに従って出力してください。

フォーマット:
1. タイトル: [論文のタイトル]
2. 著者と発表年: [著者名, 発表年]
3. 目的: [研究の目的を1-2文で]
4. 方法: [研究手法やアプローチを1-2文で]
5. 結果: [主要な結果を簡潔に]
6. 結論と意義: [結論とその意義を簡潔に]
7. キーワード: [関連するキーワードを3～5個]

論文内容:
{text}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an academic assistant that summarizes research papers."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return None

# データベースに保存
def save_to_db(connection, title, author, year, purpose, method, results, conclusion, keywords, file_path):
    cursor = connection.cursor()
    cursor.execute('''
    INSERT INTO theses (title, author, year, purpose, method, results, conclusion, keywords, file_path)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, author, year, purpose, method, results, conclusion, keywords, file_path))
    connection.commit()

# 要約を解析してデータベースに保存
def parse_and_save_summary(connection, summary, file_path):
    lines = summary.split("\n")
    try:
        title = lines[0].split(":")[1].strip() if len(lines[0].split(":")) > 1 else "タイトル不明"
        author_year = lines[1].split(":")[1].strip() if len(lines[1].split(":")) > 1 else "著者不明"
        purpose = lines[2].split(":")[1].strip() if len(lines[2].split(":")) > 1 else "目的不明"
        method = lines[3].split(":")[1].strip() if len(lines[3].split(":")) > 1 else "方法不明"
        results = lines[4].split(":")[1].strip() if len(lines[4].split(":")) > 1 else "結果不明"
        conclusion = lines[5].split(":")[1].strip() if len(lines[5].split(":")) > 1 else "結論不明"
        keywords = lines[6].split(":")[1].strip() if len(lines[6].split(":")) > 1 else "キーワード不明"
    except IndexError as e:
        print(f"Error parsing summary: {e}")
        return

    author, year = (author_year.split(",") if author_year and "," in author_year else (author_year, None))

    save_to_db(connection, title, author, year, purpose, method, results, conclusion, keywords, file_path)

# ファイルを処理
def process_file(file_path):
    # PDFファイルのみ処理する
    if not file_path.endswith(".pdf"):
        print(f"Skipping {file_path}, not a PDF file.")
        return
    
    connection = sqlite3.connect('thesis_database.db')  # スレッドごとに新しい接続を作成
    cursor = connection.cursor()
    
    # すでに要約されているか確認
    cursor.execute('SELECT 1 FROM theses WHERE file_path = ?', (file_path,))
    if cursor.fetchone():
        print(f"Skipping {file_path}, already summarized.")
        connection.close()
        return

    print(f"Processing {file_path}...")
    text = extract_text_from_pdf(file_path)
    if text:
        summary = summarize_text(text[:4000])  # トークン制限を考慮
        if summary:
            parse_and_save_summary(connection, summary, file_path)
            print(f"Summary saved to database for {file_path}")
    
    connection.close()  # 接続を閉じる

# メイン処理

# メイン処理の最初にデータベースを初期化
initialize_database()

base_dir = "thesisDB/"
files = list_files(base_dir)

with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(process_file, files)
