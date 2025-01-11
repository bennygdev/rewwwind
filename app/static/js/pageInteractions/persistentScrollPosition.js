window.addEventListener('beforeunload', () => {
    localStorage.setItem('scrollPosition', window.scrollY);
});

window.addEventListener('load', () => {
    const scrollPosition = localStorage.getItem('scrollPosition');
    if (scrollPosition) {
        document.documentElement.style.scrollBehavior = 'auto'; // disable smooth scrolling
        window.scrollTo(0, parseInt(scrollPosition, 10));
        localStorage.removeItem('scrollPosition');

        // enable smooth scrolling
        setTimeout(() => {
            document.documentElement.style.scrollBehavior = '';
        }, 0);
    }
});