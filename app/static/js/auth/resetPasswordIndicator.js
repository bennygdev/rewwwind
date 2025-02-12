document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('.login__form');
  const submitButton = document.querySelector('.reset__button');
  const spinnerContainer = document.createElement('span');
  spinnerContainer.id = 'resetSpinnerContainer';
  spinnerContainer.className = 'spinner hidden';
  submitButton.appendChild(spinnerContainer);

  form.addEventListener('submit', function(e) {
    e.preventDefault();

    submitButton.disabled = true;
    submitButton.classList.add('reset__button--loading');
    spinnerContainer.classList.remove('hidden');

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
        window.location.href = '/login';
      } else {
        // Re-enable button and hide spinner on error
        submitButton.disabled = false;
        submitButton.classList.remove('reset__button--loading');
        spinnerContainer.classList.add('hidden');
        alert(data.message || 'Failed to send reset email');
      }
    })
    .catch(error => {
      // Re-enable button and hide spinner on error
      submitButton.disabled = false;
      submitButton.classList.remove('reset__button--loading');
      spinnerContainer.classList.add('hidden');
      alert('An error occurred while sending the reset email');
    });
  });
});