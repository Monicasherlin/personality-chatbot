let currentPersonality = "sweet";

function setPersonality(type) {
    currentPersonality = type;

    document.getElementById("sweetBtn").classList.remove("active");
    document.getElementById("rudeBtn").classList.remove("active");

    if (type === "sweet") {
        document.getElementById("sweetBtn").classList.add("active");
    } else {
        document.getElementById("rudeBtn").classList.add("active");
    }
}

function sendMessage() {
    let input = document.getElementById("message-input");
    let message = input.value;

    if (!message) return;

    addMessage(message, "user-message");

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: message,
            personality: currentPersonality
        })
    })
    .then(response => response.json())
    .then(data => {
        addMessage(data.reply, "ai-message");
    });

    input.value = "";
}

function addMessage(text, className) {
    let chatBox = document.getElementById("chat-box");
    let messageDiv = document.createElement("div");

    messageDiv.classList.add("message", className);
    messageDiv.innerText = text;

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}