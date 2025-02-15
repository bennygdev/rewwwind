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

let isShowingWarning = false;
let chatEndedByAdmin = false;

let userMessage;
let inputInitHeight;

let typingTimeout;

const setInitialHeight = () => {
  inputInitHeight = chatInput.scrollHeight;
};

const saveAIChatHistory = () => {
  if (!isSupportChat) {
    const chatMessages = [];
    document.querySelectorAll('.chatbox .chat').forEach(li => {
      const messageText = li.querySelector('p').textContent;
      const isOutgoing = li.classList.contains('outgoing');
      chatMessages.push({
        message: messageText,
        type: isOutgoing ? 'outgoing' : 'incoming'
      });
    });
    
    localStorage.setItem('aiChatHistory', JSON.stringify(chatMessages));
  }
}

const loadAIChatHistory = () => {
  const savedHistory = localStorage.getItem('aiChatHistory');
  if (savedHistory && !isSupportChat) {
    const chatMessages = JSON.parse(savedHistory);
    chatbox.innerHTML = '';
    
    chatMessages.forEach(msg => {
      const messageElement = createChatLi(msg.message, msg.type);
      chatbox.appendChild(messageElement);
    });
    
    // Show chat interface if there's history
    if (chatMessages.length > 0) {
      document.getElementById('chatChoice').style.display = 'none';
      document.querySelector('.chatbox').style.display = 'block';
      document.querySelector('.chat-input').style.display = 'flex';
      switchToSupportLink.style.display = 'block';
      backBtn.style.display = 'block';
    }
    
    chatbox.scrollTo(0, chatbox.scrollHeight);
  }
}

chatInput.addEventListener("input", () => {
  if (!inputInitHeight) {
    setInitialHeight(); // Set the initial height if not set already
  }
  
  chatInput.style.height = `${inputInitHeight}px`;
  chatInput.style.height = `${chatInput.scrollHeight}px`;

  if (isSupportChat && currentRoom) {
    socket.emit('customer_typing', { room_id: currentRoom });
    
    clearTimeout(typingTimeout);
    
    // set new timeout
    typingTimeout = setTimeout(() => {
      socket.emit('customer_stopped_typing', { room_id: currentRoom });
    }, 1000); // delay 1 second
  }
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
    showSupportForm();
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

  if (chatbox.children.length === 0) {
    const greetingMessage = createChatLi('Hi there 👋\nHow can I help you today?', 'incoming');
    chatbox.innerHTML = ''; // Clear any existing messages
    chatbox.appendChild(greetingMessage);
    
    // Save initial greeting
    saveAIChatHistory();
  }
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
backBtn.addEventListener('click', async () => {
  if (isSupportChat && currentRoom && !chatEndedByAdmin) {
    const shouldLeave = await showLeaveWarning();

    if (shouldLeave) {
      // First emit that customer is leaving
      socket.emit('customer_leave', {
        room_id: currentRoom
      });
      
      // Then end the chat
      socket.emit('end_chat', {
        room_id: currentRoom,
        ended_by: 'customer'
      });
      
      resetChat();
    }
    // If shouldn't leave, do nothing and let them continue chatting
  } else {
    resetChat();
  }
});

function showSupportForm() {
  const existingContent = chatbox.innerHTML;
  chatbox.innerHTML = '';
  
  const supportContainer = document.createElement('div');
  supportContainer.className = 'support-request-container';
  supportContainer.innerHTML = `
    <form class="support-request-form" id="supportRequestForm">
      <h3>Start a Support Chat</h3>
      <div class="form-group">
        <select class="form-control" id="supportType" required>
          <option value="">Select Support Type</option>
          <option value="technical">Technical Support</option>
          <option value="billing">Billing Support</option>
          <option value="account">Account Support</option>
          <option value="general">General Inquiry</option>
        </select>
      </div>
      <div class="form-group">
        <textarea 
          class="form-control" 
          id="problemDescription" 
          placeholder="Please describe your issue..."
          required
        ></textarea>
      </div>
      <div class="form-buttons">
        <button type="submit" class="proceed-btn">Start Chat</button>
        <button type="button" class="goBack-btn">Go Back</button>
      </div>
    </form>
  `;
  
  chatbox.appendChild(supportContainer);
  
  const form = supportContainer.querySelector('#supportRequestForm');
  const goBackBtn = supportContainer.querySelector('.goBack-btn');
  
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const supportType = document.getElementById('supportType').value;
    const description = document.getElementById('problemDescription').value;
    
    if (supportType && description) {
      chatbox.innerHTML = '';
      initializeSupportChat(supportType, description);
    }
  });
  
  goBackBtn.addEventListener('click', () => {
    resetChat();
  });
}

