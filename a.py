import sqlalchemy

# db = sqlalchemy.create_engine(
#     sqlalchemy.engine.url.URL(
#         drivername='mysql+pymysql',
#         username='root',
#         password='root',
#         database='minichat',
#         query={
#             'unix_socket': '/cloudsql/minichat-274103:asia-southeast1:minichat-database'
#         }
#     ),
#     pool_size=1,
#     max_overflow=0,
# )

db = sqlalchemy.create_engine('mysql+pymysql://root:root@127.0.0.1/minichat')

cmd = 'INSERT INTO minichat.dummy (id) VALUES (1);'
with db.connect() as conn:
    result = conn.execute(cmd)

print(result)