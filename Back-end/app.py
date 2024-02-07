// app.js
function registerUser() {
    const fullName = document.getElementById('fullName').value;
    const username = document.getElementById('username').value;
    
    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ fullName, username })
    })
    .then(response => {
        if (response.ok) {
            // Hide registration form and show send message form
            document.getElementById('registrationForm').classList.add('hidden');
            document.getElementById('sendMessageForm').classList.remove('hidden');
        } else {
            throw new Error('Failed to register user');
        }
    })
    .catch(error => {
        console.error('Error registering user:', error);
        // Display error message to user
    });
}

function sendMessage() {
    const recipient = document.getElementById('recipient').value;
    const message = document.getElementById('message').value;
    
    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ recipient, message })
    })
    .then(response => {
        if (response.ok) {
            // Message sent successfully, clear form
            document.getElementById('recipient').value = '';
            document.getElementById('message').value = '';
            // Optionally, display success message to user
        } else {
            throw new Error('Failed to send message');
        }
    })
    .catch(error => {
        console.error('Error sending message:', error);
        // Display error message to user
    });
}

// Fetch and display messages when the page loads
document.addEventListener('DOMContentLoaded', () => {
    fetchMessages();
});

function fetchMessages() {
    fetch('/view_messages/username', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const messagesList = document.getElementById('messagesList');
        messagesList.innerHTML = '';
        data.messages.forEach(message => {
            const li = document.createElement('li');
            li.textContent = message;
            messagesList.appendChild(li);
        });
        // Show messages container
        document.getElementById('messagesContainer').classList.remove('hidden');
    })
    .catch(error => {
        console.error('Error fetching messages:', error);
        // Display error message to user
    });
}

