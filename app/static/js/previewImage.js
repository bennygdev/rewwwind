const fileInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');

fileInput.addEventListener('change', function(event) {
  const file = event.target.files[0];

  if (file) {
    const reader = new FileReader();

    reader.onload = function(e) {
      imagePreview.src = e.target.result;
    };

    reader.readAsDataURL(file);
  }
});