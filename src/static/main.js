document.addEventListener('DOMContentLoaded', () => {

    // --- Hamburger Menu ---
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        // Add a close button for mobile
        const closeBtn = document.createElement('div');
        closeBtn.className = 'mobile-close-btn';
        closeBtn.innerHTML = '&times;';
        navLinks.prepend(closeBtn);

        const closeMenu = () => {
            hamburger.classList.remove('active');
            navLinks.classList.remove('open');
        };

        hamburger.addEventListener('click', (e) => {
            e.stopPropagation();
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('open');
        });

        closeBtn.addEventListener('click', closeMenu);

        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', closeMenu);
        });

        // Close when clicking empty space inside nav-links (mobile background) or outside
        document.addEventListener('click', (e) => {
            if (navLinks.classList.contains('open') && !hamburger.contains(e.target)) {
                if (e.target === navLinks || !navLinks.contains(e.target)) {
                    closeMenu();
                }
            }
        });
    }

    // --- Sticky Navbar (Always visible) ---
    // The auto-hide feature has been removed as per user request.
    const header = document.querySelector('header');
    if (header) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
                header.style.boxShadow = '0 4px 25px rgba(107,33,200,0.6)';
                header.style.background = 'rgba(10, 3, 26, 0.95)';
            } else {
                header.style.boxShadow = '0 2px 20px rgba(107,33,200,0.3)';
                header.style.background = 'rgba(10, 3, 26, 0.75)';
            }
        }, { passive: true });
    }

    // --- Smooth Scrolling for Anchors ---
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // --- Swiper Slider Initialization (Lazy via IntersectionObserver) ---
    const swiperConfig = {
        slidesPerView: 1,
        spaceBetween: 20,
        loop: true,
        speed: 500,             // Smooth 500ms transition
        autoplay: {
            delay: 3000,
            disableOnInteraction: false,
            pauseOnMouseEnter: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        lazy: true,              // Enable lazy loading images inside slides
        watchSlidesProgress: true,
        breakpoints: {
            768: {
                slidesPerView: 2,
                spaceBetween: 30,
                autoplay: false,
            },
            1024: {
                slidesPerView: 3,
                spaceBetween: 40,
                autoplay: false,
            },
        }
    };

    // Use IntersectionObserver to only initialize Swiper when visible
    const swiperElements = document.querySelectorAll('.swiper');
    if ('IntersectionObserver' in window) {
        const swiperObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    new Swiper(entry.target, swiperConfig);
                    observer.unobserve(entry.target); // Init once only
                }
            });
        }, { rootMargin: '200px' });

        swiperElements.forEach(el => swiperObserver.observe(el));
    } else {
        // Fallback for browsers without IntersectionObserver
        swiperElements.forEach(el => new Swiper(el, swiperConfig));
    }

});