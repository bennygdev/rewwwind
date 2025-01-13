const chatInput = document.querySelector('.chat-input textarea');
const sendChatBtn = document.querySelector('.chat-input span');
const chatbox = document.querySelector('.chatbox');
const chatbotToggler = document.querySelector('.chatbot-toggler');
const chatbotWrapper = document.querySelector('.chatbot__wrapper');
const chatbotHeaderCloseBtn = document.querySelector('.chatbot header span');
const sendBtn = document.getElementById('send-btn');
const switchToSupportLink = document.querySelector('.switch-to-support');
const socket = io();

let currentRoom = null;
let isSupportChat = false;

let userMessage;
let inputInitHeight;

const setInitialHeight = () => {
  inputInitHeight = chatInput.scrollHeight;
};

chatInput.addEventListener("input", () => {
  if (!inputInitHeight) {
    setInitialHeight(); // Set the initial height if not set already
  }
  
  chatInput.style.height = `${inputInitHeight}px`;
  chatInput.style.height = `${chatInput.scrollHeight}px`;
});

document.getElementById('supportBtn').addEventListener('click', async () => {
  // Check if user is authenticated
  const response = await fetch('/dashboard/api/check-auth');
  const data = await response.json();
  switchToSupportLink.style.display = 'none';
  
  if (!data.authenticated) {
    window.location.href = '/login';
    return;
  }

  // Check if user already has an active chat
  const chatResponse = await fetch('/dashboard/api/check-active-chat');
  const chatData = await chatResponse.json();
  
  if (chatData.hasActiveChat) {
    // Restore previous chat session
    currentRoom = chatData.roomId;
    isSupportChat = true;
    showChatInterface();
    // Load previous messages
    const messages = chatData.messages;
    messages.forEach(msg => {
      const messageElement = createChatLi(msg.message, msg.type);
      chatbox.appendChild(messageElement);
    });
  } else {
    // Start new chat
    isSupportChat = true;
    showChatInterface();
    initializeSupportChat();
  }
});

function showChatInterface() {
  document.getElementById('chatChoice').style.display = 'none';
  document.querySelector('.chatbox').style.display = 'block';
  document.querySelector('.chat-input').style.display = 'flex';
  backBtn.style.display = 'block';
}

document.getElementById('chatbotBtn').addEventListener('click', () => {
  isSupportChat = false;
  document.getElementById('chatChoice').style.display = 'none';
  document.querySelector('.chatbox').style.display = 'block';
  document.querySelector('.chat-input').style.display = 'flex';
  switchToSupportLink.style.display = 'block';
  backBtn.style.display = 'block';

  const greetingMessage = createChatLi('Hi there 👋\nHow can I help you today?', 'incoming');
  chatbox.innerHTML = ''; // Clear any existing messages
  chatbox.appendChild(greetingMessage);
});

const chatHeader = document.querySelector('.chatbot header');
chatHeader.innerHTML = `
  <button class="back-btn" style="position: absolute; left: 20px; display: none;">
    <i class="fa-solid fa-arrow-left"></i>
  </button>
  <h2>Chat</h2>
  <span><i class="fa-solid fa-xmark fa-lg"></i></span>
`;

const backBtn = document.querySelector('.back-btn');

// Handle back button click
backBtn.addEventListener('click', () => {
  if (isSupportChat && currentRoom) {
    // First emit that customer is leaving
    socket.emit('customer_leave', {
      room_id: currentRoom
    });
    
    // Then end the chat
    socket.emit('end_chat', {
      room_id: currentRoom,
      ended_by: 'customer'
    });
  }
  resetChat();
});

function initializeSupportChat() {
  // Request customer support
  socket.emit('request_support', {});
  
  // Initial waiting message
  const waitingMessage = createChatLi('Requesting customer support...', 'incoming');
  chatbox.appendChild(waitingMessage);
}

const createChatLi = (message, className) => {
  // create a chat li element with passed message and classname
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", className);

  let chatContent = className === "outgoing" ? `<p></p>` : `<span><i class="fa-solid fa-robot"></i></span><p></p>`;
  chatLi.innerHTML = chatContent;
  chatLi.querySelector("p").textContent = message
  return chatLi;
}

const generateResponse = async (incomingChatLi) => {
  const messageElement = incomingChatLi.querySelector("p");

  try {
    const response = await fetch('/api/chat', { // gemini api endpoint
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector('meta[name="csrf-token"]')?.content
      },
      body: JSON.stringify({
        message: userMessage
      })
    });

    const data = await response.json();
      
    if (response.ok) {
      messageElement.textContent = data.response;
    } else {
      throw new Error(data.error || 'Failed to get response');
    }
  } catch (error) {
    console.error(error);
    messageElement.classList.add("error");
    messageElement.textContent = "Oops! Something went wrong. Please try again.";
  } finally {
    chatbox.scrollTo(0, chatbox.scrollHeight);
  }
}

