document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("file-input");
  const previewContainer = document.getElementById("preview-container");


  fileInput.addEventListener("change", (event) => {
      const files = event.target.files;
      previewContainer.innerHTML = "";

      if (files.length === 0) {
          const message = document.createElement("p");
          message.textContent = "No files selected.";
          previewContainer.appendChild(message);
          return;
      }

      for (const file of files) {
          if (file.type.startsWith("image/")) {
              const reader = new FileReader();
              reader.onload = (e) => {
             
                  const img = document.createElement("img");
                  img.src = e.target.result;
                  img.classList.add("preview-image");
                  previewContainer.appendChild(img);
              };
              reader.readAsDataURL(file);
          } else {
              alert("Only image files are allowed.");
          }
      }
  });
});
