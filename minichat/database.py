import sqlalchemy

# Cloud SQL
# db = sqlalchemy.create_engine(
#         sqlalchemy.engine.url.URL(
#             drivername="mysql+gaerdmbs",
#             username="root",
#             password="root",
#             database="minichat",
#             query={"unix_socket": "/cloudsql/minichat-274103:asia-southeast1:minichat-database"},
#         ),
#     )

# FOR LOCAL development database w/ docker with nginx as load balancer 
# Pinn choose MySQL haha :)
# from dotenv import load_dotenv
# import os

# load_dotenv()
# print(os.getenv("DB_URL"))# 
DB_URI = "mysql+pymysql://chat:123@chat_db_1:3306/minichat"
print(DB_URI)#
db= sqlalchemy.create_engine(DB_URI)

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
    cmd = f"INSERT INTO minichat.users (username) VALUES ('{name}');"
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