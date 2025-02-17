function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// user search functionality
function setupSearch(options) {
  const {
    searchInput,
    searchResults,
    selectedContainer,
    selectedId,
    errorSpan,
    searchEndpoint,
    formatResult,
    formatSelected
  } = options;

  const performSearch = debounce(async (query) => {
    if (query.length < 2) {
      searchResults.style.display = 'none';
      return;
    }

    try {
      const response = await fetch(`/dashboard/api/${searchEndpoint}?q=${encodeURIComponent(query)}`);
      const data = await response.json();

      searchResults.innerHTML = '';
          
      if (data.length === 0) {
        searchResults.innerHTML = '<div class="search__result">No result found</div>';
      } else {
        data.forEach(item => {
          const div = document.createElement('div');
          div.className = 'search__result';
          div.innerHTML = formatResult(item);
          div.addEventListener('click', () => selectItem(item));
          searchResults.appendChild(div);
        });
      }
          
      searchResults.style.display = 'block';
    } catch (error) {
      console.error('Search error:', error);
    }
  }, 300);

  function selectItem(item) {
    selectedId.value = item.id;
    searchInput.value = '';
    searchResults.style.display = 'none';
      
    selectedContainer.innerHTML = `
      <div>
        ${formatSelected(item)}
        <button type="button" class="selected__button" onclick="clearSelected('${options.clearFunction}')"><i class="fa-solid fa-xmark"></i></button>
      </div>
    `;
    selectedContainer.style.display = 'block';
    errorSpan.style.display = 'none';
  }

  searchInput.addEventListener('input', (e) => performSearch(e.target.value));

  // close search results when clicking outside
  document.addEventListener('click', (e) => {
    if (!searchResults.contains(e.target) && e.target !== searchInput) {
      searchResults.style.display = 'none';
    }
  });

  return { selectItem };
}

// setup user search
const userSearch = setupSearch({
  searchInput: document.getElementById('userSearch'),
  searchResults: document.getElementById('userSearchResults'),
  selectedContainer: document.getElementById('selectedUser'),
  selectedId: document.getElementById('selectedUserId'),
  errorSpan: document.getElementById('userError'),
  searchEndpoint: 'search-users',
  formatResult: user => `${user.username} (${user.email})`,
  formatSelected: user => `<strong>Selected User:</strong> ${user.username} (${user.email})`,
  clearFunction: 'user'
});

// setup voucher search
const voucherSearch = setupSearch({
  searchInput: document.getElementById('voucherSearch'),
  searchResults: document.getElementById('voucherSearchResults'),
  selectedContainer: document.getElementById('selectedVoucher'),
  selectedId: document.getElementById('selectedVoucherId'),
  errorSpan: document.getElementById('voucherError'),
  searchEndpoint: 'search-vouchers',
  formatResult: voucher => `${voucher.code} - ${voucher.description}`,
  formatSelected: voucher => `<strong>Selected Voucher:</strong> ${voucher.code} (${voucher.type})`,
  clearFunction: 'voucher'
});

// clear selection functions
window.clearSelected = function(type) {
  if (type === 'user') {
    document.getElementById('selectedUserId').value = '';
    document.getElementById('selectedUser').style.display = 'none';
    document.getElementById('userSearch').value = '';
  } else if (type === 'voucher') {
    document.getElementById('selectedVoucherId').value = '';
    document.getElementById('selectedVoucher').style.display = 'none';
    document.getElementById('voucherSearch').value = '';
  }
};

// Form submission
document.getElementById('giftVoucherForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  if (!document.getElementById('selectedUserId').value) {
    document.getElementById('userError').textContent = 'Please select a user';
    document.getElementById('userError').style.display = 'block';
    return;
  }
  
  if (!document.getElementById('selectedVoucherId').value) {
    document.getElementById('voucherError').textContent = 'Please select a voucher';
    document.getElementById('voucherError').style.display = 'block';
    return;
  }
  
  const formData = new FormData(this);
  
  try {
    const response = await fetch('/dashboard/api/gift-voucher', {
      method: 'POST',
      body: formData
    });
      
    const data = await response.json();
      
    if (data.success) {
      const successMessage = document.createElement('div');
      successMessage.className = 'success__message';
      successMessage.textContent = data.message;
      this.appendChild(successMessage);
          
      // reset form and selected items
      this.reset();
      clearSelected('user');
      clearSelected('voucher');
          
      setTimeout(() => {
        successMessage.remove();
      }, 5000);
    } else {
      const errorMessage = document.createElement('div');
      errorMessage.className = 'error__message';
      errorMessage.textContent = data.message;
      this.appendChild(errorMessage);
          
      setTimeout(() => {
        errorMessage.remove();
      }, 5000);
    }
  } catch (error) {
    console.error('Error:', error);
  }
});

// pass chat context via URL parameters
function navigateWithChatContext(customerId, customerName, customerEmail, chatDate, supportType, chatId) {
  const params = new URLSearchParams({
    customerId: customerId,
    customerName: customerName,
    customerEmail: customerEmail,
    chatDate: chatDate,
    supportType: supportType,
    chatId: chatId,
    fromChat: 'true'
  });
  
  window.location.href = `/dashboard/gift-voucher?${params.toString()}`;
}

function displayChatContext() {
  const params = new URLSearchParams(window.location.search);
  
  // only show context if coming from chat history
  if (params.get('fromChat') === 'true') {
    const contextDiv = document.createElement('div');
    contextDiv.className = 'chat-context';
    
    contextDiv.innerHTML = `
      <div class="chat-context__container">
        <h3>Chat Context</h3>
        <div class="chat-context__details">
          <p><strong>Customer:</strong> ${params.get('customerName')} (${params.get('customerEmail')})</p>
          <p><strong>Chat Date:</strong> ${params.get('chatDate')}</p>
          <p><strong>Support Type:</strong> ${params.get('supportType')}</p>
          <p><a href="/dashboard/chat-history/${params.get('chatId')}" class="chat-context__link">
            <i class="fa-solid fa-arrow-up-right-from-square"></i> View Chat History
          </a></p>
        </div>
      </div>
    `;
    
    // Insert after the form
    const form = document.getElementById('giftVoucherForm');
    form.parentNode.insertBefore(contextDiv, form.nextSibling);
    
    // Auto-select the customer in the search
    const userSearchInput = document.getElementById('userSearch');
    if (userSearchInput) {
      const selectEvent = {
        id: params.get('customerId'),
        username: params.get('customerName'),
        email: params.get('customerEmail')
      };
      userSearch.selectItem(selectEvent);
    }
  }
}

if (document.getElementById('giftVoucherForm')) {
  displayChatContext();
}