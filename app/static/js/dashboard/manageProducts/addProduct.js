// note to self: don't use this code anywhere else lol

class Form {
    constructor(formSelector, submitUrl) {
        this.form = document.querySelector(formSelector);
        this.submitUrl = submitUrl;
        this.formData = new FormData();

        this.init();
    }

    // initialise event listeners
    init() {
        this.form.addEventListener('submit', (event) => this.handleSubmit(event));
    }

    // custom form data logic
    prepareFormData() {
        const formElements = this.form.querySelectorAll('input, select, textarea');
        formElements.forEach(element => {
            if (element.name && !['productImages', 'productThumbnail', /^productConditions.*/].includes(element.name)) {
                this.formData.append(element.name, element.value);
            }
        });
        return this.formData;
    }

    // custom form submission
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
                } else {
                    this.displayFlashMessage(result.message, 'error');
                    console.log(result.message)
                    this.fileList = [];
                    this.fileListDisplay.innerHTML = '';
                    this.fileInput.previousElementSibling.style.background = '';
                    this.formData = new FormData()
                }
                window.scroll({top: 0, behavior: 'smooth'});
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            this.displayFlashMessage("An unexpected error occurred.", 'error');
        }
    }
    
    // custom flash method because i can't code
    displayFlashMessage(message, category) {
    const flashContainer = document.querySelector('.flash-messages');
    const alert = document.createElement('div');
    alert.classList.add('alert');
    alert.classList.add('alert-dismissible');
    alert.classList.add('fade');
    alert.classList.add('show');

    if (category === 'error') {
        alert.classList.add('alert-danger');
        alert.innerHTML = `
            <strong>Error:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
    } else if (category === 'success') {
        alert.classList.add('alert-success');
        alert.innerHTML = `
            <strong>Success:</strong> ${message}
            <p id="countdown">Redirecting in 3 seconds...</p>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
    } else {
        alert.classList.add('alert-info');
        alert.innerHTML = `
            <strong>Info:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
    }
    
    flashContainer.appendChild(alert);
    if (category === 'success') {this.startCountdown(3)};
}

// Countdown logic for redirecting after 3 seconds
startCountdown(seconds) {
    const countdown = document.getElementById('countdown');
    const timer = setInterval(() => {
        seconds -= 1;
        countdown.textContent = `Redirecting in ${seconds} seconds...`;

        if (seconds <= 0) {
            clearInterval(timer);
            window.location.href = '../manage-products'; // Redirect to the provided URL
        }
    }, 1000);
}
}

class ImageHandler extends Form {
    constructor(fileInputName, formSelector, submitUrl) {
        super(formSelector, submitUrl);
        this.fileInputName = fileInputName;
        this.fileInput = this.form.querySelector(`input[name="${this.fileInputName}"]`);
        this.fileList = [];
        this.productThumbnail = this.form.querySelector('input[name="productThumbnail"]');
        this.fileListDisplay = this.form.querySelector('.file-list');

        this.initImageHandling();
    }

    // initialise imagehandler event listeners
    initImageHandling() {
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (event) => this.handleFileSelect(event));
        }
    }

    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        this.fileList = this.fileList.concat(files);
    
        // displaying files (images)
        this.fileListDisplay.innerHTML = '';  // resetting previous display list
        this.fileList.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.classList.add('image__container');
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.alt = `Image Preview ${index + 1}`;
                fileItem.appendChild(img);
    
                // check if this is first time uploading file, and set it to thumbnail
                if (index === 0 && !Array.from(this.fileListDisplay.childNodes).find(file => file.classList.contains('active'))) {
                    fileItem.classList.add('active');
                    this.fileInput.previousElementSibling.style.background = `url(${img.src}) no-repeat center`;
                    this.fileInput.previousElementSibling.style.backgroundSize = '250px';
                    this.productThumbnail.value = index;
                }
            };
    
            reader.readAsDataURL(file);
            this.fileListDisplay.appendChild(fileItem);
            fileItem.addEventListener('click', () => this.handlePreviewImage(fileItem, index));
        });
    
        // clear input value
        event.target.value = '';
    }
    
    // setting active image as thumbnail
    handlePreviewImage(targetNode, index) {
        const items = Array.from(this.fileListDisplay.childNodes);
        const currentNode = items.find(item => item.classList.contains('active'));
    
        if (currentNode) {
            currentNode.classList.remove('active');
        }
    
        targetNode.classList.add('active');
        const img = targetNode.querySelector('img');
    
        // Set the background to the clicked image
        if (img) {
            this.fileInput.previousElementSibling.style.background = `url(${img.src}) no-repeat center`;
            this.fileInput.previousElementSibling.style.backgroundSize = '250px';
        }
        this.productThumbnail.value = index;
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
    constructor(fileInputName, formSelector, submitUrl) {
        super(fileInputName, formSelector, submitUrl);
        this.conditionsContainer = this.form.querySelector('.product__conditions');
        this.conditionList = Array.from(this.form.querySelectorAll('.condition'));
        this.lastCondition = this.conditionList[this.conditionList.length - 1];
        this.addConditionBtn = this.form.querySelector('button.addCondition');

        this.initConditionHandler();
    }

    initConditionHandler() {
        this.addConditionBtn.addEventListener('click', () => this.addCondition());
    }

    addCondition() {
        const newCondition = this.lastCondition.cloneNode(true);
        const newConditionInputs = Array.from(newCondition.querySelectorAll('input, select'));
        newConditionInputs.forEach(input => {
            const name = input.name
            if (name) {
                const newName = name.replace(/\d+/, this.conditionList.length);
                input.setAttribute('name', newName);
                name.includes('condition') ? input.value = 1 : input.value = '';
            };
        });

        this.conditionList.push(newCondition);
        this.conditionsContainer.insertBefore(newCondition, this.addConditionBtn);
    }

    prepareFormData() {
        const formData = super.prepareFormData();

        this.conditionList.forEach((condition, index) => {
            const inputs = condition.querySelectorAll('input, select');
            inputs.forEach((input) => {
                if (input.name) {
                    formData.append(input.name, input.value);
                }
            });
        });

        return formData;
    }
}

new ConditionHandler('productImages', 'form', '/dashboard/manage-products/add-product');