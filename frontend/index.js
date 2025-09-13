const chatLog = document.getElementById('chat-log'),
      userInput = document.getElementById('user-input'),
      sendButton = document.getElementById('send-button'),
      conformButton = document.getElementById('conform'),
      logoutButton = document.getElementById('logout-button'),
      clearHistoryButton = document.getElementById('clear-history-button'),
      clearHistoryModal = document.getElementById('clear-history-modal'),
      confirmClearButton = document.getElementById('confirm-clear'),
      cancelClearButton = document.getElementById('cancel-clear'),
      usernameInput = document.getElementById('username'),
      buttonIcon = document.getElementById('button-icon'),
      loginContainer = document.querySelector('.login-container'),
      youtube = document.getElementById('youtube'),
      inputContainer = document.querySelector('.input-container'),
      info = document.querySelector('.info');
<<<<<<< HEAD

// let url = "https://orange-trout-jxg7p4799j6255qr-9999.app.github.dev"
// let url = "https://ll62xj-9999.csb.app"
// let url = "https://a0545507d9f6.ngrok-free.app"
let url = "http://localhost:9999";

=======
let url = "https://orange-trout-jxg7p4799j6255qr-9999.app.github.dev"
// let url = "https://ll62xj-9999.csb.app"
// let url = "https://a0545507d9f6.ngrok-free.app"
// let url = "http://localhost:9999"
>>>>>>> bb2562532ae92ad7dc6bda038412c555b346dd69
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') sendMessage();
});

// Toggle nút clear history
function toggleClearHistoryButton() {
    const sessionId = sessionStorage.getItem("sessionId");
    if (sessionId && chatLog.children.length > 0) {
        clearHistoryButton.style.display = "block"; 
    } else {
        clearHistoryButton.style.display = "none"; 
    }
}

// Đăng nhập
conformButton.addEventListener('click', (e) => {
    e.preventDefault();
    const username = usernameInput.value;
    if (!username) {
        alert("Vui lòng nhập tên đăng nhập!");
        return; 
    }
    sessionStorage.setItem("sessionId", username);
    document.getElementById('name').innerText = "Xin chào " + username;
    loginContainer.style.display = "none";
    inputContainer.style.display = "flex";
    logoutButton.style.display = "block";

    loadDialogue(username).then(() => {
        toggleClearHistoryButton();
    });
});

// Đăng xuất
logoutButton.addEventListener("click", () => {
    sessionStorage.removeItem("sessionId");  
    loginContainer.style.display = "block";  
    inputContainer.style.display = "none";
    logoutButton.style.display = "none";
    chatLog.innerHTML = "";
    info.style.display = "flex";
    toggleClearHistoryButton();
});

// Xử lý nút xóa lịch sử
clearHistoryButton.addEventListener("click", () => {
    clearHistoryModal.style.display = "block";
});

confirmClearButton.addEventListener("click", async () => {
    const sessionId = sessionStorage.getItem("sessionId");
    if (!sessionId) return;

    try {
        const response = await fetch(url + `/clear-history/${sessionId}`, {
            method: "DELETE"
        });

        if (response.ok) {
            chatLog.innerHTML = "";
            info.style.display = "flex";
        } else {
            throw new Error("Không thể xóa lịch sử trên server");
        }
    } catch (error) {
        console.error("Lỗi khi xóa lịch sử:", error);
        chatLog.innerHTML = "";
        info.style.display = "flex";
        alert("Đã xóa lịch sử trò chuyện trên giao diện!");
    }

    clearHistoryModal.style.display = "none";
    toggleClearHistoryButton();
});

cancelClearButton.addEventListener("click", () => {
    clearHistoryModal.style.display = "none";
});
clearHistoryModal.addEventListener("click", (e) => {
    if (e.target === clearHistoryModal) {
        clearHistoryModal.style.display = "none";
    }
});

// Load khi vào lại trang
window.onload = function() {
   if (sessionStorage.getItem("sessionId")) {
    sessionId = sessionStorage.getItem("sessionId");
    console.log("Đã có sessionId:", sessionId );
    document.getElementById('name').innerText = "Xin chào " + sessionId;
    loginContainer.style.display = "none";
    inputContainer.style.display = "flex";
    logoutButton.style.display = "block";

    loadDialogue(sessionId).then(() => {
        toggleClearHistoryButton();
    });
  } else {
    inputContainer.style.display = "none";
    logoutButton.style.display = "none";
    clearHistoryButton.style.display = "none";
  }
};

