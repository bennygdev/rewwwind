class Form {
    constructor(formSelector, submitUrl) {
        this.form = document.querySelector(formSelector);
        this.submitUrl = submitUrl;
        this.formData = new FormData();

        this.init();
    }

    // Initialise event listeners
    init() {
        this.form.addEventListener('submit', (event) => this.handleSubmit(event));
    }

    // Validate a single field
    validateField(field) {
        let errorSpan = field.nextElementSibling; // Assuming the error span is next to the input
        if (!errorSpan || !errorSpan.classList.contains('error')) {
            return true; // No error span found, skip validation
        }
        // Clear previous error
        errorSpan.textContent = '';
                
        // Check required
        if (field.required && !field.value.trim()) {
            errorSpan.textContent = 'This field is required.';
            return false;
        }

        // Check min value for stock and price
        if (field.hasAttribute('min') && parseFloat(field.value) < parseFloat(field.min)) {
            errorSpan.textContent = `The value must be at least ${field.min}.`;
            return false;
        }

        // Check minlength
        if (field.minLength && field.value.length < field.minLength) {
            errorSpan.innerHTML = `The inputted text is too short. Please enter at least ${field.minLength} characters.<br>You currently have ${field.value.length} character(s).`;
            return false;
        }

        // Check maxlength
        if (field.maxLength && field.value.length > field.maxLength) {
            errorSpan.textContent = `The inputted text is too long. Please enter less than ${field.maxLength} characters.<br>You currently have ${field.value.length} character(s).`;
            return false;
        }
    
        return true; // Field is valid
    }

    // Validate all fields
    validateForm() {
        let isValid = true;
        const fields = this.form.querySelectorAll('input, select, textarea');
        
        let firstNF = false
        fields.forEach(field => {
            if (!this.validateField(field)) {
                field.style.border = '1px solid red';
                isValid = false;
                field.addEventListener('change', () => {field.style.border = 'var(--bs-border-width) solid var(--bs-border-color)'});
                if (!firstNF) {
                    field.scrollIntoView({ behavior: 'smooth', block: 'center'});
                    firstNF = !firstNF;
                }
            }
        });

        // Additional validation for stock and price
        const conditionDivs = this.form.querySelectorAll('.condition');
        conditionDivs.forEach(conditionDiv => {
            const stockField = conditionDiv.querySelector('input[name*="-stock"]');
            const priceField = conditionDiv.querySelector('input[name*="-price"]');
            const errorSpan = conditionDiv.nextElementSibling;
            errorSpan.innerHTML = '';
    
            if (stockField && priceField && errorSpan) {
                const stockValue = parseFloat(stockField.value);
                const priceValue = parseFloat(priceField.value);
    
                // Check stock
                if (isNaN(stockValue) || stockValue <= 0) {
                    conditionDiv.style.border = '1px solid red';
                    stockField.style.border = '1px solid red';
                    stockField.addEventListener('change', () => {
                        stockField.style.border = 'var(--bs-border-width) solid var(--bs-border-color)';
                        conditionDiv.style.border = '1px solid black';
                    });
                    errorSpan.innerHTML = 'Stock must be greater than 0.';
                    isValid = false;
                }

                // Check price (only if stock is valid)
                if (isNaN(priceValue) || priceValue <= 0) {
                    if (errorSpan.innerHTML) {
                        // If stock already has an error, append price error
                        errorSpan.innerHTML += '<br>Price must be greater than 0.';
                    } else {
                        // If stock is valid, display price error only
                        errorSpan.innerHTML = 'Price must be greater than 0.';
                    }
                    conditionDiv.style.border = '1px solid red';
                    priceField.style.border = '1px solid red';
                    priceField.addEventListener('change', () => {
                        priceField.style.border = 'var(--bs-border-width) solid var(--bs-border-color)';
                        conditionDiv.style.border = '1px solid black';
                    });
                    isValid = false;
                }
            }
        });
    
        return isValid;
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
    
        // Get the submit button
        const submitButton = this.form.querySelector('#submit');
    
        // Disable the button and add a loading indicator
        submitButton.disabled = true;
        submitButton.value = 'Submitting...'; // Change the button text
        submitButton.classList.add('loading'); // Add a class for styling (optional)
    
        // Validate the form
        if (!this.validateForm()) {
            // Re-enable the button and reset the text if validation fails
            submitButton.disabled = false;
            submitButton.value = 'Add Product'; // Reset button text
            submitButton.classList.remove('loading'); // Remove loading class
            return; // Stop submission if validation fails
        }
    
        // Prepare form data
        const formData = this.prepareFormData();
    
        try {
            // Submit the form data
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
                    // Redirect on success
                    result.message.includes('add') ? window.location.href = '../manage-products' : window.location.href = '../../manage-products';
                } else {
                    // Display error message
                    this.displayFlashMessage(result.message, 'error');
                    this.resetForm();
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            this.displayFlashMessage("An unexpected error occurred.", 'error');
        } finally {
            // Re-enable the button and reset the text
            submitButton.disabled = false;
            submitButton.value = 'Add Product'; // Reset button text
            submitButton.classList.remove('loading'); // Remove loading class
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
        this.fileInput = document.getElementById(`productImages`);
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
            images.forEach(image => this.processFiles(image));
            this.update = !this.update;
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
            this.productThumbnail.value = null;
            this.labelImg.src = '';
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
                img.src = `/static/media/uploads/${file}`;
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

            if (document.getElementById('images')) {document.getElementById('images').value = this.fileList};
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
        this.updateDropdowns(); // reset first
    }

    addCondition() {
        const options = ['Brand New', 'Like New', 'Lightly Used', 'Well Used'];
    
        // Clone the first condition element
        const newCondition = this.conditionList[0].cloneNode(true);
        const newError = this.conditionList[0].nextElementSibling.cloneNode(true);
    
        newCondition.querySelectorAll('input, select').forEach(item => {
            item.value = ''; // Reset values
            item.id = item.id.replace(/-\d+-(?=\w+$)/, `-${this.conditionList.length}-`);
            item.name = item.id;
        });
    
        // Update delete button functionality
        const deleteBtn = newCondition.querySelector('.deleteCondition');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                this.deleteCondition(newCondition);
            });
        }
    
        // Add change event listener to select dropdown
        const select = newCondition.querySelector('select');
        if (select) {
            select.addEventListener('change', () => this.updateDropdowns());
        }
    
        this.conditionsContainer.insertBefore(newCondition, this.addConditionBtn);
        newCondition.after(newError);
        this.conditionList.push(newCondition);
        
        this.conditionList.forEach(c => {
            this.updateDropdowns(); // Update dropdowns after adding new condition
        })
    }       

    deleteCondition(condition) {
        // Remove the condition from the DOM
        this.conditionsContainer.removeChild(condition);
        // Update the condition list
        this.conditionList = this.conditionList.filter(item => item !== condition);
        this.updateDropdowns(); // Refresh dropdowns after deletion
    }
    
    updateDropdowns() {
        const options = ['Brand New', 'Like New', 'Lightly Used', 'Well Used'];
    
        // Get all selected values from existing conditions
        const selectedValues = Array.from(this.conditionsContainer.querySelectorAll('select'))
            .map(select => select.value)
            .filter(value => value); // Remove empty values
        
        console.log(this.conditionList)
        this.conditionList.length > 3 ? this.addConditionBtn.style.display = 'none'  : this.addConditionBtn.style.display = 'block';
    
        // Iterate through all condition boxes and update their dropdowns
        this.conditionsContainer.querySelectorAll('select').forEach(select => {
            const currentValue = select.value; // Store current selection
    
            // Clear existing options
            select.innerHTML = '';
    
            // Repopulate dropdown with all options, disabling selected ones
            options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option;
                optionElement.textContent = option;
    
                // If the option is selected in another dropdown, disable it
                if (selectedValues.includes(option) && option !== currentValue) {
                    optionElement.disabled = true;
                }
    
                // Retain the current selection
                if (option === currentValue) {
                    optionElement.selected = true;
                }
    
                select.appendChild(optionElement);
            });
    
            // Ensure onchange event listener is always attached
            select.removeEventListener('change', () => this.updateDropdowns());
            select.addEventListener('change', () => this.updateDropdowns());
        });
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

