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

// New Arrivals Carousel functionality
document.addEventListener('DOMContentLoaded', function() {
  const track = document.querySelector('.carousel-track');
  const products = track.children;
  const prevButton = document.querySelector('.carousel-control.prev');
  const nextButton = document.querySelector('.carousel-control.next');
  const goToStartButton = document.querySelector('.carousel-control.go-to-start');
  
  let currentIndex = 0;
  const productWidth = 280; // Fixed width
  const productGap = 40;
  
  function calculateProductsPerView() {
    // Calculate based on available width in track container
    const trackContainer = document.querySelector('.carousel-track-container');
    return Math.floor((trackContainer.offsetWidth + productGap) / (productWidth + productGap));
  }
  
  function calculateMaxIndex() {
    return Math.max(0, products.length - calculateProductsPerView());
  }
  
  function updateButtonStates() {
    prevButton.style.opacity = currentIndex === 0 ? '0.5' : '1';
    prevButton.style.cursor = currentIndex === 0 ? 'default' : 'pointer';
    
    nextButton.style.opacity = currentIndex >= calculateMaxIndex() ? '0.5' : '1';
    nextButton.style.cursor = currentIndex >= calculateMaxIndex() ? 'default' : 'pointer';
  }
  
  function moveSlide(direction) {
    if (direction === 'prev' && currentIndex > 0) {
      currentIndex--;
    } else if (direction === 'next' && currentIndex < calculateMaxIndex()) {
      currentIndex++;
    }
    
    const translateX = currentIndex * -(productWidth + productGap);
    track.style.transform = `translateX(${translateX}px)`;
    updateButtonStates();
  }
  
  function goToStart() {
    currentIndex = 0;
    track.style.transform = 'translateX(0)';
    updateButtonStates();
  }
  
  // Event listeners
  prevButton.addEventListener('click', () => moveSlide('prev'));
  nextButton.addEventListener('click', () => moveSlide('next'));
  goToStartButton.addEventListener('click', goToStart);
  
  // Initial button states
  updateButtonStates();
  
  // Update on window resize
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      const maxIndex = calculateMaxIndex();
      if (currentIndex > maxIndex) {
        currentIndex = maxIndex;
        const translateX = currentIndex * -(productWidth + productGap);
        track.style.transform = `translateX(${translateX}px)`;
      }
      updateButtonStates();
    }, 250);
  });
});