chat_input_html ="""
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Custom Chat Input</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>

    <div class="chat-container">
        <input type="text" class="chat-input" placeholder="Type a message..." id="chat-input">
        <button class="icon-btn" id="toggle-icon">
            <i class="fas fa-microphone"></i>
        </button>
    </div>

    <div class="recorder_wrapper">
        <div class="recorder">
            <button class="record_btn" id="button"></button>
            <p id="msg_box"></p>
        </div>
    </div>
    <style>
     @import 'https://fonts.googleapis.com/css2?family=Roboto:wght@300&display=swap';

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Roboto', sans-serif;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: flex-end;
 
 

    backdrop-filter: blur(1px);
}

.chat-container {
    backdrop-filter: blur(12px);
    background: rgba(255, 255, 255, 0.1);
    border-radius: 30px;
    padding: 10px;
    display: flex;
    position: fixed;
    align-items: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    width: 95%;
    height: 60px;
    max-width: 600px;
    margin-bottom: 25px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.chat-input {
    border: none;
    background: rgba(255, 255, 255, 0.2); /* Transparent background for glass effect */
    backdrop-filter: blur(6px); /* Add blur for glassmorphic look */
    border-radius: 20px;
    padding: 10px;
    outline: none;
    font-size: 16px;
    color: black; /* Changed for contrast */
    flex-grow: 2;
    margin-right: 10px;
    box-shadow: inset 0 4px 10px rgba(0, 0, 0, 0.1); /* Inner shadow for depth */
}

.chat-input::placeholder {
    color: rgba(0, 0, 0, 0.7); /* Semi-transparent placeholder */
}

.icon-btn {
    background: linear-gradient(145deg, #00B0F0, #00D4FF); /* Gradient for depth */
    border: none;
    border-radius: 50%;
    color: white;
    width: 50px;
    height: 50px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    font-size: 20px;
    transition: background-color 0.3s, transform 0.3s, box-shadow 0.3s;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); /* Add shadow for pop effect */
}

.icon-btn:hover {
    background: linear-gradient(145deg, #ff66b2, #ff1a75); /* Gradient hover effect */
    box-shadow: 0 8px 20px rgba(255, 102, 178, 0.4); /* Glowing effect on hover */
}

.icon-btn:active {
    transform: scale(1.1);
}

.recorder_wrapper {
    display: none;
}

/* Media Queries */
@media (max-width: 768px) {
    .chat-container {
        max-width: 90%;
        padding: 8px;
    }

    .chat-input {
        font-size: 14px;
    }

    .icon-btn {
        width: 45px;
        height: 45px;
        font-size: 18px;
    }
}

@media (max-width: 480px) {
    .chat-container {
        max-width: 100%;
        padding: 5px;
    }

    .chat-input {
        font-size: 12px;
    }

    .icon-btn {
        width: 40px;
        height: 40px;
        font-size: 16px;
    }
}
    </style>
<script>
const chatInput = document.getElementById('chat-input');
const toggleIcon = document.getElementById('toggle-icon');
const msgBox = document.getElementById('msg_box');
let btnStatus = 'inactive', mediaRecorder, chunks = [];

// Function to send data to Flask backend
function sendDataToServer(data, callback) {
    fetch('http://127.0.0.1:5000/save-input', {  // Change URL to your Flask backend
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)  // Send JSON data (text or audio)
    })
    .then(response => response.json())
    .then(result => {
        console.log('Data successfully sent to server:', result);
        callback();  // Callback to handle UI update after sending data
    })
    .catch(error => {
        console.error('Error sending data to server:', error);
    });
}

// Function to refresh the chat UI
function updateChat() {
    // Add code here to refresh the UI or fetch updated chat messages
    // For example, you can trigger a Streamlit rerun from the backend
    console.log("Chat updated with new message.");
}

// Event listener for text input
chatInput.addEventListener('input', () => {
    if (chatInput.value.trim().length > 0) {
        toggleIcon.innerHTML = '<i class="fas fa-paper-plane"></i>';
    } else if (btnStatus !== 'recording') {
        toggleIcon.innerHTML = '<i class="fas fa-microphone"></i>';
    }
});

// Event listener for the button click (toggle between sending text or starting/stopping recording)
toggleIcon.addEventListener('click', () => {
    if (chatInput.value.trim().length > 0) {
        // Handle sending text input to Flask
        sendDataToServer({ text: chatInput.value }, updateChat);
        chatInput.value = '';  // Clear the input field after sending
        toggleIcon.innerHTML = '<i class="fas fa-microphone"></i>';
    } else {
        // Handle recording functionality
        if (btnStatus === 'inactive') {
            startRecording();
        } else if (btnStatus === 'recording') {
            stopRecording();
        }
    }
});

// Function to start recording audio
function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        btnStatus = 'recording';
        toggleIcon.innerHTML = '<i class="fas fa-stop"></i>';
        msgBox.innerHTML = 'Recording...';

        // Collect audio data
        mediaRecorder.ondataavailable = event => {
            chunks.push(event.data);
        };

        // Handle stop recording
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(chunks, { 'type': 'audio/ogg; codecs=opus' });
            chunks = [];  // Reset the chunks array
            handleAudioInput(audioBlob);  // Process the recorded audio
        };
    }).catch(error => {
        console.error("Error accessing microphone:", error);
        msgBox.innerHTML = 'Error accessing the microphone';
    });
}

// Function to stop recording audio
function stopRecording() {
    if (mediaRecorder) {
        mediaRecorder.stop();
        btnStatus = 'inactive';
        toggleIcon.innerHTML = '<i class="fas fa-microphone"></i>';
        msgBox.innerHTML = 'Press the microphone to start recording';
    }
}

// Function to handle sending the recorded audio to Flask
function handleAudioInput(audioBlob) {
    const reader = new FileReader();
    reader.readAsDataURL(audioBlob);  // Convert audio blob to base64
    reader.onloadend = function () {
        const base64String = reader.result.split(',')[1];  // Extract base64 from the result
        sendDataToServer({ audio: base64String }, updateChat);  // Send base64-encoded audio to Flask
    };
}
</script>
"""