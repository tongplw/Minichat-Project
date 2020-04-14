from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://root:root@35.247.185.92/message')

cmd = 'INSERT INTO message.urls (cat, url) VALUES '