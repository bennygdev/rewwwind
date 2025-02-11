const socket = io();

// Handle new chat requests
socket.on('new_chat_request', (data) => {
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
document.querySelector('.chat-requests').addEventListener('click', (e) => {
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
    }
  }
});