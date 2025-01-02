function adjustProductSpacing() {
    const container = document.querySelector('.products');
    const products = Array.from(container.children);

    if (!products.length) return;

    // Container width
    const containerWidth = container.offsetWidth;

    // Card dimensions
    const cardWidth = products[0].offsetWidth;
    const minGap = 30; // Minimum gap between cards

    // Calculate items per row
    const itemsPerRow = Math.floor((containerWidth + minGap) / (cardWidth + minGap));

    // Calculate dynamic gap
    const totalCardWidth = itemsPerRow * cardWidth;
    const remainingSpace = containerWidth - totalCardWidth;
    const gap = Math.max(minGap, remainingSpace / Math.max(itemsPerRow - 1, 1));

    // Reset styles
    container.style.display = 'flex';
    container.style.flexWrap = 'wrap';
    container.style.rowGap = '0'; // No vertical gaps
    container.style.columnGap = `${gap}px`; // Horizontal gaps only

    // Apply width to each product for consistent alignment
    products.forEach(product => {
        product.style.marginBottom = '40px'; // Ensure no margin between rows
    });
}

// Initial setup
adjustProductSpacing();

// Adjust dynamically on window resize
window.addEventListener('resize', adjustProductSpacing);
