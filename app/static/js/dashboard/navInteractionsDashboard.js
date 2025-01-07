// scroll to stick navbar
document.addEventListener("DOMContentLoaded", () => {
  const navbar = document.querySelector('.main__navbar');
  const navbarHeight = 0;

  let isSticky = false;
  let lastScrollTop = 0;

  window.addEventListener("scroll", () => {
    let scrollTop = window.scrollY;

    if (scrollTop > lastScrollTop) {
      // Scroll down
      if (scrollTop > navbarHeight && !isSticky) {
        navbar.classList.add("sticky");
        isSticky = true;
      }
    } else {
      // Scroll up
      if (scrollTop <= navbarHeight && isSticky) {
        
        navbar.classList.remove("sticky");
        isSticky = false;
      }
    }

    lastScrollTop = scrollTop;
  });

  // Display option menu
  const navProfile = document.querySelector('.nav__profile');
  const optionMenu = document.querySelector('.nav__optionMenu');

  const displayMenu = () => {
    navProfile.classList.toggle('focused');
    optionMenu.style.display = optionMenu.style.display === 'block' ? 'none' : 'block';
  }

  const handleBlur = (event) => {
    if (!optionMenu.contains(event.relatedTarget)) {
      optionMenu.style.display = "none";
      navProfile.classList.remove("focused");
    }
  }

  navProfile.addEventListener('click', displayMenu);
  navProfile.addEventListener('focus', displayMenu);
  navProfile.addEventListener('blur', handleBlur);

  optionMenu.addEventListener('mousedown', (event) => {
    event.preventDefault();
  });

  document.addEventListener('click', (event) => {
    if (!navProfile.contains(event.target) && !optionMenu.contains(event.target)) {
      optionMenu.style.display = 'none';
      navProfile.classList.remove('focused');
    }
  });
  
});
