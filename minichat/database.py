import sqlalchemy

DB_URI = "mysql+pymysql://chat:123@chat_db_1:3306/minichat"
db = sqlalchemy.create_engine(DB_URI)

def escape(text):
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "\\'")
    text = text.replace('"', '\\"')
    text = text.replace(';', '\\;')
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

def join_channel(username, group_name):
    username = escape(username)
    group_name = escape(group_name)
    cmd = f"INSERT INTO minichat.group_user (group, user) VALUES ('{group_name}', '{username}');"
    with db.connect() as conn:
        conn.execute(cmd)

def leave_channel(username, channel_name):
    username = escape(username)
    group_name = escape(group_name)
    cmd = f"DELETE FROM minichat.group_user WHERE user = '{username}' AND group = '{group_name}';"
    with db.connect() as conn:
        conn.execute(cmd)

def load_channels():
    cmd1 = f'SELECT * FROM minichat.groups;'
    cmd2 = f'SELECT * FROM minichat.group_user;'
    with db.connect() as conn:
        result = conn.execute(cmd1)
        out = {}
        for i in result.fetchall():
            out[i[0]] = []
        result = conn.execute(cmd2)
        for group, user in result.fetchall():
            out[group] += [user]
        return out

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
        message, username, channel, timstamp = record[1:5]
        history[str(channel)].append((str(username), str(message), timstamp))
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