function showLeaveWarning() {
  if (isShowingWarning) {
    return Promise.resolve(false);
  }

  if (chatEndedByAdmin) {
    return Promise.resolve(true);
  }

  isShowingWarning = true;

  const warningMessage = document.createElement('li');
  warningMessage.className = 'chat leave-warning';
  warningMessage.innerHTML = `
    <div class="warning-message">
      <h3>⚠️ Warning</h3>
      <div class="warning-text">Are you sure you want to leave this support chat?</div>
      <div class="warning-text">This will end your current chat session.</div>
      <div class="warning-buttons">
        <button class="leave-btn">Leave Chat</button>
        <button class="stay-btn">Stay in Chat</button>
      </div>
    </div>
  `;
  
  chatbox.appendChild(warningMessage);
  chatbox.scrollTo(0, chatbox.scrollHeight);
  
  // Disable chat while warning is shown
  chatInput.disabled = true;
  
  return new Promise((resolve) => {
    const leaveBtn = warningMessage.querySelector('.leave-btn');
    const stayBtn = warningMessage.querySelector('.stay-btn');

    const cleanup = () => {
      warningMessage.remove();
      chatInput.disabled = false;
      isShowingWarning = false;
    };
    
    leaveBtn.addEventListener('click', () => {
      cleanup();
      resolve(true); // User wants to leave
    });
    
    stayBtn.addEventListener('click', () => {
      cleanup();
      resolve(false); // User wants to stay
    });
  });
}

function initializeSupportChat(supportType, description) {
  chatInput.disabled = false;

  // Request customer support
  socket.emit('request_support', {
    supportType: supportType,
    description: description
  });
  
  // Initial waiting message
  const waitingMessage = createChatLi('Requesting customer support...', 'incoming');
  chatbox.appendChild(waitingMessage);

  // Add the customer's description as their first message
  const descriptionMessage = createChatLi(description, 'outgoing');
  chatbox.appendChild(descriptionMessage);
}

const createChatLi = (message, className) => {
  // create a chat li element with passed message and classname
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", className);

  let chatContent;
  if (className === "outgoing") {
    chatContent = `<p></p>`;
  } else {
    const icon = isSupportChat ? "fa-headset" : "fa-robot";
    chatContent = `<span><i class="fa-solid ${icon}"></i></span><p></p>`;
  }

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

  return Promise.resolve();
}

const handleChat = () => {
  userMessage = chatInput.value.trim();
  // console.log(userMessage)
  if (!userMessage) return;

  // Clear input and reset height
  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px`

  if (isSupportChat && currentRoom) {
    clearTimeout(typingTimeout);
    socket.emit('customer_stopped_typing', { room_id: currentRoom });
  }

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
        generateResponse(incomingChatLi).then(() => {
          saveAIChatHistory();
        });
    }, 600);

    saveAIChatHistory();
  }
}

// Add reconnection logic when page loads
window.addEventListener('load', () => {
  if (isSupportChat) {
    socket.emit('customer_reconnect');
  } else {
    loadAIChatHistory();
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

  const chatHeader = document.querySelector('.chat-header');
  if (chatHeader) {
    const supportType = currentRoom ? active_chats[currentRoom].supportType : 'general';
    const supportTypeLabel = getSupportTypeLabel(supportType);
    
    chatHeader.innerHTML = `
      <div class="chat-header-container">
        <h4>${data.message}</h4>
        <span class="support-type-badge support-type-${supportType}">${supportTypeLabel}</span>
      </div>
    `;
  }
});

// helper function
function getSupportTypeLabel(type) {
  const labels = {
    'technical': 'Technical Support',
    'billing': 'Billing Support',
    'account': 'Account Support',
    'general': 'General Inquiry'
  };
  return labels[type] || 'General Inquiry';
}

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
    
//   // Reset chat after delay
//   setTimeout(() => {
//     resetChat();
//   }, 3000);
// });
socket.on('chat_ended', (data) => {
  // Add the end message
  const messageElement = createChatLi(data.message, 'incoming');
  chatbox.appendChild(messageElement);
  
  // Only reset if customer ended the chat
  if (data.ended_by === 'admin') {
    chatEndedByAdmin = true;

    // If admin ended the chat, show follow-up message and new chat option
    const followUpMessage = createChatLi("You're free to leave this chat. Thank you for using our support service!", 'incoming');
    chatbox.appendChild(followUpMessage);
    
    chatInput.disabled = true;

    // Create and add the "Start New Chat" link below the chat messages
    const newChatMessage = document.createElement('li');
    newChatMessage.className = 'chat new-chat-prompt';
    newChatMessage.innerHTML = `
      <div class="new-chat-link">
        <a href="#" class="start-new-chat">Start a New Chat Session</a>
      </div>
    `;
    chatbox.appendChild(newChatMessage);

    // Add event listener for the new chat link
    newChatMessage.querySelector('.start-new-chat').addEventListener('click', (e) => {
      e.preventDefault();
      chatEndedByAdmin = false;
      showSupportForm();
    });
  } else {
    resetChat();
  }
  
  chatbox.scrollTo(0, chatbox.scrollHeight);
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
  chatInput.disabled = false;
  chatEndedByAdmin = false;
  isShowingWarning = false;

  localStorage.removeItem('aiChatHistory');

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

// Typing indicators
socket.on('admin_typing', () => {
  const existingIndicator = document.querySelector('.typing-indicator');
  if (!existingIndicator) {
    const typingLi = document.createElement("li");
    typingLi.classList.add("chat", "incoming", "typing-indicator");
    typingLi.innerHTML = `<span><i class="fa-solid fa-headset"></i></span><p>Support representative is typing...</p>`;
    chatbox.appendChild(typingLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);
  }
});

socket.on('admin_stopped_typing', () => {
  const typingIndicator = document.querySelector('.typing-indicator');
  if (typingIndicator) {
    typingIndicator.remove();
  }
});