const modelConfig = {
    model_name: "llama-3.3-70b-versatile",
    model_provider: "Groq",
};

function sendMessage() {
    const message = userInput.value.trim();
    const sessionId = sessionStorage.getItem("sessionId");
    if (!message) return;
    buttonIcon.classList.remove('fa-solid', 'fa-paper-plane');
    buttonIcon.classList.add('fas', 'fa-spinner', 'fa-pulse');
    appendMessage('user', message);
    userInput.value = '';
    const options = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            model_name: modelConfig.model_name,
            model_provider: modelConfig.model_provider,
            messages: [message],
        })
    };
    fetch(url+`/chat?session_id=${sessionId}`, options)
        .then(response => {
            if (!response.ok) throw new Error(`Lỗi ${response.status}: ${response.statusText}`);
            return response.json();
        })
        .then(data => appendMessage('bot', data))
        .catch(err =>{
           appendMessage('bot', { ai: "Error: " + err.message, tool: [] })
        })
        .finally(() => {
            buttonIcon.classList.add('fa-solid', 'fa-paper-plane');
            buttonIcon.classList.remove('fas', 'fa-spinner', 'fa-pulse');
        });
}

let activeIframe = null;
function appendMessage(sender, message) { 
    info.style.display = "none";
    const chatElement = document.createElement('div');
    chatElement.classList.add("chat-box");

    const iconElement = document.createElement('div');
    iconElement.classList.add("icon");
    const icon = document.createElement('i');

    const messageElement = document.createElement('div');
    messageElement.classList.add(sender);
    messageElement.style.display = "flex";
    messageElement.style.flexDirection = "column";

    if (sender === 'user') {
        icon.classList.add('fa-regular', 'fa-user');
        iconElement.id = 'user-icon';
        messageElement.innerText = message;
    } else {
        icon.classList.add('fa-solid', 'fa-robot');
        iconElement.id = 'bot-icon';
        console.log(message);
        
        if (Array.isArray(message.tool) && message.tool.length > 0) {
            try {
                let videos = [];

                message.tool.forEach(toolItem => {
                    try {
                        let parsed = typeof toolItem === "string" ? JSON.parse(toolItem) : toolItem;
                        if (typeof parsed === "string") {
                            parsed = JSON.parse(parsed);
                        }
                        if (Array.isArray(parsed)) {
                            videos = videos.concat(parsed);
                        } else {
                            videos.push(parsed);
                        }
                    } catch (err) {
                        console.error("Parse toolItem lỗi:", err, toolItem);
                    }
                });

                console.log("✅ Parsed videos:", videos);
                videos = videos.filter(v => v && v.video_id);

                if (videos.length > 0) {
                    const data = videos[0]; 
                    const videoContainer = document.createElement('div');
                    videoContainer.style.display = "flex";
                    videoContainer.style.justifyContent = "center";
                    videoContainer.style.marginBottom = "10px";
                    videoContainer.style.width = "100%"; 

                    const iframe = document.createElement("iframe");
                    iframe.width = "560";
                    iframe.height = "315";
                    iframe.src = `https://www.youtube.com/embed/${data.video_id}`;
                    iframe.title = data.title || "YouTube video player";
                    iframe.frameBorder = "0";
                    iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
                    iframe.allowFullscreen = true;

                    videoContainer.appendChild(iframe);
                    messageElement.appendChild(videoContainer);

                    if (activeIframe) {
                        activeIframe.closest('div').remove();
                    }
                    activeIframe = iframe;
                }
            } catch (err) {
                console.error("Lỗi khi xử lý video:", err);
            }
        }

        if (message.ai) {
            const textElement = document.createElement('div');
            textElement.innerText = message.ai;
            messageElement.appendChild(textElement);
        }
    }

    iconElement.appendChild(icon);
    chatElement.appendChild(iconElement);
    chatElement.appendChild(messageElement);
    chatLog.appendChild(chatElement);
    chatLog.scrollTop = chatLog.scrollHeight;

    toggleClearHistoryButton(); // ✅ gọi sau khi thêm message
}

function appendListMessage(ListMessage) {
    ListMessage.forEach(msg => {
        if (msg.role === "user") {
            appendMessage("user", msg.content);
        } else if (msg.role === "ai") {
            appendMessage("bot", { 
                ai: msg.content, 
                tool: msg.tool || [] 
            });
        } else if (msg.role === "tool") {
            appendMessage("tool", msg.content);
        }
    });
}

const micButton = document.getElementById("mic-button");
const micIcon = document.getElementById("mic-icon");

