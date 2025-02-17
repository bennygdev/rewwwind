document.addEventListener("DOMContentLoaded", function () {
    console.log("tradeDetails.js loaded!");

    const shippingOptions = document.querySelectorAll('input[name="shipping_option"]');
    const trackingNumberSection = document.getElementById("tracking-number-section");
    const shippingAddressSection = document.getElementById("shipping-address-section");

    function updateFormDisplay() {
        let selectedOption = document.querySelector('input[name="shipping_option"]:checked');
        
        // Ensure elements exist before modifying classList
        if (!selectedOption || !trackingNumberSection || !shippingAddressSection) return;

        trackingNumberSection.classList.add("hidden");
        shippingAddressSection.classList.add("hidden");

        if (selectedOption.value === "Mail-in") {
            trackingNumberSection.classList.remove("hidden");
        } else if (selectedOption.value === "Pick-Up Service") {
            shippingAddressSection.classList.remove("hidden");
        }
    }

    // Attach event listeners to radio buttons
    shippingOptions.forEach(option => {
        option.addEventListener("change", updateFormDisplay);
    });

    // Run on page load in case there is a pre-selected option
    updateFormDisplay();
});

document.addEventListener("DOMContentLoaded", function () {
    // Close flash message when clicking the close button
    document.querySelectorAll(".close-flash").forEach(button => {
        button.addEventListener("click", function () {
            this.parentElement.style.display = "none";
        });
    });

    // Auto-hide flash message after 5 seconds
    setTimeout(() => {
        document.querySelectorAll(".flash-message").forEach(message => {
            message.style.opacity = "0";
            setTimeout(() => {
                message.style.display = "none";
            }, 500);
        });
    }, 5000); // 5 seconds
});

document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ tradeDetails.js Loaded - Carousel Initialized");

    let images = JSON.parse('{{ trade_item.images | tojson | safe }}');  // Extract images safely
    let currentIndex = 0;

    const imageElement = document.getElementById("trade-image");
    const prevBtn = document.getElementById("prev-image");
    const nextBtn = document.getElementById("next-image");

    console.log("Loaded images:", images);  // Debugging: Show loaded images

    function updateImage() {
        console.log(`Displaying image ${currentIndex}: ${images[currentIndex]}`); 
        if (images.length > 0) {
            imageElement.src = "{{ url_for('static', filename='media/uploads/') }}" + images[currentIndex];
        }
    }

    if (!prevBtn || !nextBtn) {
        console.error("❌ Error: Buttons not found in DOM!");
        return;
    } else {
        console.log("✅ Buttons Found - Adding Event Listeners");
    }

    prevBtn.addEventListener("click", function () {
        console.log("⬅️ Prev button clicked");
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        updateImage();
    });

    nextBtn.addEventListener("click", function () {
        console.log("➡️ Next button clicked");
        currentIndex = (currentIndex + 1) % images.length;
        updateImage();
    });

    updateImage(); // Load the first image on page load
});
