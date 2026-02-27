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

        window.addEventListener('scroll', function () {
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

            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // --- Swiper Slider Initialization ---
    // Applies to both Portfolio and Courses Swiper Containers
    const swipers = document.querySelectorAll('.swiper');
    swipers.forEach((swiperEl) => {
        if (swiperEl) {
            new Swiper(swiperEl, {
                slidesPerView: 1,      // Show 1 item on mobile
                spaceBetween: 30,
                loop: true,
                autoplay: {
                    delay: 2000,
                    disableOnInteraction: false,
                },
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
                breakpoints: {
                    768: {
                        slidesPerView: 2, // Show 2 items on tablet
                        spaceBetween: 40,
                        autoplay: false,  // Disable autoplay
                    },
                    1024: {
                        slidesPerView: 3, // Show 3 items on desktop
                        spaceBetween: 50,
                        autoplay: false,  // Disable autoplay
                    },
                }
            });
        }
    });

});