console.log("Trade-ins JS Loaded!");
document.addEventListener("DOMContentLoaded", function () {
    const popup = document.getElementById("successPopup");

    if (popup) {
        popup.classList.add("show");

        // Hide the popup after 3 seconds
        setTimeout(() => {
            popup.classList.remove("show");
        }, 3000);
    }
});