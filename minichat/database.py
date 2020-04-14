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
    cmd = f'INSERT INTO minichat.message (message, user, group) VALUES ("{message}", "{user_id}", "{group_id}");'
    with db.connect() as conn:
        conn.execute(cmd)

def create_user(name):
    cmd = f'INSERT INTO minichat.users (name) VALUES ("{name}");'
    with db.connect() as conn:
        conn.execute(cmd)

def create_group(name):
    cmd = f'INSERT INTO minichat.groups (name) VALUES ("{name}");'
    with db.connect() as conn:
        conn.execute(cmd)