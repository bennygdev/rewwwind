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
class Filter {
    constructor(filter) {
        this.filter = filter;
        this.icon = filter.querySelector('i.bi-chevron-down');
        this.options = Array.from(filter.querySelectorAll('li'));
        this.currentlySelected = filter.querySelector('span');
        this.active = false;

        // make sure label does not grow too long
        parseFloat(window.getComputedStyle(this.currentlySelected).width) >= 74 ?
        this.currentlySelected.innerText = this.currentlySelected.innerText.substring(0, 6) + '...' :
        this.currentlySelected.innerText.replace('...', '');

        // option selection logic
        this.highlightedIndex = 0;
        this.targetIndex = 0;

        // bind global event listeners to context to avoid anonymity issues
        this.handleOutsideClick = this.handleOutsideClick.bind(this);
        this.handleKeyboard = this.handleKeyboard.bind(this);

        // initialise local event listeners
        this.init();
    };

    init() {
        this.filter.addEventListener('click', () => this.toggleFilter());
        this.options.forEach(option => {
            option.addEventListener('mouseover', () => this.handleHover(option));
            option.addEventListener('click', (e) => {if (e.target === option) {this.selectOption()}});
        });
    };

    toggleFilter() { 
        // trigger style and active status changes
        this.active = !this.active;
        this.filter.classList.toggle('active', this.active);
        this.filter.style.borderRadius = this.active ? '1.5em 1.5em 0 0' : '1.5em';
        this.icon.style.rotate = this.active ? '180deg' : '0deg';
        this.options.forEach((option) => option.style.display = this.active ? 'block' : 'none');
        
        // trigger event listeners to avoid propagation
        if (this.active) {
            document.addEventListener('click', this.handleOutsideClick);
            document.addEventListener('keydown', this.handleKeyboard);
        } else {
            document.removeEventListener('click', this.handleOutsideClick);
            document.removeEventListener('keydown', this.handleKeyboard);
        };
        // make sure label does not grow too long
        parseFloat(window.getComputedStyle(this.currentlySelected).width) >= 74 ?
        this.currentlySelected.innerText = this.currentlySelected.innerText.substring(0, 6) + '...' :
        this.currentlySelected.innerText.replace('...', '');
    };

    handleOutsideClick(e) {
        // close filter when it is not targeted by pointer
        if (this.active && !this.filter.contains(e.target)) {
            this.toggleFilter();
        };
    };

    handleHover(option) { // NOTE: Does not work when devtools is open because browser is considered to be inactive
        // find previous highlighted index and to-be highlighted index
        this.highlightedIndex = this.options.findIndex(option => Array.from(option.classList).includes('highlighted'));
        this.targetIndex = this.options.indexOf(option);

        // update highlighted option
        this.options[this.highlightedIndex].classList.remove('highlighted');
        this.options[this.targetIndex].classList.add('highlighted');
    };

    handleKeyboard(e) {
        e.preventDefault();
        if (['Enter', 'Escape', 'Tab'].includes(e.key)) { // close filters except Enter
            if (e.key === 'Enter') {this.selectOption()}; // select new option
            if (this.active) {this.toggleFilter()};
        } else if (['ArrowUp', 'ArrowDown'].includes(e.key)) { // selecting options
            // find previous highlighted index
            this.highlightedIndex = this.options.findIndex(option => Array.from(option.classList).includes('highlighted'));

            // when up take previous index or first index as target, vice versa
            e.key == 'ArrowUp' ?
            this.highlightedIndex > 0 ? this.targetIndex = this.highlightedIndex - 1 : this.targetIndex = this.options.length - 1 :
            this.highlightedIndex < this.options.length - 1 ? this.targetIndex = this.highlightedIndex + 1 : this.targetIndex = 0 ;
            
            // update highlighted option
            this.options[this.highlightedIndex].classList.remove('highlighted');
            this.options[this.targetIndex].classList.add('highlighted');
        };
    };

    selectOption() {
        // change span text to selected option
        this.currentlySelected.innerText = this.options[this.targetIndex].innerText;
        this.filter.classList.toggle('activated', !['none', 'all'].includes(this.currentlySelected.innerText.toLowerCase()));
    };
};
// initialise Filters
const filters = document.querySelectorAll('.filter');
filters.forEach(filter => new Filter(filter));