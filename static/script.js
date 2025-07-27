let currentChatId = null;

async function newChat() {
  clearError();
  const response = await fetch("/new_chat", {
    method: "POST"
  });
  const data = await response.json();
  if (data.error) {
    showError(data.error)
  }
  currentChatId = data.chat_id;

  // Update UI
  document.getElementById("chatBox").innerHTML = "";
  addConversationToSidebar(currentChatId);
}

async function sendMessage() {
  clearError();
  const input = document.getElementById("userInput");
  const chatBox = document.getElementById("chatBox");
  const userMessage = input.value.trim();
  if (!userMessage) return;

  if (!currentChatId) {
    showError("Please create new Chat!")
    return;
  }

  // Add user message to UI
  const userBubble = document.createElement("div");
  userBubble.className = "message user";
  userBubble.textContent = userMessage;
  chatBox.appendChild(userBubble);
  input.value = "";

  // Show loading
  const loading = document.createElement("div");
  loading.className = "message ai";
  loading.textContent = "Typing...";
  chatBox.appendChild(loading);
  chatBox.scrollTop = chatBox.scrollHeight;

  // Send to backend
  const response = await fetch(`/chat/${currentChatId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMessage })
  });

  const data = await response.json();
  if (data.error) {
    showError(data.error)
  }
  loading.textContent = data.reply;
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function loadChat(id) {
  clearError();
  currentChatId = id;
  const chatBox = document.getElementById("chatBox");
  chatBox.innerHTML = "";

  const response = await fetch(`/load_chat/${id}`);
  const data = await response.json();

  if (data.error) {
    showError(data.error)
  }

  data.messages.forEach(msg => {
    if (msg.role === "system") return; // skip system
    const bubble = document.createElement("div");
    bubble.className = "message " + (msg.role === "user" ? "user" : "ai");
    bubble.textContent = msg.content;
    chatBox.appendChild(bubble);
  });

  chatBox.scrollTop = chatBox.scrollHeight;
}

function showError(message) {
  const errorBox = document.getElementById("errorMessage");
  const errorText = document.getElementById("errorText");
  errorText.innerText = message;
  errorBox.style.display = "block";
}

function hideError() {
  document.getElementById("errorMessage").style.display = "none";
}

function clearError() {
  const errorText = document.getElementById("errorText");
  errorText.innerText = "";
  hideError();
}


function addConversationToSidebar(id) {
  const list = document.getElementById("conversationList");
  const item = document.createElement("li");
  item.textContent = `Chat ${list.children.length + 1}`;
  item.onclick = () => loadChat(id);
  list.appendChild(item);
}

document.addEventListener("DOMContentLoaded", () => {
  const textarea = document.getElementById("userInput");
  textarea.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Ngăn xuống dòng
      sendMessage();
    }
  });
});

async function uploadFile() {
  clearError();
  const fileInput = document.getElementById("fileInput");
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const response = await fetch("/upload", {
    method: "POST",
    body: formData
  });

  const data = await response.json();
  alert(data.message || data.error);
}
