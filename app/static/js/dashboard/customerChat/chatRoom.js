const socket = io();
let currentRoom = null;

const chatInputArea = document.querySelector('.chat-input-area');
const saveStatusDiv = document.createElement('div');

let adminTypingTimeout;

saveStatusDiv.className = 'save-status mt-2 text-center';
chatInputArea.appendChild(saveStatusDiv);

// Add chat controls to header
document.querySelector('.chat-header').innerHTML += `
  <div class="chat-controls">
    <button id="backBtn">Back</button>
    <button id="endChatBtn">End Chat</button>
  </div>
`;

// Extract room ID from URL path instead of query params
currentRoom = window.location.pathname.split('/').pop();

// debug
console.log('Connecting to room:', currentRoom);

// Handle back button
document.getElementById('backBtn').addEventListener('click', () => {
  if (currentRoom) {
    socket.emit('admin_leave_chat', {
      room_id: currentRoom
    });
  }
  window.location.href = '/dashboard/customer-chat';
});

// Handle end chat button
document.getElementById('endChatBtn').addEventListener('click', () => {
  if (currentRoom) {
    socket.emit('end_chat', {
      room_id: currentRoom,
      ended_by: 'admin'
    });
  }
});

// Join chat room as soon as socket connects
socket.on('connect', () => {
  console.log('Socket connected');
  if (currentRoom) {
    console.log('Joining room:', currentRoom);
    socket.emit('admin_join_chat', { room_id: currentRoom });
  }
  startConnectionMonitor();
});

// Confirm room join
socket.on('admin_joined', (data) => {
  console.log('Successfully joined room:', data);
  const messageHtml = `
    <div class="message system">
      <div class="message-content">
        ${data.message}
      </div>
    </div>
  `;
  document.querySelector('.chat-messages').insertAdjacentHTML('beforeend', messageHtml);
});

// Handle sending messages
document.getElementById('sendMessage').addEventListener('click', sendMessage);
document.getElementById('adminChatInput').addEventListener('input', (e) => {
  const input = e.target;
  
  if (currentRoom) {
    socket.emit('admin_typing', { room_id: currentRoom });
    
    clearTimeout(adminTypingTimeout);
    
    // set new timeout
    adminTypingTimeout = setTimeout(() => {
      socket.emit('admin_stopped_typing', { room_id: currentRoom });
    }, 1000); // delay 1 second
  }
});

document.getElementById('adminChatInput').addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

