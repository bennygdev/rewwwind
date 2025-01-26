document.getElementById('unsubscribeBtn').addEventListener('click', function() {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');

  fetch(`/dashboard/unsubscribe/${token}`)
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    const messageEl = document.getElementById('message');
    const btnEl = document.getElementById('unsubscribeBtn');
      
    if (data.success) {
      messageEl.textContent = 'You have been unsubscribed.';
      messageEl.classList.add('text-green-600');
      btnEl.disabled = true;
      btnEl.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
      messageEl.textContent = 'Error: Unable to unsubscribe.';
      messageEl.classList.add('text-red-600');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    const messageEl = document.getElementById('message');
    messageEl.textContent = 'Error: Unable to unsubscribe.';
    messageEl.classList.add('text-red-600');
  });
});