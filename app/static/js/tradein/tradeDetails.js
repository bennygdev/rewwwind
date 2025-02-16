document.addEventListener("DOMContentLoaded", function () {
    console.log("tradeDetails.js Loaded!");

    const shippingOptions = document.querySelectorAll('input[name="shipping_option"]');
    const trackingSection = document.getElementById("tracking-number-section");
    const shippingAddressSection = document.getElementById("shipping-address-section");
    const paymentSection = document.getElementById("payment-section");

    // Initially hide all sections
    trackingSection.classList.add("hidden");
    shippingAddressSection.classList.add("hidden");
    paymentSection.classList.add("hidden");

    // Function to handle visibility based on selection
    function handleShippingSelection(event) {
        const selectedValue = event.target.value;
        console.log("Selected Shipping Option:", selectedValue);

        // Hide all sections initially
        trackingSection.classList.add("hidden");
        shippingAddressSection.classList.add("hidden");
        paymentSection.classList.add("hidden");

        // Show relevant sections based on the selected shipping option
        if (selectedValue === "Mail-in") {
            trackingSection.classList.remove("hidden");  // Show Tracking Number
            paymentSection.classList.remove("hidden");   // Show Payment Section
        } else if (selectedValue === "In-Store") {
            paymentSection.classList.remove("hidden");   // Show Payment Section
        } else if (selectedValue === "Pick-up") {
            shippingAddressSection.classList.remove("hidden"); // Show Shipping Address
            paymentSection.classList.remove("hidden");   // Show Payment Section
        }
    }

    // Attach event listeners to all radio buttons
    shippingOptions.forEach(option => {
        option.addEventListener("change", handleShippingSelection);
    });
});

