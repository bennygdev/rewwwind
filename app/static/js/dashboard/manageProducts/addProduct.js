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

    // Prepare form data for submission
    prepareFormData() {
        const formElements = this.form.querySelectorAll('input, select, textarea');
        formElements.forEach(element => {
            if (element.name && !['productImages', 'productThumbnail', /^productConditions.*/].includes(element.name)) {
                console.log(element.name);
                this.formData.append(element.name, element.value);
            }
        });
        console.log('Called prepareFormData from:', this.constructor.name);
        return this.formData;
    }

    // Handle form submission
    async handleSubmit(event) {
        event.preventDefault();

        const formData = this.prepareFormData();

        // Debugging: Log the form data
        for (let [key, value] of formData.entries()) {
            console.log(`${key}:`, value);
        }

        const response = await fetch(this.submitUrl, {
            method: 'POST',
            body: formData,
        });

        const result = await response.text();
        console.log(result);  // Handle response if necessary
    }
}

class ImageHandler extends Form {
    constructor(fileInputName, formSelector, submitUrl) {
        super(formSelector, submitUrl);  // Call the parent constructor
        this.fileInputName = fileInputName;
        this.fileInput = this.form.querySelector(`input[name="${this.fileInputName}"]`);
        this.fileList = [];
        this.productThumbnail = this.form.querySelector('input[name="productThumbnail"]');
        this.fileListDisplay = this.fileInput.nextElementSibling;

        this.initImageHandling();
    }

    // Initialize image-specific event listeners
    initImageHandling() {
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (event) => this.handleFileSelect(event));
        }
    }

    // Handle file selection (for image inputs)
    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        this.fileList = this.fileList.concat(files);
    
        // Logic to display files
        this.fileListDisplay.innerHTML = '';  // Clear existing list
        this.fileList.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.classList.add('image__container');
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.alt = `Image Preview ${index + 1}`;
                fileItem.appendChild(img);
    
                // Check if it's the first image and set background and active class
                if (index === 0 && !Array.from(this.fileListDisplay.childNodes).find(file => file.classList.contains('active'))) {
                    fileItem.classList.add('active');  // Mark first image as active
                    this.fileInput.previousElementSibling.style.background = `url(${img.src}) no-repeat center`;  // Set background
                    this.fileInput.previousElementSibling.style.backgroundSize = '250px';
                    this.productThumbnail.value = index;
                }
            };
    
            reader.readAsDataURL(file);  // Start the reading process
            this.fileListDisplay.appendChild(fileItem);
            fileItem.addEventListener('click', () => this.handlePreviewImage(fileItem, index));
        });
    
        // Clear input value to allow re-selection
        event.target.value = '';
    }
    
    // Handle image preview (set as active)
    handlePreviewImage(targetNode, index) {
        const items = Array.from(this.fileListDisplay.childNodes);
        const currentNode = items.find(item => item.classList.contains('active'));
    
        if (currentNode) {
            currentNode.classList.remove('active');
        }
    
        targetNode.classList.add('active');  // Mark the clicked item as active
        const img = targetNode.querySelector('img');  // Select the img element within targetNode
    
        // Set the background to the clicked image
        if (img) {
            this.fileInput.previousElementSibling.style.background = `url(${img.src}) no-repeat center`;
            this.fileInput.previousElementSibling.style.backgroundSize = '250px';
        }
        this.productThumbnail.value = index;
    }

    // Override the parent's method to append image files as well
    prepareFormData() {
        const formData = super.prepareFormData();

        // Append image files to FormData
        this.fileList.forEach(file => formData.append(this.fileInput.name, file));
        formData.append(this.productThumbnail.name, this.productThumbnail.value)

        return formData;
    }
}

class ConditionHandler extends Form {
    constructor(formSelector, submitUrl) {
        super(formSelector, submitUrl);
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
        const formData = super.prepareFormData();  // Get parent form data

        // Append conditions to FormData
        this.conditionList.forEach((condition, index) => {
            const inputs = condition.querySelectorAll('input, select');
            inputs.forEach((input) => {
                if (input.name) {
                    formData.append(input.name, input.value);
                }
            });
        });

        return formData;  // Return the updated form data
    }
}

new ImageHandler('productImages', 'form', '/dashboard/manage-products/add-product');
new ConditionHandler('form', '/dashboard/manage-products/add-product');