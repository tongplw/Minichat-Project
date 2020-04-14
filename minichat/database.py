import sqlalchemy


db = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username="root",
            password="root",
            database="minichat",
            query={"unix_socket": "/cloudsql/minichat-274103:asia-southeast1:minichat-database"},
        ),
    )

def create_message(message, user_id, group_id):
    cmd = f'INSERT INTO minichat.messages (message, user_id, group_id) VALUES (`{message}`, `{user_id}`, `{group_id}`);'
    with db.connect() as conn:
        conn.execute(cmd)

def create_user(name):
    cmd = f'INSERT INTO minichat.users (username) VALUES (`{name}`);'
    with db.connect() as conn:
        conn.execute(cmd)

def create_group(name):
    cmd = f'INSERT INTO minichat.groups (name) VALUES (`{name}`);'
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
        return [i[0] for i in result.fetchall()]

def load_channels_history():
    cmd = f'SELECT * FROM minichat.message;'
    with db.connect() as conn:
        result = conn.execute(cmd)
        
        history = {}
        for record in result.fetchall():
            message, username, channel = record[1:4]
            if channel not in history:
                history[channel] = []
            history[channel].append((username, message))
        return history