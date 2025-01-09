// TO USE PASTE THIS HTML STRUCTURE, styles can be found in css/pageInteractions/filters.css, script in js/pageInteractions/filters.js. will ***probably*** create filter sql table later.
/* <label>Genre</label>
<div class="filter">
    <span class="selected">All</span>&nbsp;&nbsp;<i class="bi bi-chevron-down"></i>
    <ul class="filter--options">
        <li class="highlighted">All</li>
        <li>Vinyl</li>
        <li>Book</li>
        <li>Movie</li>
    </ul>
</div> */


// filters (custom select) interaction
// Function to handle filter selection and update URL parameters
class Filter {
    constructor(filter, maxWidth, maxChar) {
        this.filter = filter;
        this.icon = filter.querySelector('i.bi-chevron-down');
        this.options = Array.from(filter.querySelectorAll('li'));
        this.currentlySelected = filter.querySelector('.selected');
        this.active = false;
        this.maxWidth = maxWidth;
        this.maxChar = maxChar;

        // Adjust label text if it's too long
        this.adjustLabelText();

        // Option selection logic
        this.highlightedIndex = 0;

        // Bind event listeners
        this.handleOutsideClick = this.handleOutsideClick.bind(this);
        this.handleKeyboard = this.handleKeyboard.bind(this);

        // Initialize local event listeners
        this.init();
    }

    init() {
        this.filter.addEventListener('click', () => this.toggleFilter());
        this.options.forEach(option => {
            if (!option.classList.contains('disabled')) {
                option.addEventListener('mouseover', () => this.handleHover(option));
                option.addEventListener('click', (e) => {
                    if (e.target === option) {
                        this.selectOption();
                    }
                });
            }
        });
    }

    toggleFilter() {
        this.active = !this.active;
        this.filter.classList.toggle('active', this.active);
        this.filter.style.borderRadius = this.active ? '1.5em 1.5em 0 0' : '1.5em';
        this.icon.style.rotate = this.active ? '180deg' : '0deg';
        this.options.forEach(option => {
            option.style.display = this.active ? 'block' : 'none';
        });

        if (this.active) {
            document.addEventListener('click', this.handleOutsideClick);
            document.addEventListener('keydown', this.handleKeyboard);
        } else {
            document.removeEventListener('click', this.handleOutsideClick);
            document.removeEventListener('keydown', this.handleKeyboard);
        }

        this.adjustLabelText();
    }

    handleOutsideClick(e) {
        if (this.active && !this.filter.contains(e.target)) {
            this.toggleFilter();
        }
    }

    handleHover(option) {
        const highlighted = this.options.find(opt => opt.classList.contains('highlighted'));
        if (highlighted) {
            highlighted.classList.remove('highlighted');
        }
        option.classList.add('highlighted');
    }

    handleKeyboard(e) {
        e.preventDefault();

        if (['Enter', 'Escape', 'Tab'].includes(e.key)) {
            if (e.key === 'Enter') {
                this.selectOption();
            }
            if (this.active) {
                this.toggleFilter();
            }
        } else if (['ArrowUp', 'ArrowDown'].includes(e.key)) {
            const currentIndex = this.options.findIndex(option => option.classList.contains('highlighted'));
            const targetIndex = (e.key === 'ArrowUp')
                ? (currentIndex > 0 ? currentIndex - 1 : this.options.length - 1)
                : (currentIndex < this.options.length - 1 ? currentIndex + 1 : 0);

            this.options[currentIndex].classList.remove('highlighted');
            this.options[targetIndex].classList.add('highlighted');
        }
    }

    selectOption() {
        const selectedOption = this.options.find(option => option.classList.contains('highlighted'));
        this.currentlySelected.innerText = selectedOption.innerText;
        const filterKey = this.filter.getAttribute('filter-for'); // e.g., 'type', 'genre'
        const params = new URLSearchParams(window.location.search);

        if (['all','none'].includes(selectedOption.innerText.toLowerCase())) {
            if (filterKey === 'type') {
                params.delete('genre')
            }
            params.delete(filterKey);
        } else {
            params.set(filterKey, selectedOption.innerText.toLowerCase());
        }

        window.location.search = params.toString(); // Update the URL
    }

    adjustLabelText() {
        if (parseFloat(window.getComputedStyle(this.currentlySelected).width) >= this.maxWidth) {
            this.currentlySelected.innerText = this.currentlySelected.innerText.substring(0, this.maxChar) + '...';
        } else {
            this.currentlySelected.innerText = this.currentlySelected.innerText.replace('...', '');
        }
    }
}

// initialise Filters
if (!window.location.href.includes('products/product')) {
    const filters = Array.from(document.querySelectorAll('.filter')).filter(filter => !filter.classList.contains('review'));
    filters.forEach(filter => new Filter(filter, 74, 6));
} else {
    new Filter(document.getElementById('filter'), 100, 10);
}