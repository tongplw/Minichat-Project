import os
from functools import wraps

from flask import Flask, session, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "123"
socketio = SocketIO(app)


logged_in_users = []
channel_list = []
history = {}
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
<div class="d-flex justify-content-{to_user} mb-4">
<div class="msg_cotainer{send}">
<b>{username} </b>{text}
</div>
</div>
"""


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

    # create session for new user
    session["username"] = username
    print(session)
    logged_in_users.append(username)

    return redirect(url_for("chat"))


@app.route("/chat")
@logged_in
def chat():
    return render_template(
        "chat.html", page_title="Chat", username=session.get("username")
    )


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
        history[channel].append((username, message["text"]))

        # send msg for current user
        emit(
            "receive message",
            {
                "text": msg_template.format(
                    to_user="end", text=message["text"], send="_send", username="",
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
                ),
            },
            room=session.get("channel"),
            include_self=False,
        )


@socketio.on("connect to channel")
def connect_to_channel(channel):
    name = channel["name"]
    session["channel"] = name
    username = session.get("username")
    join_room(name)
    emit(
        "user has joined",
        f"{username} has joined to {name}</br>",
        room=name,
        include_self=False,
    )


@socketio.on("leave channel")
def leave_channel():
    if "channel" in session.keys():
        leave_room(session.get("channel"))
        emit(
            "user has left",
            f"{session.get('username')} has left the {session.get('channel')}</br>",
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
                        to_user="end", text=msg[1], send="_send", username="",
                    )
                )
            else:
                channel_history.append(
                    msg_template.format(
                        to_user="start",
                        text=msg[1],
                        send="",
                        username="".join([msg[0], ": "]),
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


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
