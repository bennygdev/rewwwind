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