let can_record = false;
let is_recording = false;
let recorder = null;
let chucks = [];
let audioStream = null;
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

micButton.addEventListener('click', async () => {
    if (!is_recording) {
        try {
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            recorder = new MediaRecorder(audioStream);
            can_record = true;
            is_recording = true;
            await new Promise(resolve => {
                micIcon.classList.remove("fa-microphone-slash");
                micIcon.classList.add("fa-microphone");
                micButton.style.backgroundColor = "#e53935"; 
                userInput.disabled = true;
                sendButton.disabled = true;
                sendButton.style.backgroundColor = "#ccc";
                sendButton.style.cursor = "not-allowed"; 
                resolve();
            });
            recorder.ondataavailable = e => chucks.push(e.data);

            recorder.onstop = async () => {
                console.log("🔹 Dừng ghi âm, chuẩn bị xử lý...");
                const sessionId = sessionStorage.getItem("sessionId")

                const blob = new Blob(chucks, { type: "audio/ogg; codecs=opus" });
                chucks = [];

                const arrayBuffer = await blob.arrayBuffer();
                const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
                const wavData = audioBufferToWav(audioBuffer);
                const wavBlob = new Blob([wavData], { type: "audio/wav" });
                console.log("🔹 Upload WAV lên FastAPI...");
                const formData = new FormData();
                formData.append("file", wavBlob, sessionId +".wav");
                try {
                    const res = await fetch(url + "/upload-audio/", {
                        method: "POST",
                        body: formData
                    });
                    const data = await res.json();
                    console.log("Upload thành công", data);
                } catch(err) {
                    console.error("Upload error:", err);
                }
                try {
                    const res1 = await fetch(url + `/get-audio-result?session_id=${sessionId}`, {
                        method: "GET",
                        headers: {
                            "ngrok-skip-browser-warning": "true"
                        }
                    });
                    console.log("Lấy kết quả nhận diện...");
                    console.log(res1);

                    const text = await res1.json();
                    console.log(text);
                    appendListMessage(text)
                    sendButton.disabled = false;
                    userInput.disabled = false;
                    sendButton.style.backgroundColor = "#4caf50";
                    sendButton.style.cursor = "pointer"; 

                } catch (err) {
                    console.error("Get result error:", err);
                }         
            };
            recorder.start();
        } catch (err) {
            console.error("Không thể truy cập mic:", err);
        }

    } else {
        recorder.stop();
        if (audioStream) {
            audioStream.getTracks().forEach(track => track.stop());
            audioStream = null;
            can_record = false;
        }
        is_recording = false;      
        await new Promise(resolve => {
            micIcon.classList.remove("fa-microphone");
            micIcon.classList.add("fa-microphone-slash");
            micButton.style.backgroundColor = "#2196f3";
            resolve();
        });
    }
});

async function loadDialogue(sessionId) {
    try {
        const res = await fetch(url + `/get-dialogue/${sessionId}`);
        if (!res.ok) throw new Error(`Lỗi ${res.status}: ${res.statusText}`);

        const dialogue = await res.json();
        console.log("Dữ liệu dialogue:", dialogue);
        appendListMessage(dialogue);
        toggleClearHistoryButton();
    } catch (err) {
        console.error("Load dialogue error:", err);
    }
}

function audioBufferToWav(buffer) {
    let numOfChan = buffer.numberOfChannels,
        length = buffer.length * numOfChan * 2 + 44,
        bufferArray = new ArrayBuffer(length),
        view = new DataView(bufferArray),
        channels = [], i, sample, offset=0, pos=0;

    function setUint16(data){ view.setUint16(pos, data, true); pos += 2; }
    function setUint32(data){ view.setUint32(pos, data, true); pos += 4; }

    setUint32(0x46464952); 
    setUint32(length-8);
    setUint32(0x45564157); 

    setUint32(0x20746d66); setUint32(16);
    setUint16(1); setUint16(numOfChan);
    setUint32(buffer.sampleRate);
    setUint32(buffer.sampleRate * 2 * numOfChan);
    setUint16(numOfChan * 2); setUint16(16);

    setUint32(0x61746164); setUint32(length-pos-4);

    for(i=0; i<numOfChan; i++) channels.push(buffer.getChannelData(i));

    while(offset < buffer.length){
        for(i=0; i<numOfChan; i++){
            sample = Math.max(-1, Math.min(1, channels[i][offset]));
            sample = (0.5 + sample*32767)|0;
            view.setInt16(pos, sample, true);
            pos += 2;
        }
        offset++;
    }

    return bufferArray;
}
