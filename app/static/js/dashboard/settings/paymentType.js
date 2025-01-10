document.addEventListener('DOMContentLoaded', function() {
  const cardNumberInput = document.querySelector('[name="card_number"]');
  const cvvInput = document.querySelector('[name="card_cvv"]');
  const radioButtons = document.querySelectorAll('[name="paymentType_id"]');

  radioButtons.forEach(radio => {
      radio.addEventListener('change', function() {
          // Reset fields when changing card type
          cardNumberInput.value = '';
          cvvInput.value = '';
          
          // Update maxlength based on card type
          if (this.value === '3') { // Amex
              cardNumberInput.setAttribute('maxlength', '15');
              cvvInput.setAttribute('maxlength', '4');
          } else { // Visa/Mastercard
              cardNumberInput.setAttribute('maxlength', '16');
              cvvInput.setAttribute('maxlength', '3');
          }
      });
  });
});