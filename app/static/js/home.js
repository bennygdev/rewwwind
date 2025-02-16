// Banner Carousel functionality
document.addEventListener("DOMContentLoaded", function() {
  const bannerSlides = document.querySelectorAll('.banner-slide');
  const bannerIndicators = document.querySelectorAll('.banner-indicator');
  const bannerIndicatorWrappers = document.querySelectorAll('.banner-indicator-wrapper');
  const bannerPrevButton = document.querySelector('.banner-control.prev');
  const bannerNextButton = document.querySelector('.banner-control.next');
  
  let currentBannerSlide = 0;
  let bannerIntervalId;
  const slideDuration = 8000;
  
  function showBannerSlide(index) {
    // Hide all slides first
    bannerSlides.forEach(slide => {
      slide.classList.remove('active');
      slide.style.display = 'none';
    });
    
    bannerIndicators.forEach(indicator => {
      indicator.classList.remove('active');
      void indicator.offsetWidth;
    });
    
    bannerSlides[index].classList.add('active');
    bannerSlides[index].style.display = 'block';
    bannerIndicators[index].classList.add('active');
    
    currentBannerSlide = index;
  }
  
  if (bannerPrevButton) {
    bannerPrevButton.addEventListener('click', () => {
      let newIndex = currentBannerSlide - 1;
      if (newIndex < 0) newIndex = bannerSlides.length - 1;
      showBannerSlide(newIndex);
      resetBannerInterval();
    });
  }
  
  if (bannerNextButton) {
    bannerNextButton.addEventListener('click', () => {
      let newIndex = currentBannerSlide + 1;
      if (newIndex >= bannerSlides.length) newIndex = 0;
      showBannerSlide(newIndex);
      resetBannerInterval();
    });
  }
  
  bannerIndicatorWrappers.forEach((wrapper, index) => {
    wrapper.addEventListener('click', () => {
      showBannerSlide(index);
      resetBannerInterval();
    });
  });
  
  function startBannerInterval() {
    bannerIntervalId = setInterval(() => {
      let newIndex = currentBannerSlide + 1;
      if (newIndex >= bannerSlides.length) newIndex = 0;
      showBannerSlide(newIndex);
    }, slideDuration);
  }
  
  function resetBannerInterval() {
    clearInterval(bannerIntervalId);
    startBannerInterval();
  }
  
  if (bannerSlides.length > 0) {
    bannerSlides.forEach(slide => {
      slide.style.display = 'none';
    });
    
    showBannerSlide(0);
    startBannerInterval();
  }
});

document.addEventListener("DOMContentLoaded", function () {
    const track = document.querySelector(".carousel-track");
    const slides = Array.from(track.children);
    const prevButton = document.querySelector(".carousel-control.prev");
    const nextButton = document.querySelector(".carousel-control.next");
    const goToStartButton = document.querySelector(".carousel-control.go-to-start");
    const carouselContainer = document.querySelector(".carousel-container");

    const slideWidth = slides[0].getBoundingClientRect().width;
    
    slides.forEach((slide, index) => {
        slide.style.left = `${slideWidth * index}px`;
    });

    let currentIndex = 0;
    let autoSlideInterval = null;
    let isAutoSliding = false;

    const moveToSlide = (targetSlideIndex) => {
        const amountToMove = -slideWidth * targetSlideIndex;
        track.style.transform = `translateX(${amountToMove}px)`;
        currentIndex = targetSlideIndex;
    };

    const startAutoSlide = () => {
        if (isAutoSliding) return; // prevent issue when switching tabs and trigger more than once
        isAutoSliding = true;
        autoSlideInterval = setInterval(() => {
            const nextIndex = (currentIndex + 1) % slides.length;
            moveToSlide(nextIndex);
        }, 3000);
    };

    const stopAutoSlide = () => {
        clearInterval(autoSlideInterval);
        isAutoSliding = false;
    };

    // Start auto-slide initially
    startAutoSlide();

    // pause upon hover
    carouselContainer.addEventListener("mouseover", stopAutoSlide);
    carouselContainer.addEventListener("mouseout", startAutoSlide);

    // pause when tab not active
    document.addEventListener("visibilitychange", () => {
        if (document.hidden) {
            stopAutoSlide();
        } else {
            startAutoSlide();
        }
    });

    // continuously move when button held down
    let intervalId;

    const handleHold = (direction) => {
        if (intervalId) clearInterval(intervalId);
        intervalId = setInterval(() => {
            const newIndex = currentIndex + direction;
            if (newIndex >= 0 && newIndex < slides.length) {
                moveToSlide(newIndex);
            } else {
                clearInterval(intervalId);
            }
        }, 200);
    };

    const handleSingleClick = (direction) => {
        const newIndex = currentIndex + direction;
        if (newIndex >= 0 && newIndex < slides.length) {
            moveToSlide(newIndex);
        }
    };
    
    // click and hold
    prevButton.addEventListener("mousedown", () => handleHold(-1));
    nextButton.addEventListener("mousedown", () => handleHold(1));
    document.addEventListener("mouseup", () => clearInterval(intervalId));

    // single click
    prevButton.addEventListener("click", () => handleSingleClick(-1));
    nextButton.addEventListener("click", () => handleSingleClick(1));

    // go to beginning
    goToStartButton.addEventListener("click", () => {
        moveToSlide(0);
    });
});

function adjustText() {
    if (window.innerWidth > 1400) {
        document.querySelectorAll('p.name').forEach(p => {
            if (parseFloat(getComputedStyle(p).width) >= 200) {
                p.innerText = p.innerText.slice(0, 11).trim() + '...'; // not foolproof i'd assume, but will just leave it as is for now
            }
        })
    } else {
        document.querySelectorAll('p.name').forEach(p => {
            if (parseFloat(getComputedStyle(p).width) >= 120) {
                p.innerText = p.innerText.slice(0, 6).trim() + '...';
            }
        })
    }
}

window.addEventListener('resize', adjustText);
adjustText();