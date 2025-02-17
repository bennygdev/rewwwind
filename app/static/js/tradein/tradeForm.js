document.addEventListener("DOMContentLoaded", function () {
    console.log("tradeForm.js is loaded!");

    const inputFile = document.querySelector("#file-input");
    const fullImagePreview = document.querySelector("#full-image-preview");
    const fullImagePreviewContainer = document.querySelector("#full-image-preview-container");
    const previewContainer = document.querySelector("#preview-container");
    const imagePathsInput = document.querySelector("#image_paths");

    let images = [];
    let imageFiles = [];
    let currentIndex = 0;

    inputFile.addEventListener("change", function () {
        images = Array.from(this.files);
        imageFiles = [...images]; 
        currentIndex = 0;
        updatePreview();
    });

    function updatePreview() {
        previewContainer.innerHTML = "";

        images.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = function () {
                const imgWrapper = document.createElement("div");
                imgWrapper.classList.add("image-wrapper");

                const img = document.createElement("img");
                img.src = reader.result;
                img.classList.add("preview-image");
                img.dataset.index = index;
                img.addEventListener("click", () => showFullImage(index));

                const deleteBtn = document.createElement("button");
                deleteBtn.innerHTML = "&times;";
                deleteBtn.classList.add("delete-image-btn");
                deleteBtn.addEventListener("click", function (event) {
                    event.stopPropagation();
                    removeImage(index);
                });

                imgWrapper.appendChild(img);
                imgWrapper.appendChild(deleteBtn);
                previewContainer.appendChild(imgWrapper);
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
                fullImagePreviewContainer.classList.remove("hidden");
            };
            reader.readAsDataURL(images[index]);
        }
    }

    function removeImage(index) {
        images.splice(index, 1);
        imageFiles.splice(index, 1);

        if (images.length === 0) {
            fullImagePreview.classList.add("hidden");
            fullImagePreviewContainer.classList.add("hidden");
        }

        updatePreview();
        imagePathsInput.value = JSON.stringify(images.map(file => file.name));
    }

    previewContainer.addEventListener("click", function (event) {
        if (event.target.classList.contains("preview-image")) {
            showFullImage(event.target.dataset.index);
        }
    });

    fullImagePreviewContainer.addEventListener("click", function () {
        fullImagePreviewContainer.classList.add("hidden");
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            fullImagePreviewContainer.classList.add("hidden");
        }
    });
});
