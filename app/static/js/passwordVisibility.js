document.addEventListener("DOMContentLoaded", function () {
  const togglePassword = document.getElementById("toggle-password");
  const eyeIcon = document.getElementById("eye-icon");
  const passwordFields = document.querySelectorAll(".password");

  togglePassword.addEventListener("click", function () {
    passwordFields.forEach(function (field) {
      const type = field.type === "password" ? "text" : "password";
      field.type = type;
    });

    if (passwordFields[0].type === "password") {
      eyeIcon.classList.replace("fa-eye-slash", "fa-eye");
    } else {
      eyeIcon.classList.replace("fa-eye", "fa-eye-slash");
    }
  });
});
