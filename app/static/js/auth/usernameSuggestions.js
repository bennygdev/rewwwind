function generateUsername(baseText) {
  if (!baseText || baseText.length < 3) return null;
  
  // remove special characters and spaces, keep alphanumeric
  const cleanText = baseText.replace(/[^a-zA-Z0-9]/g, '');
  
  const getRandomNumber = () => Math.floor(Math.random() * 900) + 100;
  
  return `${cleanText}-${getRandomNumber()}`;
}

function createSuggestionButton(suggestion, inputField) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'username-suggestion-btn';
  button.textContent = suggestion;
  
  button.addEventListener('click', () => {
    inputField.value = suggestion;
    // Trigger validation if needed
    inputField.dispatchEvent(new Event('input'));
  });
  
  return button;
}

let debounceTimer;
let lastValue = '';

document.addEventListener('DOMContentLoaded', () => {
  const usernameField = document.querySelector('#username');
  
  // create suggestions container if it doesnt exist
  let suggestionsContainer = document.querySelector('.username-suggestions-wrapper');
  if (!suggestionsContainer) {
    suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'username-suggestions-wrapper';
    
    // create label
    const label = document.createElement('div');
    label.className = 'suggestions-label';
    label.textContent = 'Suggestions:';
    suggestionsContainer.appendChild(label);
    
    // create suggestions container
    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'username-suggestions';
    suggestionsContainer.appendChild(buttonsContainer);
    
    usernameField.parentNode.insertBefore(suggestionsContainer, 
      usernameField.nextSibling);
  }
  
  usernameField.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    
    const baseText = e.target.value.trim();
    const buttonsContainer = document.querySelector('.username-suggestions');
    
    if (baseText.length < 3) {
      buttonsContainer.innerHTML = '';
      document.querySelector('.suggestions-label').style.display = 'none';
      return;
    }
    
    // only generate new suggestions if the input has changed
    if (baseText === lastValue) return;
    lastValue = baseText;
    
    // generating indicator
    buttonsContainer.innerHTML = `
      <div class="generating-wrapper">
        <div class="spinner"></div>
        <p class="generating-text">Generating suggestions...</p>
      </div>
    `;
    document.querySelector('.suggestions-label').style.display = 'block';
    
    // debounce the generation to avoid too many updates
    debounceTimer = setTimeout(() => {
      buttonsContainer.innerHTML = '';
      
      // generate 3 unique suggestions
      const suggestions = new Set();
      while (suggestions.size < 3) {
        const suggestion = generateUsername(baseText);
        if (suggestion) suggestions.add(suggestion);
      }
      
      // create and append buttons
      suggestions.forEach(suggestion => {
        const button = createSuggestionButton(suggestion, usernameField);
        buttonsContainer.appendChild(button);
      });
    }, 500);
  });
});