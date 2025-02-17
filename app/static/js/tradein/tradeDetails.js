document.addEventListener("DOMContentLoaded", function () {
    console.log("tradeDetails.js loaded!");

    const form = document.querySelector("form");
    const shippingOptions = document.querySelectorAll('input[name="shipping_option"]');
    const trackingNumberSection = document.getElementById("tracking-number-section");
    const shippingAddressSection = document.getElementById("shipping-address-section");

    function updateFormDisplay() {
        let selectedOption = document.querySelector('input[name="shipping_option"]:checked');

        if (!selectedOption) return;

        trackingNumberSection.classList.add("hidden");
        shippingAddressSection.classList.add("hidden");

        if (selectedOption.value === "Mail-in") {
            trackingNumberSection.classList.remove("hidden");
        } 
        else if (selectedOption.value === "Pick-Up Service") {
            shippingAddressSection.classList.remove("hidden");
        }
    }

    shippingOptions.forEach(option => {
        option.addEventListener("change", updateFormDisplay);
    });

    updateFormDisplay();

    form.addEventListener("submit", function (event) {
        let errors = document.querySelectorAll(".form-error");
        errors.forEach(error => error.remove());

        let inputs = document.querySelectorAll("input");
        let hasErrors = false;

        inputs.forEach(input => {
            if (!input.checkValidity()) {
                let errorMessage = input.validationMessage;
                let errorSpan = document.createElement("span");
                errorSpan.classList.add("form-error");
                errorSpan.textContent = errorMessage;
                input.insertAdjacentElement("afterend", errorSpan);
                hasErrors = true;
            }
        });

        if (hasErrors) {
            event.preventDefault();
        }
    });
});