import sqlite3 as sql

dbname = 'Memory.db'
conn = sql.connect(dbname)

def create_db():
    cur = conn.cursor()
    
    # ユーザーを記録するデータベース
    table1 = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="persons"').fetchone()
    if table1 is None:
        cur.execute(
            'CREATE TABLE persons(id INTEGER PRIMARY KEY, name STRING)'
        )
        
    # メッセージを記録するでベータベース
    table2 = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="messages"').fetchone()
    if table2 is None:
        cur.execute(
            'CREATE TABLE messages(id INTEGER PRIMARY KEY AUTOINCREMENT, usr_id INTEGER, message STRING)'
        )
    
    conn.commit()  # 変更を保存
    cur.close()    # カーソルを閉じる

# データベース接続はプログラム終了時に閉じる
# conn.close()

def db_test():
    cur = conn.cursor()
    
    person = cur.execute('SELECT * FROM persons where id = 100').fetchone()
    print(person)
    if person is None :
        cur.execute('INSERT INTO persons(id, name) values(100, "Taro")')
        conn.commit()
    cur.execute('INSERT INTO persons(name) values("Hanako")')
    cur.execute('INSERT INTO persons(name) values("Hiroki")')
    conn.commit()
    
if __name__ == "__main__":
    create_db()
    db_test()
