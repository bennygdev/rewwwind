function adjustText() {
    if (window.innerWidth > 1400) {
        document.querySelectorAll('.name p:first-child').forEach(p => {
            console.log(getComputedStyle(p).width)
            if (parseFloat(getComputedStyle(p).width) >= 250) {
                p.innerText = p.innerText.slice(0, 20).trim() + '...'; // not foolproof i'd assume, but will just leave it as is for now
            }
        })
    } else {
        document.querySelectorAll('.name p:first-child').forEach(p => {
            if (parseFloat(getComputedStyle(p).width) >= 180) {
                p.innerText = p.innerText.slice(0, 12).trim() + '...';
            }
        })
    }
}

window.addEventListener('resize', adjustText);
adjustText();


const WarningDiv = document.querySelector('.product__statistic.warning')
WarningDiv.addEventListener('click', () => {
    const params = new URLSearchParams(window.location.search);
    params.set('stock', 'lowest first')
    window.location.search = params.toString();
})