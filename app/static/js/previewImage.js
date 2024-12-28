const fileInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');
const removeImageButton = document.getElementById('removeImageButton');
const removeImageInput = document.getElementById('remove_image');

// when a new file is selected
fileInput.addEventListener('change', function(event) {
  const file = event.target.files[0];

  if (file) {
    const reader = new FileReader();

    reader.onload = function(e) {
      imagePreview.src = e.target.result;
      imagePreview.style.display = 'block'; 
    };
    
    reader.readAsDataURL(file);
    removeImageInput.value = '';  // clear the "remove" state, because a new image is uploaded
  }
});

// when remove image is clicked
removeImageButton.addEventListener('click', function() {
  imagePreview.style.display = 'none';
  removeImageInput.value = 'remove';
  fileInput.value = '';
});
