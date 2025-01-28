document.addEventListener("DOMContentLoaded", function () {
  const filterForm = document.getElementById("filterForm");
  const filterSelects = filterForm.querySelectorAll("select");

  // Function to update filters
  function updateFilters() {
    // Get current URL and create URLSearchParams object
    const currentUrl = new URL(window.location.href);
    const searchParams = new URLSearchParams(currentUrl.search);

    // Update search params with current filter values
    filterSelects.forEach((select) => {
      if (select.value) {
        searchParams.set(select.name, select.value);
      } else {
        searchParams.delete(select.name);
      }
    });

    // Preserve search query if it exists
    const searchQuery = document.querySelector('input[name="q"]')?.value;
    if (searchQuery) {
      searchParams.set("q", searchQuery);
    }

    // Update URL and reload page
    currentUrl.search = searchParams.toString();
    window.location.href = currentUrl.toString();
  }

  // Add change event listeners to all select elements
  filterSelects.forEach((select) => {
    select.addEventListener("change", updateFilters);
  });
});
