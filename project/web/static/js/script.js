document.addEventListener('DOMContentLoaded', function() {

    /* ============================================================= */
    /* AOS (ANIMATE ON SCROLL) INITIALIZATION */
    /* ============================================================= */
    AOS.init({
        duration: 1000,
        easing: 'ease-in-out',
        once: true
    });


    /* ============================================================= */
    /* THEME TOGGLE FUNCTIONALITY */
    /* ============================================================= */
    const themeToggleButton = document.getElementById('theme-toggle');
    const body = document.body;

    // This check is necessary because the theme toggle button might not be on every page.
    if (themeToggleButton) {
        // Check for saved theme in local storage
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            body.classList.add('dark-theme');
            themeToggleButton.classList.add('active');
        }

        // Add click event listener to the toggle button
        themeToggleButton.addEventListener('click', function() {
            body.classList.toggle('dark-theme');
            themeToggleButton.classList.toggle('active');

            // Save the current theme to local storage
            if (body.classList.contains('dark-theme')) {
                localStorage.setItem('theme', 'dark');
            } else {
                localStorage.setItem('theme', 'light');
            }
        });
    }


    /* ============================================================= */
    /* CAROUSEL FUNCTIONALITY (FOR PROPERTY PAGE) */
    /* ============================================================= */
    // Note: These variables and functions are globally scoped inside the DOMContentLoaded listener.
    // They won't cause errors if the carousel elements don't exist on the current page.
    let slideIndex = 1;

    function showSlides(n) {
        let i;
        let slides = document.getElementsByClassName("carousel-item");
        let dots = document.getElementsByClassName("dot"); // Assuming you might have dots for navigation
        if (slides.length === 0) return; // Exit if no carousel on the page

        if (n > slides.length) { slideIndex = 1; }
        if (n < 1) { slideIndex = slides.length; }

        for (i = 0; i < slides.length; i++) {
            slides[i].style.display = "none";
        }
        
        // This is for dot indicators, if you add them later
        // for (i = 0; i < dots.length; i++) {
        //     dots[i].className = dots[i].className.replace(" active", "");
        // }

        slides[slideIndex - 1].style.display = "block";
        // if(dots.length > 0) {
        //     dots[slideIndex-1].className += " active";
        // }
    }

    // This function needs to be accessible globally if called from onclick attributes in HTML
    window.plusSlides = function(n) {
        showSlides(slideIndex += n);
    }
    
    // Initial call to show the first slide if a carousel exists
    showSlides(slideIndex);
});