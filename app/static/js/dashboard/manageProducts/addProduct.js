class FileFormHandler {
    constructor(fileInputName, submitUrl) {
        this.fileList = [];
        this.form = document.querySelector('form');
        this.fileInput = this.form.querySelector(`input[name="${fileInputName}"]`);
        this.productThumbnail = this.form.querySelector('input[name="productThumbnail"]');
        this.fileListDisplay = this.fileInput.nextElementSibling;
        this.submitUrl = submitUrl;

        this.init();
    }

    // initialise event listeners
    init() {
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (event) => this.handleFileSelect(event));
        }

        this.form.addEventListener('submit', (event) => this.handleSubmit(event));
    }

    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        this.fileList = this.fileList.concat(files);
    
        // logic to display files
        this.fileListDisplay.innerHTML = '';  // clear existing list so that it is rendered correctly.
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
        this.productThumbnail.value = index
    }
    

    // Prepare form data for submission
    prepareFormData() {
        const formData = new FormData();

        // Append files to FormData
        this.fileList.forEach(file => formData.append(this.fileInput.name, file));

        // Get all other form fields and append them
        const formElements = this.form.querySelectorAll('input, select, textarea');
        formElements.forEach(element => {
            if (element.name && element.name !== this.fileInput.name) {
                formData.append(element.name, element.value);
            }
        });

        return formData;
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
    }
}

new FileFormHandler('productImages', '/dashboard/manage-products/add-product');