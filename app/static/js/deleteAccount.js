let currentFormId = null;

function openDeleteModal(accountId) {
  currentFormId = `deleteForm-${accountId}`;
  toggleModal();
}

function toggleModal() {
  const modal = document.getElementById('deleteModal');
  modal.style.display = modal.style.display === 'flex' ? 'none' : 'flex';
}

function confirmDelete() {
  if (currentFormId) {
    document.getElementById(currentFormId).submit();
  }
  toggleModal();
}