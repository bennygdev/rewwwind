const overlay = document.querySelector('.overlay');
const modal = document.querySelector('.modal');

if (overlay && modal) {
    const closeBtn1 = document.querySelector('.modal .success .bi-x-lg');
    const closeBtn2 = document.querySelector('.modal .success .button-wrapper input');
    const btns = [closeBtn1, closeBtn2]
    btns.forEach(btn => {
        btn.addEventListener('click', () => {
            overlay.style.display = 'none';
            modal.style.display = 'none';
        })
    });

    document.addEventListener('keydown', (e) => {
        if (e.key == 'Escape') {
            overlay.style.display = 'none';
            modal.style.display = 'none';
        }
    });
};