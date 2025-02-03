document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('newsletterForm');
  const submitButton = document.getElementById('submitButton');
  const spinnerContainer = document.getElementById('spinnerContainer');

  form.addEventListener('submit', function(e) {
    e.preventDefault();

    submitButton.disabled = true;
    submitButton.classList.add('newsletter__submit--loading');
    spinnerContainer.classList.remove('hidden');

    const formData = new FormData(form);

    fetch(form.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        window.location.reload();
      } else {
        // Re-enable button and hide spinner on error
        submitButton.disabled = false;
        submitButton.classList.remove('newsletter__submit--loading');
        spinnerContainer.classList.add('hidden');
        alert(data.message || 'Failed to send newsletter');
      }
    })
    .catch(error => {
      // Re-enable button and hide spinner on error
      submitButton.disabled = false;
      submitButton.classList.remove('newsletter__submit--loading');
      spinnerContainer.classList.add('hidden');
      alert('An error occurred while sending the newsletter');
    });
  });
});