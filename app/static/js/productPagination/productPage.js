class RatingStars {
    constructor(container) {
        this.container = document.querySelector(container);
        this.stars = Array.from(this.container.querySelectorAll('i.bi-star-fill'));
        this.rating = 4;

        this.fillStars();
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
            }
        })
    }
}

new RatingStars(".product .rating");
new RatingStars(".review .rating")