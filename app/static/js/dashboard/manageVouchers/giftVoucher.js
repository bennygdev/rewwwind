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