const voucherData = {
  // Vinyl Exclusive Vouchers
  'VINYLSHIP': {
    title: 'Free Shipping on Vinyl',
    description: 'Enjoy free shipping on any vinyl record purchase above $50. Perfect for building your collection!',
    type: 'free_shipping',
    icon: 'fa-truck',
    criteria: [
      'Buy at least 3 vinyl items.'
    ],
    validity: '30 days',
    terms: [
      'Minimum purchase of $50 on vinyl records',
      'One-time use per customer',
      'Cannot be combined with other shipping offers',
      'Excludes international shipping',
      'Valid only for vinyl records category'
    ]
  },
  'VINYL25': {
    title: '25% Off Vinyl',
    description: 'Get 25% off on your vinyl purchase. Maximum discount of $30.',
    type: 'percentage',
    icon: 'fa-percent',
    criteria: [
      'Buy at least $30 worth of vinyl items.'
    ],
    validity: '14 days',
    terms: [
      'Maximum discount capped at $30',
      'One-time use per customer',
      'Cannot be combined with other percentage discounts',
      'Discount applies before shipping and taxes',
      'Valid only for vinyl records category'
    ]
  },
  'VINYLNEW15': {
    title: '$15 Off New Releases',
    description: 'Save $15 on any new release vinyl record. Minimum purchase of $75 required.',
    type: 'fixed_amount',
    icon: 'fa-tag',
    criteria: [
      'Buy at least 3 vinyl items',
      'Minimum purchase of $20'
    ],
    validity: '7 days',
    terms: [
      'Minimum purchase of $75',
      'One-time use per customer',
      'Valid only on new release vinyl records, and must have least one new release vinyl',
      'Cannot be combined with other discounts',
      'Subject to new release availability',
      'Valid only for vinyl records category',
      'Valid only on vinyl records released within the last 30 days'
    ]
  },
  'VINYL2FOR1': {
    title: 'Buy 1 Get 1 50% Off',
    description: 'Buy any vinyl and get 50% off on your second vinyl of equal or lesser value.',
    type: 'percentage',
    icon: 'fa-gift',
    criteria: [
      'Spend over $120'
    ],
    validity: '30 days',
    terms: [
      'Must purchase two or more vinyl records',
      'One-time use per customer',
      'Discount applies to equal or lesser value item',
      'Cannot be combined with other offers',
      'Valid only for vinyl records category'
    ]
  },

  // Book Lovers' Specials
  'BOOKWORM20': {
    title: '20% Off Books',
    description: 'Enjoy 20% off on all books. Perfect for expanding your reading collection!',
    type: 'percentage',
    icon: 'fa-book',
    criteria: [
      'Buy at least 3 books'
    ],
    validity: '30 days',
    terms: [
      'Maximum discount of $50',
      'One-time use per customer',
      'Cannot be combined with other percentage discounts',
      'Excludes pre-orders',
      'Valid for books only'
    ]
  },
  'BOOKSHIP': {
    title: 'Free Book Shipping',
    description: 'Free shipping on any book order above $35. Stock up on your reading list!',
    type: 'free_shipping',
    icon: 'fa-truck',
    criteria: [
      'Spend at least $30 on Books'
    ],
    validity: '14 days',
    terms: [
      'Minimum purchase of $50 on books',
      'One-time use per customer',
      'Cannot be combined with other shipping offers',
      'Excludes international shipping',
      'Valid only for book category'
    ]
  },
  'BOOK10OFF': {
    title: '$10 Off Books',
    description: 'Take $10 off when you spend $50 or more on books.',
    type: 'fixed_amount',
    icon: 'fa-tag',
    criteria: [
      'Spend at least $50 on Books'
    ],
    validity: '30 days',
    terms: [
      'Minimum purchase of $50 on books',
      'One-time use per customer',
      'Cannot be combined with other discounts',
      'Valid for books only',
      'Excludes gift cards and special editions'
    ]
  },
  'BOOKNEW': {
    title: '15% Off New Releases',
    description: 'Get 15% off on all new release books. Stay current with the latest titles!',
    type: 'percentage',
    icon: 'fa-gift',
    criteria: [
      'Spend at least $100 on Books'
    ],
    validity: '21 days',
    terms: [
      'Maximum discount of $30',
      'One-time use per customer',
      'Valid only on new release books',
      'Cannot be combined with other offers',
      'Subject to new release availability'
    ]
  },

  // Special Vouchers
  'FIRSTOFF10': {
    title: '10% Off Your First Order',
    description: 'Enjoy 10% off on your first order. Start your journey at Rewwwind!',
    type: 'percentage',
    icon: 'fa-book',
    criteria: [
      'Sign up for a Rewwwind account'
    ],
    validity: '30 days',
    terms: [
      'Maximum discount of $50',
      'Valid only for first-time customers',
      'One-time use only',
      'Cannot be combined with other offers',
      'Valid on all categories',
      'Must be used on first purchase'
    ]
  },
  'FREESHIP': {
    title: 'Free Shipping',
    description: 'Free shipping on your order above $50. Stock up on your reading list!',
    type: 'free_shipping',
    icon: 'fa-truck',
    criteria: [
      'Buy at least $50 worth of items'
    ],
    validity: '14 days',
    terms: [
      'Minimum purchase of $50',
      'One-time use per customer',
      'Cannot be combined with other shipping offers',
      'Excludes international shipping',
      'Standard shipping only'
    ]
  },
  'GET10OFF': {
    title: '$15 Off Your Order',
    description: 'Take $15 off when you spend $100 or more.',
    type: 'fixed_amount',
    icon: 'fa-tag',
    criteria: [
      'Spend at least $100'
    ],
    validity: '30 days',
    terms: [
      'Minimum purchase of $100',
      'One-time use per customer',
      'Cannot be combined with other discounts',
      'Excludes gift cards',
      'Valid on full-priced items only'
    ]
  },
  'SPECIAL15': {
    title: '15% Off New Releases',
    description: 'Get 15% off on all new specials. Stay current with the latest titles!',
    type: 'percentage',
    icon: 'fa-gift',
    criteria: [
      'Buy at least 5 items.'
    ],
    validity: '21 days',
    terms: [
      'Maximum discount of $25',
      'One-time use per customer',
      'Valid only on items marked as "Special"',
      'Cannot be combined with other offers',
      'Subject to availability'
    ]
  }
};

function openVoucherModal(code) {
  const voucher = voucherData[code];
  if (!voucher) return;

  document.getElementById('modalVoucherCode').textContent = code;
  document.getElementById('modalVoucherTitle').textContent = voucher.title;
  document.getElementById('modalVoucherDescription').textContent = voucher.description;
  
  const criteriaList = document.getElementById('modalVoucherCriteria');
  criteriaList.innerHTML = voucher.criteria.map(item => `<li>${item}</li>`).join('');
  
  document.getElementById('modalVoucherValidity').textContent = voucher.validity;
  
  const termsList = document.getElementById('modalVoucherTerms');
  termsList.innerHTML = voucher.terms.map(item => `<li>${item}</li>`).join('');
  
  toggleVoucherModal();
}

function toggleVoucherModal() {
  const modal = document.getElementById('voucherModal');
  modal.style.display = modal.style.display === 'flex' ? 'none' : 'flex';
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('voucherModal');
  const modalBox = modal.querySelector('.modal-box');

  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      toggleVoucherModal();
    }
  });

  modalBox.addEventListener('click', (e) => {
    e.stopPropagation();
  });
});