document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('.login__form');
  const submitButton = document.getElementById('resetSubmitButton');
  const spinner = document.getElementById('resetSpinnerContainer');
  const emailField = document.querySelector('input[name="email"]');
  const emailContainer = document.querySelector('.login__email');

  if (form) {
    form.addEventListener('submit', async function(e) {
      e.preventDefault();

      const existingErrors = emailContainer.querySelectorAll('.error');
      existingErrors.forEach(error => error.remove());

      spinner.classList.remove('hidden');
      submitButton.disabled = true;
      submitButton.classList.add('reset__button--loading');

      try {
        const response = await fetch('/reset-password', {
          method: 'POST',
          body: new FormData(form),
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        const data = await response.json();

        if (data.success) {
          window.location.href = '/login';
        } else {
          if (data.errors && data.errors.email) {
            const errorSpan = document.createElement('span');
            errorSpan.className = 'error';
            errorSpan.textContent = data.errors.email[0];
            emailContainer.appendChild(errorSpan);
          } else if (data.message) {
            const errorSpan = document.createElement('span');
            errorSpan.className = 'error';
            errorSpan.textContent = data.message;
            emailContainer.appendChild(errorSpan);
          }
        }
      } catch (error) {
        console.error('Error:', error);
        const errorSpan = document.createElement('span');
        errorSpan.className = 'error';
        errorSpan.textContent = 'An unexpected error occurred. Please try again.';
        emailContainer.appendChild(errorSpan);
      } finally {
        // Hide spinner and enable button
        spinner.classList.add('hidden');
        submitButton.disabled = false;
        submitButton.classList.remove('reset__button--loading');
      }
    });
  }
});