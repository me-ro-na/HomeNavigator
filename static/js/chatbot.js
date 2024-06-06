document.getElementById('send-button').addEventListener('click', function(event) {
    event.preventDefault();
    sendMessage();
});

document.getElementById('chat-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});

function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (message) {
        const userMessage = document.createElement('div');
        userMessage.className = 'chat-message user';
        userMessage.innerText = message;
        document.getElementById('chat-messages').appendChild(userMessage);
        
        input.value = '';

        // Simulate bot response
        setTimeout(() => {
            const botMessage = document.createElement('div');
            botMessage.className = 'chat-message bot';
            document.getElementById('chat-messages').appendChild(botMessage);
            typeWriter(botMessage, '이것은 봇의 응답입니다.');
        }, 1000);
    }
}

function typeWriter(element, text, i = 0) {
    if (i < text.length) {
        element.innerHTML += text.charAt(i);
        setTimeout(() => typeWriter(element, text, i + 1), 50);
    } else {
        document.getElementById('chat-messages').scrollTop = document.getElementById('chat-messages').scrollHeight;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    let chatHistory = [];

    sendButton.addEventListener('click', function() {
        const message = chatInput.value.trim();
        if (message) {
            addMessageToChat('user', message);
            chatHistory.push({"role": "user", "message": message});
            chatInput.value = '';
            sendMessageToAPI(message);
        }
    });

    chatInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            const message = chatInput.value.trim();
            if (message) {
                addMessageToChat('user', message);
                chatHistory.push({"role": "user", "message": message});
                chatInput.value = '';
                sendMessageToAPI(message);
            }
        }
    });

    function addMessageToChat(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${sender}`;
        messageElement.innerText = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function sendMessageToAPI(message) {
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message, chat_history: chatHistory })
        })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                addMessageToChat('assistant', data.response);
                chatHistory.push({"role": "assistant", "message": data.response});
            } else {
                addMessageToChat('assistant', '응답을 처리하는 중 오류가 발생했습니다.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessageToChat('assistant', '서버와 통신하는 중 오류가 발생했습니다.');
        });
    }
});