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