import sqlite3 as sql
import json
from ..db.create_db import create_db

def add_user(user_id, user_name):
    dbname = 'Memory.db'
    conn = sql.connect(dbname)
    cur = conn.cursor()
    # # テーブルが存在するか確認
    # cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='persons'")
    # if cur.fetchone() is None:
    #     create_db()
    try:
        # ユーザーが存在するか確認
        cur.execute('SELECT id FROM persons WHERE id = ?', (user_id,))
        if cur.fetchone() is None:
            # ユーザーが存在しない場合、新規追加
            cur.execute('INSERT INTO persons(id, name) VALUES (?, ?)', (user_id, user_name))
            print(f"User {user_id} added with name {user_name}.")
            conn.commit()
        else:
            # ユーザーが存在する場合、名前を更新
            cur.execute('UPDATE persons SET name = ? WHERE id = ?', (user_name, user_id))
            print(f"User {user_id} updated with new name {user_name}.")
            conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()
        
def add_msg(user_id, message):
    dbname = 'Memory.db'
    conn = sql.connect(dbname)
    cur = conn.cursor()
    cur.execute('SELECT id FROM persons WHERE id = ?', (user_id,))
    if cur.fetchone() is None:
        return None
    
    # messageをdbに追加
    try :
        cur.execute(f'INSERT INTO messages(usr_id, message) values(?, ?)',
                    (user_id, json.dumps(message, ensure_ascii=False)))
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

    
def pull_msg(user_id, num = 10):
    dbname = 'Memory.db'
    conn = sql.connect(dbname)
    cur = conn.cursor()
    message_str = cur.execute(f'SELECT message FROM messages WHERE usr_id={user_id}').fetchall()
    
    try:
        message_json = [json.loads(s[0]) for s in message_str]
        return message_json[-num:]
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        
def pull_user(user_id):
    dbname = 'Memory.db'
    conn = sql.connect(dbname)
    cur = conn.cursor()
    try:
        user_name = cur.execute('SELECT name FROM persons WHERE id = ?', (user_id,)).fetchone()
        if user_name:
            return user_name[0]  # 名前を返す
        else:
            return None  # ユーザーが見つからなかった場合
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()