import sqlite3 as sql

def add_user(user_id, user_name):
    dbname = 'Memory.db'
    conn = sql.connect(dbname)
    cur = conn.cursor()
    # ユーザーが存在するか確認
    cur.execute('SELECT id FROM persons WHERE id = ?', (user_id,))
    if cur.fetchone() is None:
        # ユーザーが存在しない場合、新規追加
        cur.execute('INSERT INTO persons(id, name) VALUES (?, ?)', (user_id, user_name))
        print(f"User {user_id} added with name {user_name}.")
    else:
        # ユーザーが存在する場合、名前を更新
        cur.execute('UPDATE persons SET name = ? WHERE id = ?', (user_name, user_id))
        print(f"User {user_id} updated with new name {user_name}.")
        conn.commit()
        
        
def add_msg():
    dbname = 'Memory.db'
    conn = sql.connect(dbname)
    cur = conn.cursor()
    