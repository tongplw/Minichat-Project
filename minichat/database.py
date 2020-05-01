import sqlalchemy
from datetime import datetime, timedelta

DB_URI = "mysql+pymysql://chat:123@chat_db_1:3306/minichat"
db = sqlalchemy.create_engine(DB_URI)

def escape(text):
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "\\'")
    text = text.replace('"', '\\"')
    return text
    
def create_message(message, user_id, group_id):
    message = escape(message)
    user_id = escape(user_id)
    group_id = escape(group_id)
    cmd = f"INSERT INTO minichat.messages (message, user_id, group_id) VALUES ('{message}', '{user_id}', '{group_id}');"
    with db.connect() as conn:
        conn.execute(cmd)

def create_user(name):
    name = escape(name)
    cmd = f"INSERT IGNORE INTO minichat.users (username, is_online, last_login) VALUES ('{name}', 1, CURRENT_TIMESTAMP);"
    with db.connect() as conn:
        conn.execute(cmd)

def create_group(name):
    name = escape(name)
    cmd = f"INSERT INTO minichat.groups (name) VALUES ('{name}');"
    with db.connect() as conn:
        conn.execute(cmd)

def load_channels():
    cmd = f'SELECT * FROM minichat.groups;'
    with db.connect() as conn:
        result = conn.execute(cmd)
        return [i[0] for i in result.fetchall()]

def load_users():
    cmd = f'SELECT username FROM minichat.users WHERE last_login > date_sub(NOW(), interval 1 hour) AND is_online = 1;'
    with db.connect() as conn:
        result = conn.execute(cmd)
        return [i[0] for i in result.fetchall()]

def load_channels_history():
    cmd = f'SELECT * FROM minichat.messages ORDER BY sent_on;'
    with db.connect() as conn:
        result = conn.execute(cmd)
    history = {}
    for channel in load_channels():
        history[str(channel)] = []
    for record in result.fetchall():
        message, username, channel = record[1:4]
        history[str(channel)].append((str(username), str(message)))
    return history

def check_online(username):
    username = escape(username)
    cmd = f"UPDATE minichat.users SET is_online=1, last_login=CURRENT_TIMESTAMP WHERE username='{username}';"
    with db.connect() as conn:
        conn.execute(cmd)

def check_offline(username):
    username = escape(username)
    cmd = f"UPDATE minichat.users SET is_online=0 WHERE username='{username}';"
    with db.connect() as conn:
        conn.execute(cmd)