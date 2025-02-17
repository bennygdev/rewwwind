document.addEventListener('DOMContentLoaded', function () {
    if (window.location.href.includes('/products')) {
        const dragDropArea = document.getElementById('drag-drop-area');
        const fileInput = document.getElementById('file-input');
        const previewImage = document.getElementById('preview-image');
        const previewText = document.getElementById('preview-text');
        const uploadForm = document.getElementById('upload-form');
      
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
          dragDropArea.addEventListener(eventName, preventDefaults, false);
        });
      
        function preventDefaults(e) {
          e.preventDefault();
          e.stopPropagation();
        }
      
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
          dragDropArea.addEventListener(eventName, () => dragDropArea.classList.add('highlight'), false);
        });
      
        ['dragleave', 'drop'].forEach(eventName => {
          dragDropArea.addEventListener(eventName, () => dragDropArea.classList.remove('highlight'), false);
        });
      
        // Handle dropped files
        dragDropArea.addEventListener('drop', handleDrop, false);
      
        function handleDrop(e) {
          const files = e.dataTransfer.files;
          if (files.length > 0) {
            handleFile(files[0]);
          }
        }
      
        // Handle file input
        fileInput.addEventListener('change', function () {
          if (this.files && this.files[0]) {
            handleFile(this.files[0]);
          }
        });
      
        // Handle file and display preview
        function handleFile(file) {
          if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function (e) {
              previewImage.src = e.target.result;
              previewImage.style.display = 'block';
              previewText.style.display = 'none';
            };
            reader.readAsDataURL(file);
          } else {
            alert('Please upload an image file.');
          }
        }
    }

    const btn = document.getElementById('image_search');
    const overlay = document.getElementById('overlay');
    const modal = document.getElementById('modal');
    const prev = localStorage.getItem('toggleImg');

    btn.addEventListener('click', () => test());

    if (prev == '1') {
        btn.click()
    }

    function test() {
        if (window.location.href.includes('/products')) {
            localStorage.setItem('toggleImg', '0')
            overlay.style.display = 'block';
            modal.style.display = 'flex';
        } else {
            const targCon = document.querySelector('.search__wrapper form');
            const targ = targCon.getAttribute('action');
            localStorage.setItem('toggleImg', '1');
            window.location.href = targ;
        }
    }

    if (overlay && modal) {
        const closeBtn1 = document.querySelector('.modal .success .bi-x-lg');
        const closeBtn2 = document.querySelector('.modal .success .button-wrapper input');
        const btns = [closeBtn1, closeBtn2]
        btns.forEach(btn => {
            btn.addEventListener('click', () => {
                overlay.style.display = 'none';
                modal.style.display = 'none';
                previewImage.src = '#';
                previewImage.style.display = 'none';
                previewText.style.display = 'block';
            })
        });

        document.addEventListener('keydown', (e) => {
            if (e.key == 'Escape') {
                overlay.style.display = 'none';
                modal.style.display = 'none';
                previewImage.src = '#';
                previewImage.style.display = 'none';
                previewText.style.display = 'block';
            }
        });
    };
});