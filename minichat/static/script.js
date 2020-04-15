// then page is loaded
document.addEventListener("DOMContentLoaded", () => {

    // connect to web socket 
    var socket = io.connect(location.protocol + "//" + document.domain + ":" + location.port);

    // when connected, configure buttons
    socket.on('connect', () => {

        // configure Create channel button
        createChannelBtn = document.querySelector(".input-group-prepend");
        createChannelBtn.onclick = () => {
            // take new channel name from input field
            const newChannelName = document.querySelector(".search");
            socket.emit("create channel", { "name": newChannelName.value });
            newChannelName.value = "";


        };
        
        // configure Send button
        sendMessageBtn = document.querySelector(".input-group-append");
        sendMessageBtn.onclick = () => {
            //take message
            const text = document.querySelector(".type_msg");
            socket.emit("send message", { "text": text.value });
            text.value = "";
        };
    
        textArea = document.querySelector(".type_msg");
        textArea.onkeypress = (event) => {
            if (event.keyCode === 13) { 
                event.preventDefault();
                sendMessageBtn.click(); 
            }
        };

        // load channels
        socket.emit("load channels");

    });

    // create channel
    socket.on("channel created", data => {
        // get channel list
        createChannel(data);
    });

    // channels loaded
    socket.on("channels loaded", channel_list => {
        channel_list.forEach(createChannel)
    });

    function createChannel(data) {
        console.log(data);
        const channelList = document.querySelector(".contacts");
        // add new channel to the list
        channelList.innerHTML += data;

        // add onmouseover and onmouseout actions to channles
        const liList = document.querySelectorAll(".user_info").forEach(div => {
            const li = div.parentNode.parentNode;
            if (!li.onmouseover) {
                li.onmouseover = () => {
                    li.className = "active";
                };
            };
            if (!li.onmouseout) {
                li.onmouseout = () => {
                    li.className = "";
                };
            };
            if (!div.parentNode.onclick) {
                div.parentNode.onclick = () => {
                    const chatHeader = document.querySelector(".msg_head > .bd-highlight");
                    const channel = div.querySelector("span").textContent;
                    // leave current channel
                    socket.emit("leave channel")
                    // connect to channel
                    socket.emit("connect to channel", { "name": channel });
                    socket.emit("reload channel history", channel);
                    // change chat header to selected channel
                    chatHeader.innerHTML = channel;
                    const msgBody = document.querySelector(".msg_card_body");
                    msgBody.scrollTop = msgBody.scrollHeight;
                };
            };
        });
    };

    // receive message
    socket.on("receive message", msg => {
        // get message window
        windowMessages = document.querySelector(".msg_card_body");
        windowMessages.innerHTML += msg.text;
        windowMessages.scrollTop = windowMessages.scrollHeight + windowMessages.clientHeight;
    });

    // user join to a channel
    socket.on("user has joined", msg => {
        windowMessages = document.querySelector(".msg_card_body");
        windowMessages.innerHTML += msg;
    });

    // user leave a channel
    socket.on("user has left", msg => {
        windowMessages = document.querySelector(".msg_card_body");
        windowMessages.innerHTML += msg;
    });

    // clear chat history
    socket.on("clear chat", () => {
        windowMessages = document.querySelector(".msg_card_body");
        windowMessages.innerHTML = "";
    });

    // in case of error
    socket.on("error", data => {
        alert(data);
    });

    return false;
});
