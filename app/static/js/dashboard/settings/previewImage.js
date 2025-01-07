const fileInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');
const removeImageButton = document.getElementById('removeImageButton');
const removeImageInput = document.getElementById('remove_image');

function updateRemoveButtonVisibility() {
  if (imagePreview.src !== '/static/profile_pics/profile_image_default.jpg') {
    removeImageButton.style.display = 'inline-block';
  } else {
    removeImageButton.style.display = 'none';
  }
}

// when a new file is selected
fileInput.addEventListener('change', (event) => {
  const file = event.target.files[0];

  if (file) {
    const reader = new FileReader();

    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      imagePreview.style.display = 'block';
    };

    reader.readAsDataURL(file);
    removeImageInput.value = '';

    updateRemoveButtonVisibility();
  }
});

// when remove image is clicked
removeImageButton.addEventListener('click', () => {
  imagePreview.src = '/static/profile_pics/profile_image_default.jpg';
  removeImageInput.value = 'remove';
  fileInput.value = '';

  removeImageButton.style.display = 'none';
});
