class RatingStars {
    constructor(container, text) {
        this.container = document.querySelector(container);
        this.stars = Array.from(this.container.querySelectorAll('i.bi-star-fill'));
        // this.getRatingInputs = Array.from(document.querySelectorAll('.review__section .review .rating input'));
        this.rating = parseFloat(document.getElementById('rating-score').getAttribute('get-rating-here'))
        isNaN(this.rating) ? this.rating = 0 : this.rating = this.rating.toFixed(1);
        this.rating0Text = text;
        this.ratingScore = this.container.querySelector('.ratingScore');
        this.reviewNum = this.container.querySelector('.numOfReviews');

        this.init();
        this.fillStars();
    }

    init() {
        if (this.rating === Math.round(this.rating) && this.rating !== 0) {
            this.rating = this.rating.toString() + '.0';
        }
    }
    
    fillStars() {
        this.stars.forEach((star, index) => {
            if (index + 1 <= this.rating) {
                star.style.color = 'orange';
            } else {
                let percOrange = Math.round((this.rating - index) * 100 * Math.pow(10, 1)) / Math.pow(10, 1);
                percOrange < 50 ?
                star.style.background = `linear-gradient(to left, #D9D9D9 ${100-(percOrange)}%, #FFA500 ${percOrange}%)` :                   
                star.style.background = `linear-gradient(to right, #FFA500 ${percOrange}%, #D9D9D9 ${100-(percOrange)}%)`;
                star.style.webkitBackgroundClip = 'text';
                star.style.backgroundClip = 'text';
                star.style.color = 'transparent';
            };
        });
    }
}

new RatingStars(".product .rating", 'No reviews yet. Be the first one!');
new RatingStars(".review__section .rating", '0');

class Images {
    constructor(container) {
        this.container = container;
        this.images = Array.from(this.container.querySelectorAll('.image__container img'));
        this.display = this.container.previousElementSibling.querySelector('img');
        this.imagePrev = this.images.find(image => image.src === this.display.src);

        this.init();
    }

    init() {
        this.imagePrev.parentElement.classList.add('active');

        this.images.forEach(image => {
            image.addEventListener('click', () => {this.selectImage(image)});
        });
    }

    selectImage(target) {
        this.imagePrev.parentElement.classList.remove('active');
        this.imagePrev = target;
        target.parentElement.classList.add('active');
        this.display.src = target.src;
    }
}

new Images(document.querySelector('.image-list'));
