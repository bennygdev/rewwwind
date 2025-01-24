document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('newsletter__form');
  const emailInput = document.getElementById('newsletter__email');
  const messageDiv = document.getElementById('newsletter__message');

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    fetch(form.action, {
      method: 'POST',
      body: new FormData(form),
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        messageDiv.innerHTML = 'Thank you for subscribing!';
        messageDiv.classList.remove('error');
        messageDiv.classList.add('success');
        emailInput.value = ''; // Clear the input
      } else {
        messageDiv.innerHTML = data.error || 'Subscription failed';
        messageDiv.classList.remove('success');
        messageDiv.classList.add('error');
      }
    })
    .catch(error => {
      messageDiv.innerHTML = 'An error occurred';
      messageDiv.classList.remove('success');
      messageDiv.classList.add('error');
    });
  });
});