document.getElementById('images').remove()

window.location.href.includes('/manage-products/add-product') ?
new ConditionHandler('productImages', 'form.product__form', '/dashboard/manage-products/add-product', false) :
new ConditionHandler('productImages', 'form.product__form', `/dashboard/manage-products/update-product/${document.getElementById('getIdHere').innerText}`, true);


// save form logic (class too crazy at this point of time lol)
if (window.location.href.includes('add-product')) {
    window.addEventListener('beforeunload', (event) => {

        const conditions = Array.from(document.querySelectorAll('.condition')).map(conditionDiv => ({
            condition: conditionDiv.querySelector('[name^="productConditions-"][name$="-condition"]').value,
            stock: conditionDiv.querySelector('[name^="productConditions-"][name$="-stock"]').value,
            price: conditionDiv.querySelector('[name^="productConditions-"][name$="-price"]').value
        }));

        const formData = {
            productName: document.querySelector('[name="productName"]').value,
            productCreator: document.querySelector('[name="productCreator"]').value,
            productDescription: document.querySelector('[name="productDescription"]').value,
            productType: document.querySelector('[name="productType"]').value,
            productGenre: document.querySelector('[name="productGenre"]').value,
            productConditions: conditions,
            isFeaturedSpecial: document.querySelector('[name="productIsFeaturedSpecial"]').checked,
            isFeaturedStaff: document.querySelector('[name="productIsFeaturedStaff"]').checked
        };
        

        const csrfToken = document.querySelector('input[name="csrf_token"]').value;

        fetch('/dashboard/manage-products/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(formData)
        }).then(response => {
            if (!response.ok) {
                console.error('Error:', response.statusText);
            }
        }).catch(error => console.error('Error:', error));

    });
}