function toggleEditForm(id) {
  const details = document.getElementById(`details${id}`);
  const form = document.getElementById(`editForm${id}`);
  const editButton = document.getElementById(`editButton${id}`);
  const deleteButton = document.getElementById(`deleteButton${id}`);
  const buttonGroup = document.getElementById(`buttonGroup${id}`);
    
  // toggle visibility of details and form
  if (form.style.display === 'none') {
    details.style.display = 'none';
    form.style.display = 'block';
    editButton.style.display = 'none';
    deleteButton.style.display = 'none';
    buttonGroup.style.display = 'flex';
  } else {
    details.style.display = 'block';
    form.style.display = 'none';
    editButton.style.display = 'inline-block';
    deleteButton.style.display = 'inline-block';
    buttonGroup.style.display = 'none';
  }
}

function clearErrors(formId) {
  const form = document.getElementById(formId);
  const errorMessages = form.getElementsByClassName('error-message');
  while (errorMessages.length > 0) {
      errorMessages[0].remove();
  }
}

function displayErrors(formId, errors) {
  const form = document.getElementById(formId);
  for (const field in errors) {
      const input = form.querySelector(`[name="${field}"]`);
      if (input) {
          const errorDiv = document.createElement('span');
          errorDiv.className = 'error-message';
          errorDiv.textContent = errors[field][0];
          input.parentNode.appendChild(errorDiv);
      }
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const forms = document.querySelectorAll('.editPayment__form');
  
  forms.forEach(form => {
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      const formId = form.id;
      const formData = new FormData(form);
          
      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: formData
        });
              
        const data = await response.json();
              
        clearErrors(formId);
              
        if (data.success) {
          const id = formId.replace('editForm', '');
          toggleEditForm(id);
          location.reload();
        } else {
          if (data.errors) {
            displayErrors(formId, data.errors);
          }
          if (data.message) {
            console.error(data.message);
          }
        }
      } catch (error) {
        console.error('Error:', error);
      }
    });
  });
});