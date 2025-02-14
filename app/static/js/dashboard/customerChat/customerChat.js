const socket = io();

function updateChatRequestsContainer(hasChats) {
  const chatContainer = document.querySelector('.chat-container');
  const existingEmptyState = document.querySelector('.empty-chat-state');
  const existingSidebar = document.querySelector('.chat-sidebar');

  if (!hasChats && !existingEmptyState) {
    // Remove sidebar if it exists
    if (existingSidebar) {
      existingSidebar.remove();
    }
    
    // Add empty state
    const emptyState = `
      <div class="empty-chat-state">
        <img src="/static/media/chat-empty.png" alt="No active chats">
        <h2>No Active Chats</h2>
        <p>There are currently no customers waiting for support.</p>
      </div>
    `;
    chatContainer.innerHTML = emptyState;
  } else if (hasChats && !existingSidebar) {
    // Remove empty state if it exists
    if (existingEmptyState) {
      existingEmptyState.remove();
    }
    
    // Add sidebar with chat requests
    const sidebar = `
      <div class="chat-sidebar">
        <div class="chat-requests"></div>
      </div>
    `;
    chatContainer.innerHTML = sidebar;
  }
}

// Handle new chat requests
socket.on('new_chat_request', (data) => {
  let chatRequests = document.querySelector('.chat-requests');
  
  // If we don't have a chat requests container, create the sidebar structure
  if (!chatRequests) {
    updateChatRequestsContainer(true);
    chatRequests = document.querySelector('.chat-requests');
  }

  const existingCard = document.querySelector(`.chat-request-card[data-room-id="${data.room_id}"]`);
  if (existingCard) {
    existingCard.remove();
  }

  const supportTypeLabels = {
    'technical': 'Technical Support',
    'billing': 'Billing Support',
    'account': 'Account Support',
    'general': 'General Inquiry'
  };

  const requestHtml = `
    <div class="chat-request-card" data-room-id="${data.room_id}">
      <div class="chat-request-header">
        <h5>${data.customer_name}</h5>
        <span class="status-badge status-waiting">
          Waiting
        </span>
        <small>${data.start_time}</small>
      </div>
      <div class="support-type">
        <p>Support Type: ${supportTypeLabels[data.supportType] || 'General Inquiry'}</p>
      </div>
      <button class="join-chat-btn" data-room-id="${data.room_id}" data-customer="${data.customer_name}">
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
    
    // Check if there are any remaining chat requests
    const remainingRequests = document.querySelectorAll('.chat-request-card');
    if (remainingRequests.length === 0) {
      updateChatRequestsContainer(false);
    }
  }
});

socket.on('room_status_update', (data) => {
  const requestCards = document.querySelectorAll(`.chat-request-card[data-room-id="${data.room_id}"]`);
  
  // if we found multiple cards with the same room_id, remove duplicates
  if (requestCards.length > 1) {
    // keep only the first one and remove others
    for (let i = 1; i < requestCards.length; i++) {
      requestCards[i].remove();
    }
  }
  
  const requestCard = requestCards[0];
  if (requestCard) {
    const joinBtn = requestCard.querySelector('.join-chat-btn');
    const statusBadge = requestCard.querySelector('.status-badge') || document.createElement('span');
    statusBadge.className = `status-badge status-${data.status}`;
      
    if (data.status === 'active') {
      requestCard.classList.add('active');
      joinBtn.disabled = true;
      statusBadge.textContent = `Active - ${data.admin_name}`;
      if (!requestCard.querySelector('.status-badge')) {
        requestCard.querySelector('.chat-request-header').appendChild(statusBadge);
      }
    } else {
      requestCard.classList.remove('active');
      joinBtn.disabled = false;
      statusBadge.textContent = 'Waiting';
      if (!requestCard.querySelector('.status-badge')) {
        requestCard.querySelector('.chat-request-header').appendChild(statusBadge);
      }
    }
  }
});

// Join chat functionality
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('join-chat-btn') && !e.target.disabled) {
    const roomId = e.target.dataset.roomId;
    window.location.href = `/dashboard/chat-room/${roomId}`;
  }
});

socket.on('connect', () => {
  console.log('Socket connected on admin page');
});

socket.on('disconnect', () => {
  console.log('Socket disconnected on admin page');
});

socket.on('chat_ended', (data) => {
  console.log('Chat ended event received:', data);
  if (data.ended_by === 'admin' || data.ended_by === 'customer') {
    const requestCard = document.querySelector(`.chat-request-card[data-room-id="${data.room_id}"]`);
    if (requestCard) {
      requestCard.remove();

      const remainingRequests = document.querySelectorAll('.chat-request-card');
      if (remainingRequests.length === 0) {
        updateChatRequestsContainer(false);
      }
    }
  }
});