const handleChat = () => {
  userMessage = chatInput.value.trim();
  // console.log(userMessage)
  if (!userMessage) return;

  // Clear input and reset height
  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px`

  // append user message to chatbox
  chatbox.appendChild(createChatLi(userMessage, "outgoing"));
  chatbox.scrollTo(0, chatbox.scrollHeight);

  if (isSupportChat && currentRoom) {
    // Send message through socket for support chat
    socket.emit('chat_message', {
        room_id: currentRoom,
        message: userMessage
    });
  } else {
    // Original chatbot logic
    setTimeout(() => {
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        generateResponse(incomingChatLi);
    }, 600);
  }
}

// Add reconnection logic when page loads
window.addEventListener('load', () => {
  if (isSupportChat) {
      socket.emit('customer_reconnect');
  }
});

sendBtn.addEventListener('click', handleChat);
// resize textarea height based on content
chatInput.addEventListener("input", () => {
  chatInput.style.height = `${inputInitHeight}px`
  chatInput.style.height = `${chatInput.scrollHeight}px`
});

// enter key without shift key and window width > 800
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
    e.preventDefault();
    handleChat();
  }
});

chatbotHeaderCloseBtn.addEventListener("click", () => {
  chatbotWrapper.classList.remove("show-chatbot");
});

// floating button actions
chatbotToggler.addEventListener("click", () => {
  chatbotWrapper.classList.toggle("show-chatbot");
});

document.getElementById('switchToSupport').addEventListener('click', async (e) => {
  e.preventDefault();
  
  // Check if user is authenticated
  const response = await fetch('/dashboard/api/check-auth');
  const data = await response.json();
  
  if (!data.authenticated) {
    window.location.href = '/login';
    return;
  }

  // Hide the support link since we're switching to support chat
  switchToSupportLink.style.display = 'none';
  
  // Clear the AI chat history
  chatbox.innerHTML = '';
  
  // Switch to support chat
  isSupportChat = true;
  initializeSupportChat();
});

// Socket event listeners
socket.on('support_request_acknowledged', (data) => {
  currentRoom = data.room_id;
  const messageElement = createChatLi(data.message, 'incoming');
  chatbox.appendChild(messageElement);
  chatbox.scrollTo(0, chatbox.scrollHeight);
});

socket.on('admin_joined', (data) => {
  const messageElement = createChatLi(data.message, 'incoming');
  chatbox.appendChild(messageElement);
  chatbox.scrollTo(0, chatbox.scrollHeight);
});

socket.on('admin_left_chat', (data) => {
  const messageElement = createChatLi(data.message, 'incoming');
  chatbox.appendChild(messageElement);
  chatbox.scrollTo(0, chatbox.scrollHeight);
});

socket.on('new_message', (data) => {
  if (data.sender_type !== 'customer') {
    const messageElement = createChatLi(data.message, 'incoming');
    chatbox.appendChild(messageElement);
    chatbox.scrollTo(0, chatbox.scrollHeight);
  }
});

// socket.on('chat_ended', (data) => {
//   const messageElement = createChatLi(data.message, 'incoming');
//   chatbox.appendChild(messageElement);
//   chatbox.scrollTo(0, chatbox.scrollHeight);
//   currentRoom = null;
  
//   // Reset chat interface
//   setTimeout(() => {
//     document.getElementById('chatChoice').style.display = 'block';
//     document.querySelector('.chatbox').style.display = 'none';
//     document.querySelector('.chat-input').style.display = 'none';
//     chatbox.innerHTML = ''; // Clear chat history
//   }, 3000);
// });
socket.on('chat_ended', (data) => {
  const messageElement = createChatLi(data.message, 'incoming');
  chatbox.appendChild(messageElement);
  chatbox.scrollTo(0, chatbox.scrollHeight);
    
  // Reset chat after delay
  setTimeout(() => {
    resetChat();
  }, 3000);
});

let connectionInterval;
let lastPong = Date.now();

function startConnectionMonitor() {
  connectionInterval = setInterval(() => {
    // Check if we've received a pong in the last 10 seconds
    if (Date.now() - lastPong > 10000) {
      handleDisconnection();
    }
    socket.emit('ping_connection');
  }, 5000);
}

function handleDisconnection() {
  clearInterval(connectionInterval);
    
  // Show reconnection message
  const messageElement = createChatLi('Connection lost. Attempting to reconnect...', 'system');
  chatbox.appendChild(messageElement);
    
  // Attempt to reconnect
  socket.connect();
}

socket.on('pong_connection', () => {
  lastPong = Date.now();
});

socket.on('connect', () => {
  startConnectionMonitor();
  if (currentRoom) {
    // Rejoin room if we were in one
    socket.emit('rejoin_room', { room_id: currentRoom });
  }
});

socket.on('user_disconnected', (data) => {
  const messageElement = createChatLi(data.message, 'system');
  chatbox.appendChild(messageElement);
    
  if (data.user_type === 'admin') {
    // Reset chat for customer if admin disconnects
    setTimeout(() => {
      resetChat();
    }, 3000);
  }
});

socket.on('chat_history', (data) => {
  chatbox.innerHTML = ''; // Clear existing messages
  currentRoom = data.room_id; // Set current room
  
  data.messages.forEach(msg => {
    const messageElement = createChatLi(
      msg.message, 
      msg.type === 'outgoing' ? 'outgoing' : 'incoming'
    );
    chatbox.appendChild(messageElement);
  });
  chatbox.scrollTo(0, chatbox.scrollHeight);
});

function resetChat() {
  currentRoom = null;
  isSupportChat = false;
  const chatChoice = document.getElementById('chatChoice');
  document.querySelector('.chatbox').style.display = 'none';
  document.querySelector('.chat-input').style.display = 'none';
  backBtn.style.display = 'none';
  switchToSupportLink.style.display = 'none';

  // Reset display properties
  chatChoice.style.display = 'flex';
  chatChoice.style.flexDirection = 'column';
  chatChoice.style.justifyContent = 'center';
  chatChoice.style.alignItems = 'center';
  chatChoice.style.gap = '10px';
  chatChoice.style.padding = '20px 0';

  chatbox.innerHTML = '';
}