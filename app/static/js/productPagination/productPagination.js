// list and grid views
document.addEventListener('DOMContentLoaded', function () {
    const gridViewButton = document.getElementById('gridViewButton');
    const listViewButton = document.getElementById('listViewButton');
    const productsContainer = document.querySelector('.products');
    const productContainer = Array.from(document.querySelectorAll('.product'));

    const savedView = localStorage.getItem('viewMode');

    if (savedView === 'list') {
        listViewButton.classList.add('active');
        gridViewButton.classList.remove('active');
        productsContainer.classList.add('list-view');
    } else {
        gridViewButton.classList.add('active');
        listViewButton.classList.remove('active');
        productsContainer.classList.remove('list-view');
    }

    // grid button
    gridViewButton.addEventListener('click', function () {
        if (!gridViewButton.classList.contains('active')) {
            gridViewButton.classList.add('active');
            listViewButton.classList.remove('active');
            productsContainer.classList.remove('list-view');
            localStorage.setItem('viewMode', 'grid');
        }
    });

    // list button
    listViewButton.addEventListener('click', function () {
        if (!listViewButton.classList.contains('active')) {
            listViewButton.classList.add('active');
            gridViewButton.classList.remove('active');
            productsContainer.classList.add('list-view');
            productContainer.forEach(e => {
                e.style.marginBottom = '0';
                e.addEventListener('click', (i) => {window.location.href = e.querySelector('a').getAttribute('href')});
            });
            localStorage.setItem('viewMode', 'list');
        }
    });
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
        container.style.rowGap = '20'; // Vertical gaps
        container.style.columnGap = `${gap}px`; // Horizontal gaps only
    
        // Apply width to each product for consistent alignment
        products.forEach(product => {
            if (document.getElementById('listViewButton').className != 'active' && product.className != 'description') {
                product.style.marginBottom = '40px'; // Ensure no margin between rows
            }
        });    
    }
    
    // Initial setup
    adjustProductSpacing();
    
    // Adjust dynamically on window resize
    window.addEventListener('resize', adjustProductSpacing);
});