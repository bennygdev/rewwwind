document.addEventListener('DOMContentLoaded', function() {
  const marketingEmailsCheckbox = document.getElementById('marketingEmails');
  
  if (marketingEmailsCheckbox) {
    marketingEmailsCheckbox.addEventListener('change', handleMarketingEmailsToggle);
  }
});

function handleMarketingEmailsToggle(e) {
  fetch('/dashboard/settings/toggle-marketing-emails', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
    },
    body: JSON.stringify({
      subscribed: e.target.checked
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      const message = e.target.checked ? 
        'Successfully subscribed to marketing emails' : 
        'Successfully unsubscribed from marketing emails';
    } else {
      e.target.checked = !e.target.checked;
    }
  })
  .catch(error => {
    console.error('Error:', error);
    e.target.checked = !e.target.checked; // Revert the checkbox state
  });
}