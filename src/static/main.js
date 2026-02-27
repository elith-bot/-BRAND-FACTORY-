document.addEventListener('DOMContentLoaded', () => {
    // --- Hamburger Menu --- 
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
        });

        // Close menu when a link is clicked
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                if (navLinks.classList.contains('active')) {
                    hamburger.classList.remove('active');
                    navLinks.classList.remove('active');
                }
            });
        });
    }

    // --- Auto-hiding Navbar ---
    const header = document.querySelector('header');
    if (header) {
        let lastScrollTop = 0;
        const navbarHeight = header.offsetHeight;

        window.addEventListener('scroll', function() {
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

            if (scrollTop > lastScrollTop && scrollTop > navbarHeight) {
                header.classList.add('hidden');
            } else {
                header.classList.remove('hidden');
            }
            lastScrollTop = scrollTop <= 0 ? 0 : scrollTop; 
        }, false);
    }

    // --- Smooth Scrolling for Anchors ---
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if(targetElement){
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // --- Mobile Portfolio Slider ---
    const sliderContainer = document.querySelector('#portfolio .slider-container');
    if (sliderContainer) {
        const track = sliderContainer.querySelector('.portfolio-grid');
        const slides = Array.from(track.children);
        const nextButton = sliderContainer.querySelector('.next');
        const prevButton = sliderContainer.querySelector('.prev');

        if (track && nextButton && prevButton && slides.length > 0) {
            let currentIndex = 0;
            const slideCount = slides.length;

            function goToSlide(index) {
                if (index < 0) {
                    currentIndex = slideCount - 1;
                } else if (index >= slideCount) {
                    currentIndex = 0;
                } else {
                    currentIndex = index;
                }
                track.style.transform = 'translateX(-' + currentIndex * 100 + '%)';
            }

            nextButton.addEventListener('click', () => goToSlide(currentIndex + 1));
            prevButton.addEventListener('click', () => goToSlide(currentIndex - 1));

            function checkMobileView() {
                const isMobile = window.innerWidth <= 768;
                if (isMobile) {
                    // In mobile view, we make sure the slider is active
                    track.style.display = 'flex'; // Make sure the items are in a row
                } else {
                    // In desktop view, we reset the styles
                    track.style.transform = 'translateX(0%)';
                    track.style.display = 'grid'; // Revert to grid
                }
            }

            window.addEventListener('resize', checkMobileView);
            checkMobileView(); // Initial check
        }
    }
});