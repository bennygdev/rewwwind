const socket = io();

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