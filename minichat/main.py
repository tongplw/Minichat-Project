import os
import database as db

from datetime import datetime
from functools import wraps
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import Flask, session, render_template, request, redirect, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = "123"
socketio = SocketIO(app)

logged_in_users = db.load_users()
channel_list = db.load_channels()
history = db.load_channels_history()

channel_template = """
<li class="{is_active}">
    <div class="d-flex bd-highlight">
        <div class="user_info">
            <span>{channel_name}</span>
        </div>
    </div>
</li>
"""

msg_template = """
<div class="d-flex justify-content-{to_user} ">
    <div class="msg_cotainer{send}" style="max-width: 20em;">
        <b>{username} </b>{text}
    </div>
</div>
<div class="d-flex justify-content-{to_user} timestamp ">
    {timestamp}
</div>
"""

def sync_db():
    global logged_in_users, channel_list, history
    logged_in_users = db.load_users()
    channel_list = db.load_channels()
    history = db.load_channels_history()   

def logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # check that user is logged in
        if "username" in session:
            return func(*args, **kwargs)
        return "Your are not authorized"

    return wrapper


@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("chat"))
    sync_db()
    return render_template("index.html", page_title="Login")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")

    # check that username is not empty
    if not username:
        return "Username is empty"

    # check that username is free
    if username in logged_in_users:
        return "Username is busy"
    
    db.create_user(username)
    db.check_online(username)

    # create session for new user
    session["username"] = username
    logged_in_users.append(username)
    
    return redirect(url_for("chat"))

@app.route("/logout", methods=["POST"])
def logout():
    username = session["username"]

    # delete session username
    session.pop("username", None)
    db.check_offline(username)

    while username in logged_in_users:
        logged_in_users.remove(username)

    return redirect(url_for("index"))

@app.route("/chat")
@logged_in
def chat():
    sync_db()
    if session["username"] not in logged_in_users:
        session.pop("username")
        return redirect(url_for("index"))
    return render_template("chat.html", page_title="Chat", username=session.get("username"))


@socketio.on("create channel")
def create_channel(name):
    n = name["name"]
    n = n.strip()
    if n in channel_list:
        emit("error", "Channel is already exists")
    elif not n:
        emit("error", "Channel name is empty")
    else:
        channel_list.append(n)
        history[n] = []
        data = channel_template.format(is_active="", channel_name=n)
        emit("channel created", data, broadcast=True)

        # add channel into database
        db.create_group(n)


@socketio.on("send message")
def send_message(message):
    # save msg in history
    if "channel" not in session.keys():
        emit("error", "Please join to a channel to send messages")
    elif not message["text"]:
        emit("error", "Paste your message before sending")
    else:
        channel = session.get("channel")
        username = session.get("username")
        history[channel].append((username, message["text"], datetime.now()))


        # send msg for current user
        emit(
            "receive message",
            {
                "text": msg_template.format(
                    to_user="end", 
                    text=message["text"], 
                    send="_send", 
                    username="", 
                    timestamp=datetime.now().strftime("%H:%M"),
                )
            },
        )

        # send msg for other users
        emit(
            "receive message",
            {
                "text": msg_template.format(
                    to_user="start",
                    text=message["text"],
                    send="",
                    username="".join([username, ": "]),
                    timestamp=datetime.now().strftime("%H:%M")
                ),
            },
            room=session.get("channel"),
            include_self=False,
        )

        # save message to database
        db.create_message(message["text"], username, channel)


@socketio.on("connect to channel")
def connect_to_channel(channel):
    name = channel["name"]
    session["channel"] = name
    username = session.get("username")
    join_room(name)
    emit(
        "user has joined",
        f'<span style="color:white;">{username} has joined to {name}</br>',
        room=name,
        include_self=False,
    )


@socketio.on("leave channel")
def leave_channel():
    if "channel" in session.keys():
        leave_room(session.get("channel"))
        emit(
            "user has left",
            f"""<span style="color: white;">{session.get('username')} has left the {session.get('channel')}</span></br>""",
            room=session.get("channel"),
            include_self=False,
        )


@socketio.on("reload channel history")
def reload_channel_history(name):
    # restore chat history
    channel = history[name]
    username = session.get("username")
    channel_history = []
    emit("clear chat")

    if channel:
        for msg in channel:
            if msg[0] == username:
                channel_history.append(
                    msg_template.format(
                        to_user="end", 
                        text=msg[1], 
                        send="_send", 
                        username="",
                        timestamp=msg[2].strftime("%H:%M"),
                    )
                )
            else:
                channel_history.append(
                    msg_template.format(
                        to_user="start",
                        text=msg[1],
                        send="",
                        username="".join([msg[0], ": "]),
                        timestamp=msg[2].strftime("%H:%M"),
                    )
                )
        emit("receive message", {"text": "".join(channel_history)})


@socketio.on("load channels")
def load_channels():
    if channel_list:
        emit(
            "channels loaded",
            [
                channel_template.format(is_active="", channel_name=channel)
                for channel in channel_list
            ],
        )


if __name__ == '__main__':
    print("flask running")
    socketio.run(app, host='0.0.0.0', debug=True)