function sendMessage() {
  const messageInput = document.getElementById('adminChatInput');
  const message = messageInput.value.trim();
  if (message && currentRoom) {
    clearTimeout(adminTypingTimeout);
    socket.emit('admin_stopped_typing', { room_id: currentRoom });

    console.log('Sending message to room:', currentRoom);
    socket.emit('chat_message', {
      room_id: currentRoom,
      message: message
    });
      
    // Add message to chat
    const messageHtml = `
      <div class="message outgoing">
        <div class="message-content">
          ${message}
        </div>
        <small class="message-time">${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</small>
      </div>
    `;
    document.querySelector('.chat-messages').insertAdjacentHTML('beforeend', messageHtml);
      
    // Clear input
    messageInput.value = '';
    
    // Scroll to bottom
    const chatMessages = document.querySelector('.chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

// Handle incoming messages
socket.on('new_message', (data) => {
  console.log('Received message:', data);
  if (data.sender_type === 'customer') {
    const messageHtml = `
      <div class="message incoming">
        <div class="message-content">
          ${data.message}
        </div>
        <small class="message-time">${data.timestamp}</small>
      </div>
    `;
    document.querySelector('.chat-messages').insertAdjacentHTML('beforeend', messageHtml);
    
    // Scroll to bottom
    const chatMessages = document.querySelector('.chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
});

// Handle chat history
socket.on('chat_history', (data) => {
  console.log('Received chat history:', data);
  const chatMessages = document.querySelector('.chat-messages');
  chatMessages.innerHTML = ''; // Clear existing messages
  
  if (data.messages && Array.isArray(data.messages)) {
    data.messages.forEach(msg => {
      const messageHtml = `
        <div class="message ${msg.type === 'outgoing' ? 'outgoing' : 'incoming'} mb-3">
          <div class="message-content">
            ${msg.message}
          </div>
          <small class="text-muted">${msg.timestamp}</small>
        </div>
      `;
      chatMessages.insertAdjacentHTML('beforeend', messageHtml);
    });
    
    // Scroll to bottom after loading history
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
});

let connectionInterval;
let lastPong = Date.now();

const startConnectionMonitor = () => {
  connectionInterval = setInterval(() => {
    if (Date.now() - lastPong > 10000) {
      handleDisconnection();
    }
    socket.emit('ping_connection');
  }, 5000);
}

const handleDisconnection = () => {
  clearInterval(connectionInterval);
  const messageHtml = `
    <div class="message system mb-3">
      <div class="message-content bg-warning text-dark p-2 rounded">
        Connection lost. Attempting to reconnect...
      </div>
    </div>
  `;
  document.querySelector('.chat-messages').insertAdjacentHTML('beforeend', messageHtml);
  socket.connect();
}

socket.on('pong_connection', () => {
  lastPong = Date.now();
});

socket.on('chat_ended', (data) => {
  // Show end message
  const messageHtml = `
    <div class="message system mb-3">
      <div class="message-content bg-warning text-dark p-2 rounded">
        ${data.message}
      </div>
    </div>
  `;
  document.querySelector('.chat-messages').insertAdjacentHTML('beforeend', messageHtml);

  // remove from active chats if admin ended it
  if (data.ended_by === 'admin') {
    // keep the input enabled until we receive chat_history_saved
    document.getElementById('endChatBtn').style.display = 'none';
    socket.emit('remove_chat_request', {
        room_id: currentRoom
    });
  } else {
    document.getElementById('adminChatInput').disabled = true;
    document.getElementById('endChatBtn').style.display = 'none';
  }
});

socket.on('saving_chat_history', () => {
  saveStatusDiv.textContent = 'Saving chat history...';
  saveStatusDiv.className = 'save-status mt-2 text-center text-warning';

  const chatMessages = document.querySelector('.chat-messages');
  chatMessages.scrollTop = chatMessages.scrollHeight;
});

socket.on('chat_history_saved', (data) => {
  if (data.error) {
    saveStatusDiv.textContent = 'Error saving chat history';
    saveStatusDiv.className = 'save-status mt-2 text-center text-danger';
  } else {
    saveStatusDiv.textContent = 'Chat history successfully saved';
    saveStatusDiv.className = 'save-status mt-2 text-center text-success';
      
    const currentURL = window.location.pathname;
    if (currentURL.includes('/chat-room/')) {
      document.getElementById('adminChatInput').disabled = true;
    }
  }
  
  const chatMessages = document.querySelector('.chat-messages');
  chatMessages.scrollTop = chatMessages.scrollHeight;
  
  // hide the message after 5 seconds
  setTimeout(() => {
    saveStatusDiv.textContent = '';
    saveStatusDiv.className = 'save-status mt-2 text-center';
      
    // redirect admin back to chat list after successful save if they ended the chat
    if (!data.error && currentURL.includes('/chat-room/')) {
      window.location.href = '/dashboard/customer-chat';
    }
  }, 5000);
});

socket.on('join_error', (data) => {
  window.location.href = '/dashboard/customer-chat';
});

// Typing indicators
socket.on('customer_typing', () => {
  const chatMessages = document.querySelector('.chat-messages');
  let typingIndicator = document.querySelector('.typing-indicator');
  
  if (!typingIndicator) {
    const indicatorHtml = `
      <div class="message incoming typing-indicator">
        <div class="message-content">
          Customer is typing...
        </div>
      </div>
    `;
    chatMessages.insertAdjacentHTML('beforeend', indicatorHtml);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
});

socket.on('customer_stopped_typing', () => {
  const typingIndicator = document.querySelector('.typing-indicator');
  if (typingIndicator) {
    typingIndicator.remove();
  }
});