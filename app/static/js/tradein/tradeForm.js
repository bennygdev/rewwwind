document.addEventListener("DOMContentLoaded", function () {
    console.log("tradeForm.js is loaded!");

    const inputFile = document.querySelector("#file-input");
    const fullImagePreview = document.querySelector("#full-image-preview");
    const previewContainer = document.querySelector("#preview-container");
    const prevBtn = document.querySelector("#prev-btn");
    const nextBtn = document.querySelector("#next-btn");
    const deleteBtn = document.querySelector("#delete-btn");

    let images = [];
    let currentIndex = 0;

    inputFile.addEventListener("change", function () {
        images = [...this.files];
        currentIndex = 0;
        updatePreview();
    });

    function updatePreview() {
        previewContainer.innerHTML = "";

        images.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = function () {
                const img = document.createElement("img");
                img.src = reader.result;
                img.classList.add("preview-image");
                img.dataset.index = index;
                img.addEventListener("click", () => showFullImage(index));
                previewContainer.appendChild(img);
            };
            reader.readAsDataURL(file);
        });

        if (images.length > 0) {
            showFullImage(currentIndex);
        }
    }

    function showFullImage(index) {
        if (images.length > 0) {
            const reader = new FileReader();
            reader.onload = function () {
                fullImagePreview.src = reader.result;
                fullImagePreview.classList.remove("hidden");
            };
            reader.readAsDataURL(images[index]);
        }
    }

    deleteBtn.addEventListener("click", function () {
        images.splice(currentIndex, 1);
        if (images.length === 0) {
            fullImagePreview.classList.add("hidden");
        }
        updatePreview();
    });

    prevBtn.addEventListener("click", function () {
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        showFullImage(currentIndex);
    });

    nextBtn.addEventListener("click", function () {
        currentIndex = (currentIndex + 1) % images.length;
        showFullImage(currentIndex);
    });
});
