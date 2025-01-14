const socket = io();
let currentRoom = null;

// Add chat controls to header
document.querySelector('.chat-header').innerHTML += `
  <div class="chat-controls">
    <button class="btn btn-secondary" id="backBtn">Back</button>
    <button class="btn btn-danger" id="endChatBtn">End Chat</button>
  </div>
`;

// Handle back button
document.getElementById('backBtn').addEventListener('click', () => {
  if (currentRoom) {
    socket.emit('admin_leave_chat', {
      room_id: currentRoom
    });
  }
  resetAdminChat();
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

function resetAdminChat() {
  currentRoom = null;
  document.getElementById('chatArea').classList.add('d-none');
  document.getElementById('noChatSelected').classList.remove('d-none');
  document.querySelector('.chat-messages').innerHTML = '';
}

// Handle new chat requests
socket.on('new_chat_request', (data) => {
  const requestHtml = `
    <div class="chat-request-card mb-3 p-3 border rounded" data-room-id="${data.room_id}">
      <div class="d-flex justify-content-between align-items-center">
        <h5 class="mb-1">${data.customer_name}</h5>
        <small>${data.start_time}</small>
      </div>
      <button class="btn btn-primary btn-sm join-chat" data-room-id="${data.room_id}" data-customer="${data.customer_name}">
        Join Chat
      </button>
    </div>
  `;
  document.querySelector('.chat-requests').insertAdjacentHTML('afterbegin', requestHtml);
});

socket.on('remove_chat_request', (data) => {
  const requestCard = document.querySelector(`.chat-request-card[data-room-id="${data.room_id}"]`);
  if (requestCard) {
      requestCard.remove();
  }
});

// Join chat functionality
document.querySelector('.chat-requests').addEventListener('click', (e) => {
  if (e.target.classList.contains('join-chat')) {
    const roomId = e.target.dataset.roomId;
    const customerName = e.target.dataset.customer;
            
    socket.emit('admin_join_chat', { room_id: roomId });
    currentRoom = roomId;
            
    // Update UI
    document.getElementById('chatArea').classList.remove('d-none');
    document.getElementById('noChatSelected').classList.add('d-none');
    document.getElementById('currentCustomer').textContent = `Chat with ${customerName}`;
            
    // Remove the chat request card
    e.target.closest('.chat-request-card').remove();
  }
});

// Handle sending messages
document.getElementById('sendMessage').addEventListener('click', sendMessage);
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
    socket.emit('chat_message', {
      room_id: currentRoom,
      message: message
    });
      
    // Add message to chat
    const messageHtml = `
      <div class="message outgoing mb-3">
        <div class="message-content bg-primary text-white p-2 rounded">
          ${message}
        </div>
      </div>
    `;
    document.querySelector('.chat-messages').insertAdjacentHTML('beforeend', messageHtml);
      
    // Clear input
    messageInput.value = '';
  }
}

// Handle incoming messages
socket.on('new_message', (data) => {
  if (data.sender_type === 'customer') {
    const messageHtml = `
      <div class="message incoming mb-3">
        <div class="message-content bg-light p-2 rounded">
          ${data.message}
        </div>
        <small class="text-muted">${data.timestamp}</small>
      </div>
    `;
    document.querySelector('.chat-messages').insertAdjacentHTML('beforeend', messageHtml);
  }
});

// Handle chat ending
socket.on('chat_ended', (data) => {
  if (currentRoom) {
    // Show end message
    const messageHtml = `
      <div class="message system mb-3">
        <div class="message-content bg-warning text-dark p-2 rounded">
          ${data.message}
        </div>
      </div>
    `;
    document.querySelector('.chat-messages').insertAdjacentHTML('beforeend', messageHtml);
    
    // Remove chat request card if it exists
    const requestCard = document.querySelector(`[data-room-id="${currentRoom}"]`);
    if (requestCard) {
      requestCard.remove();
    }
    
    // Reset chat after delay
    setTimeout(() => {
      resetAdminChat();
    }, 3000);
  }
});

let connectionInterval;
let lastPong = Date.now();

const startConnectionMonitor = () => {
  connectionInterval = setInterval(() => {
    // Check if we've received a pong in the last 10 seconds
    if (Date.now() - lastPong > 10000) {
      handleDisconnection();
    }
    socket.emit('ping_connection');
  }, 5000);
}

handleDisconnection = () => {
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

const resetChat = () => {
  currentRoom = null;
  document.getElementById('chatChoice').style.display = 'block';
  document.querySelector('.chatbox').style.display = 'none';
  document.querySelector('.chat-input').style.display = 'none';
  chatbox.innerHTML = '';
}

// Add event listener for chat history
socket.on('chat_history', (data) => {
  const chatMessages = document.querySelector('.chat-messages');
  chatMessages.innerHTML = ''; // Clear existing messages
  
  data.messages.forEach(msg => {
      const messageHtml = `
          <div class="message ${msg.type === 'outgoing' ? 'outgoing' : 'incoming'} mb-3">
              <div class="message-content ${msg.type === 'outgoing' ? 'bg-primary text-white' : 'bg-light'} p-2 rounded">
                  ${msg.message}
              </div>
              <small class="text-muted">${msg.timestamp}</small>
          </div>
      `;
      chatMessages.insertAdjacentHTML('beforeend', messageHtml);
  });
});

socket.on('customer_left', (data) => {
  // Show message that customer left
  const messageHtml = `
    <div class="message system mb-3">
      <div class="message-content bg-warning text-dark p-2 rounded">
        ${data.message}
      </div>
    </div>
  `;
  document.querySelector('.chat-messages').insertAdjacentHTML('beforeend', messageHtml);
  
  // Remove chat request card if it exists
  const requestCard = document.querySelector(`[data-room-id="${data.room_id}"]`);
  if (requestCard) {
    requestCard.remove();
  }
});