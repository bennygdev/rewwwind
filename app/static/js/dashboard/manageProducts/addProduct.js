class Form {
    constructor(formSelector, submitUrl) {
        this.form = document.querySelector(formSelector);
        this.submitUrl = submitUrl;
        this.formData = new FormData();

        this.init();
    }

    // Initialize event listeners
    init() {
        this.form.addEventListener('submit', (event) => this.handleSubmit(event));
    }

    // Prepare form data
    prepareFormData() {
        const formElements = this.form.querySelectorAll('input, select, textarea');
        formElements.forEach(element => {
            if (element.name && !['productImages', 'productThumbnail', /^productConditions.*/].includes(element.name)) {
                element.type === 'checkbox' ? 
                element.checked ? this.formData.append(element.name, element.value) : this.formData.append(element.name, 'false') :
                this.formData.append(element.name, element.value);
            }
        });
        return this.formData;
    }

    // Handle form submission
    async handleSubmit(event) {
        event.preventDefault();

        const formData = this.prepareFormData();

        try {
            const response = await fetch(this.submitUrl, {
                method: 'POST',
                body: formData,
            });

            const contentType = response.headers.get("Content-Type");

            if (contentType && contentType.includes("application/json")) {
                const result = await response.json();
                const flashContainer = document.querySelector('.flash-messages');
                flashContainer.innerHTML = '';

                if (result.success) {
                    this.displayFlashMessage(result.message, 'success');
                    window.location.href = '../manage-products';
                } else {
                    this.displayFlashMessage(result.message, 'error');
                    this.resetForm();
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            this.displayFlashMessage("An unexpected error occurred.", 'error');
        }
    }

    resetForm() {
        this.formData = new FormData();
    }

    // Display flash messages
    displayFlashMessage(message, category) {
        const flashContainer = document.querySelector('.flash-messages');
        const alert = document.createElement('div');
        alert.classList.add('alert', 'alert-dismissible', 'fade', 'show');

        alert.classList.add(category === 'error' ? 'alert-danger' : 'alert-success');
        alert.innerHTML = `
            <strong>${category === 'error' ? 'Error:' : 'Success:'}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        flashContainer.appendChild(alert);
    }
}

class ImageHandler extends Form {
    constructor(fileInputName, formSelector, submitUrl, is_update) {
        super(formSelector, submitUrl);
        this.fileInputName = fileInputName;
        this.fileInput = this.form.querySelector(`input[name="${this.fileInputName}"]`);
        this.label = this.form.querySelector(`label[for="${this.fileInput.id}"]`);
        this.labelImg = null;
        this.fileList = [];
        this.visibleImages = [];
        this.maxVisibleImages = 5;
        this.currentIndex = 0; // Track the starting index of visible images
        this.activeImageIndex = 0; // Track the index of the active image within visible images
        this.productThumbnail = this.form.querySelector('input[name="productThumbnail"]');
        this.fileListDisplay = this.form.querySelector('.file-list');

        this.update = is_update;

        this.initImageHandling();
    }

    initImageHandling() {
        if (this.update) {
            const images = document.getElementById('images').getAttribute('images').replace('[', '').replace(']', '').replaceAll(" ", "").replaceAll("'", "").split(',')
            this.fileList = images;
            this.updateVisibleImages();
            this.update = !this.update;
            console.log(this.update)
        }

        if (this.fileInput) {
            this.fileInput.addEventListener('change', (event) => this.handleFileSelect(event));
        }

        if (this.label) {
            this.label.addEventListener('dragover', (event) => this.handleDragOver(event));
            this.label.addEventListener('dragleave', () => this.handleDragLeave());
            this.label.addEventListener('drop', (event) => this.handleFileDrop(event));
        }

        // Add event listeners for carousel arrows
        document.querySelector('.carousel-button.left').addEventListener('click', () => this.shiftLeft());
        document.querySelector('.carousel-button.right').addEventListener('click', () => this.shiftRight());
    }

    handleDragOver(event) {
        event.preventDefault();
        this.label.classList.add('drag-over');
    }

    handleDragLeave() {
        this.label.classList.remove('drag-over');
    }

    handleFileDrop(event) {
        event.preventDefault();
        this.label.classList.remove('drag-over');

        const files = Array.from(event.dataTransfer.files);
        this.processFiles(files);
    }

    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        this.processFiles(files);
        event.target.value = ''; // Reset input
    }

    processFiles(files) {
        this.fileList = this.fileList.concat(files);
        this.updateVisibleImages();
    }

    updateVisibleImages() {
        this.visibleImages = this.fileList.slice(this.currentIndex, this.currentIndex + this.maxVisibleImages);
        this.renderFileList();
    }

    renderFileList() {
        this.fileListDisplay.innerHTML = '';

        if (!this.labelImg) {
            const img = document.createElement('img');
            this.label.appendChild(img);
            this.labelImg = img;
        }
        if (this.fileList.length === 0) {
            this.label.innerHTML = '';
        }
        if (this.fileList.length > 1) {
            document.querySelector('.carousel-button.left').style.display = 'flex';
            document.querySelector('.carousel-button.right').style.display = 'flex';
        } else {
            document.querySelector('.carousel-button.left').style.display = 'none';
            document.querySelector('.carousel-button.right').style.display = 'none';
        }
    
        this.visibleImages.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.classList.add('image__container');
    
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.alt = `Image Preview ${index + 1}`;
                fileItem.appendChild(img);
    
                if (index === this.activeImageIndex) {
                    this.setThumbnail(fileItem, img.src, index);
                }
            };
            if (typeof file !== 'string') {
                reader.readAsDataURL(file)
            } else {
                const img = document.createElement('img');
                img.src = `/static/${file}`;
                img.alt = `Image Preview ${index + 1}`;
                fileItem.appendChild(img);
    
                if (index === this.activeImageIndex) {
                    this.setThumbnail(fileItem, img.src, index);
                }
            }
    
            // Create delete button with icon
            const deleteButton = document.createElement('button');
            deleteButton.classList.add('delete-button');
            deleteButton.innerHTML = '<i class="bi bi-trash-fill"></i>';
            deleteButton.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent triggering image selection
                this.deleteImage(this.currentIndex + index);
            });
    
            fileItem.appendChild(deleteButton);
            this.fileListDisplay.appendChild(fileItem);
    
            fileItem.addEventListener('click', () => this.setThumbnail(fileItem, fileItem.querySelector('img').src, index));
        });
    }

    setThumbnail(fileItem, src, index) {
        this.fileListDisplay.querySelectorAll('.image__container').forEach(item => item.classList.remove('active'));
        fileItem.classList.add('active');
        this.labelImg.src = src;
        this.label.style.backgroundSize = '250px';
        this.productThumbnail.value = this.currentIndex + index;
        this.activeImageIndex = index;
    }
    shiftRight() {
        if (this.fileList.length <= this.maxVisibleImages) {
            // do not trigger carousel when total images are <= maxVisibleImages
            if (this.activeImageIndex < this.fileList.length - 1) {
                this.activeImageIndex++;
                const fileItem = this.fileListDisplay.children[this.activeImageIndex];
                const imgSrc = fileItem.querySelector('img').src;
                this.setThumbnail(fileItem, imgSrc, this.activeImageIndex);
            }
            return;
        }
    
        if (this.activeImageIndex < this.visibleImages.length - 1) {
            // move to next image without triggering the carousel
            this.activeImageIndex++;
            const fileItem = this.fileListDisplay.children[this.activeImageIndex];
            const imgSrc = fileItem.querySelector('img').src;
            this.setThumbnail(fileItem, imgSrc, this.activeImageIndex);
        } else if (this.currentIndex + this.maxVisibleImages < this.fileList.length) {
            // trigger carousel and set the new right-most image as active
            this.currentIndex++;
            this.updateVisibleImages();
            this.activeImageIndex = this.visibleImages.length - 1; // Set to the new right-most image
            const fileItem = this.fileListDisplay.children[this.activeImageIndex];
            const imgSrc = fileItem?.querySelector('img')?.src;
            if (fileItem && imgSrc) this.setThumbnail(fileItem, imgSrc, this.activeImageIndex);
        } else {
            // wrap around to start
            this.currentIndex = 0;
            this.updateVisibleImages();
            this.activeImageIndex = this.currentIndex; // reset to first image
            const fileItem = this.fileListDisplay.children[this.activeImageIndex];
            const imgSrc = fileItem?.querySelector('img')?.src;
            if (fileItem && imgSrc) this.setThumbnail(fileItem, imgSrc, this.activeImageIndex);
        }
    }
    
    shiftLeft() {
        if (this.fileList.length <= this.maxVisibleImages) {
            // do not trigger carousel when total images are <= maxVisibleImages
            if (this.activeImageIndex > 0) {
                // move to the previous image within visible range
                this.activeImageIndex--;
                const fileItem = this.fileListDisplay.children[this.activeImageIndex];
                const imgSrc = fileItem.querySelector('img').src;
                this.setThumbnail(fileItem, imgSrc, this.activeImageIndex);
            }
            return;
        }
    
        if (this.activeImageIndex > 0) {
            // move to previous image without triggering the carousel
            this.activeImageIndex--;
            const fileItem = this.fileListDisplay.children[this.activeImageIndex];
            const imgSrc = fileItem.querySelector('img').src;
            this.setThumbnail(fileItem, imgSrc, this.activeImageIndex);
        } else if (this.currentIndex > 0) {
            // trigger carousel and set the new left-most image as active
            this.currentIndex--;
            this.updateVisibleImages();
            this.activeImageIndex = 0; // set to the new left-most image
            const fileItem = this.fileListDisplay.children[this.activeImageIndex];
            const imgSrc = fileItem?.querySelector('img')?.src;
            if (fileItem && imgSrc) this.setThumbnail(fileItem, imgSrc, this.activeImageIndex);
        } else {
            // wrap around to the end
            this.currentIndex = this.fileList.length - this.maxVisibleImages;
            this.updateVisibleImages();
            this.activeImageIndex = 4; // set to last image
            const fileItem = this.fileListDisplay.children[this.activeImageIndex];
            const imgSrc = fileItem?.querySelector('img')?.src;
            if (fileItem && imgSrc) this.setThumbnail(fileItem, imgSrc, this.activeImageIndex);
        }
    }
    
    // delete image
    deleteImage(index) {
        this.fileList.splice(index, 1);

        if (this.activeImageIndex >= this.fileList.length) {
            this.activeImageIndex = Math.max(0, this.fileList.length - 1);
        }
        if (this.currentIndex > this.fileList.length - this.maxVisibleImages) {
            this.currentIndex = Math.max(0, this.fileList.length - this.maxVisibleImages);
        }
        this.updateVisibleImages();
    }

    // image file specific data preparation
    prepareFormData() {
        const formData = super.prepareFormData();

        this.fileList.forEach(file => formData.append(this.fileInput.name, file));
        formData.append(this.productThumbnail.name, this.productThumbnail.value)

        return formData;
    }  
}

class ConditionHandler extends ImageHandler {
    constructor(fileInputName, formSelector, submitUrl, is_update) {
        super(fileInputName, formSelector, submitUrl, is_update);
        this.conditionsContainer = this.form.querySelector('.product__conditions');
        this.conditionList = Array.from(this.form.querySelectorAll('.condition'));
        this.addConditionBtn = this.form.querySelector('button.addCondition');

        this.initConditionHandler();
    }

    initConditionHandler() {
        this.addConditionBtn.addEventListener('click', () => this.addCondition());
        // Add event listeners to existing delete buttons
        this.conditionList.forEach(condition => {
            const deleteBtn = condition.querySelector('.deleteCondition');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', () => this.deleteCondition(condition));
            }
        });
    }

    addCondition() {
        const newCondition = this.conditionList[0].cloneNode(true);
        newCondition.querySelectorAll('input, select').forEach(item => {
            item.value = '';
            item.id = item.id.replace(/-\d+-(?=\w+$)/, `-${this.conditionList.length}-`);
            item.name = item.id;
        });

        // Update delete button functionality
        const deleteBtn = newCondition.querySelector('.deleteCondition');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => this.deleteCondition(newCondition));
        }

        this.conditionsContainer.insertBefore(newCondition, this.addConditionBtn);
        this.conditionList.push(newCondition);
    }

    deleteCondition(condition) {
        // Remove the condition from the DOM
        this.conditionsContainer.removeChild(condition);
        // Update the condition list
        this.conditionList = this.conditionList.filter(item => item !== condition);
    }

    prepareFormData() {
        const formData = super.prepareFormData();

        this.conditionList.forEach((condition) => {
            condition.querySelectorAll('input, select').forEach(input => {
                formData.append(input.name, input.value);
            });
        });

        return formData;
    }
}

window.location.href.includes('/manage-products/add-product') ?
new ConditionHandler('productImages', 'form', '/dashboard/manage-products/add-product', false) :
new ConditionHandler('productImages', 'form', `/dashboard/manage-products/update-product/${document.getElementById('getIdHere').innerText}`, true);