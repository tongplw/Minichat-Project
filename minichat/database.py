import sqlalchemy
import datetime
from datetime import date, timedelta


db = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username="root",
            password="root",
            database="minichat",
            query={"unix_socket": "/cloudsql/minichat-274103:asia-southeast1:minichat-database"},
        ),
    )

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
    cmd = f"INSERT INTO minichat.users (username, is_online, last_login) VALUES ('{name}', 1, CURRENT_TIMESTAMP);"
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
    cmd = f'SELECT * FROM minichat.users;'
    with db.connect() as conn:
        result = conn.execute(cmd)
        return result.fetchall()

def load_usernames():
    return [i[0] for i in load_users()]

def load_channels_history():
    cmd = f'SELECT * FROM minichat.messages ORDER BY sent_on;'
    with db.connect() as conn:
        result = conn.execute(cmd)
    history = {}
    for channel in load_channels():
        history[channel] = []
    for record in result.fetchall():
        message, username, channel = record[1:4]
        history[channel].append((username, message))
    return history

def can_login(username):
    username = escape(username)
    cmd = f"SELECT is_online, last_login FROM minichat.users WHERE username='{username}';"
    with db.connect() as conn:
        result = conn.execute(cmd)
    is_online, last_login = result.fetchone()
    if last_login < datetime.datetime.now() - timedelta(hours=1) or not is_online:
        return True
    return False

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