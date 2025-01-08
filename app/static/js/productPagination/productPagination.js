function adjustProductSpacing() {

    if (window.innerWidth > 1400) {
        document.querySelectorAll('h5.name').forEach(h5 => {
            if (parseFloat(getComputedStyle(h5).width) >= 250) {
                h5.innerText = h5.innerText.slice(0, 22).trim()  + '...'; // not foolproof i'd assume, but will just leave it as is for now
            }
        })
    } else {
        document.querySelectorAll('h5.name').forEach(h5 => {
            if (parseFloat(getComputedStyle(h5).width) >= 180) {
                h5.innerText = h5.innerText.slice(0, 15).trim()  + '...';
            }
        })
    }
    
    const container = document.querySelector('.products');
    const products = Array.from(container.children);

    if (!products.length) return;

    // Container width
    const containerWidth = container.offsetWidth;

    // Card dimensions
    const cardWidth = products[0].offsetWidth;
    let minGap = 80; // Minimum gap between cards
    if (window.innerWidth <= 1400) {
        minGap = 40;
    }

    // Calculate items per row
    const itemsPerRow = Math.floor((containerWidth + minGap) / (cardWidth + minGap));

    // Calculate dynamic gap
    const totalCardWidth = itemsPerRow * cardWidth;
    const remainingSpace = containerWidth - totalCardWidth;
    const gap = Math.max(minGap, remainingSpace / Math.max(itemsPerRow - 1, 1));

    // Reset styles
    container.style.display = 'flex';
    container.style.flexWrap = 'wrap';
    container.style.rowGap = '10'; // Vertical gaps
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