window.onload = () => {
    var recommender = new Recommender();
    var classifier = new SentimentClassifier();
    chatbot = new Chatbot(recommender, classifier);
    var input = document.getElementById("chat-input");
    displayMessage("bot", chatbot.greet);

    // Execute a function when the user releases a key on the keyboard
    input.addEventListener("keyup", async function(event) {
        // Number 13 is the "Enter" key on the keyboard
        if (event.keyCode === 13 && chatbot.ready) {
            chatbot.ready = false;
            text = processText(input);
            await botResponse(text);
            chatbot.ready = true;
        }
    }); 
};

function processText(input) {
    //display user input to chat
    var text = input.value;
    text = text.replace(/(\r\n|\n|\r)/gm, "");
    displayMessage("client", text);
    input.value = "";
    return text;
}

async function botResponse(text) {
    //display bot response to text
    var responseText = await chatbot.chat(text);
    displayMessage("bot", responseText);
}

function displayMessage(id, text) {
    //add new message(s) to chat history
    if (typeof text === 'string' || text instanceof String) {
        var messages = [text];
    } else {
        var messages = text;
    }
    for (const message of messages) {
        if (id==="client") {
            var html_string = '<div class="d-flex flex-row justify-content-end p-3"><div class="bg-white mr-2 p-3"><span class="text-muted">' + message + '</span></div>'; 
        } else {
            var html_string = '<div class="d-flex flex-row p-3"> <img src="https://img.icons8.com/nolan/64/bot.png" width="30" height="30"> <div class="chat ml-2 p-3">' + message + '</div></div>';
        }
        //create div for html
        var wrapper= document.createElement('div');
        wrapper.innerHTML = html_string; 
        var div = wrapper.firstChild;
        var messages = document.getElementById("messages");
        messages.appendChild(div);
        div.scrollIntoView(false);
    };
}
