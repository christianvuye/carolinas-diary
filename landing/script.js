document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('waitlistForm');
    const emailInput = document.getElementById('email');
    const formMessage = document.getElementById('formMessage');

    // Check if user is already on waitlist
    const isOnWaitlist = localStorage.getItem('carolinasDiaryWaitlist');
    if (isOnWaitlist) {
        showMessage('You\'re already on the waitlist! We\'ll notify you when we launch.', 'success');
        form.style.display = 'none';
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = emailInput.value.trim();
        
        // Basic email validation
        if (!isValidEmail(email)) {
            showMessage('Please enter a valid email address.', 'error');
            return;
        }

        // Simulate form submission (in production, this would send to a backend)
        submitToWaitlist(email);
    });

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function submitToWaitlist(email) {
        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Joining...';
        submitButton.disabled = true;

        // Simulate API call with timeout
        setTimeout(() => {
            // Store in localStorage to prevent duplicate submissions
            localStorage.setItem('carolinasDiaryWaitlist', email);
            
            // Store in a waitlist array (for demo purposes)
            let waitlist = JSON.parse(localStorage.getItem('carolinasDiaryWaitlistAll') || '[]');
            if (!waitlist.includes(email)) {
                waitlist.push(email);
                localStorage.setItem('carolinasDiaryWaitlistAll', JSON.stringify(waitlist));
            }

            // Show success message
            showMessage('Success! You\'re on the waitlist. We\'ll email you when Carolina\'s Diary launches!', 'success');
            
            // Reset form
            emailInput.value = '';
            submitButton.textContent = originalText;
            submitButton.disabled = false;

            // Hide form after successful submission
            setTimeout(() => {
                form.style.display = 'none';
            }, 3000);

            // Log for demo purposes
            console.log('Waitlist:', waitlist);
        }, 1000);
    }

    function showMessage(message, type) {
        formMessage.textContent = message;
        formMessage.className = `form-message ${type}`;
        formMessage.style.display = 'block';

        // Auto-hide error messages
        if (type === 'error') {
            setTimeout(() => {
                formMessage.style.display = 'none';
            }, 5000);
        }
    }

    // Smooth scroll for CTA button
    const ctaButton = document.querySelector('.cta-button');
    if (ctaButton) {
        ctaButton.addEventListener('click', function(e) {
            if (this.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }

    // Add animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe feature cards
    const features = document.querySelectorAll('.feature');
    features.forEach(feature => {
        feature.style.opacity = '0';
        feature.style.transform = 'translateY(20px)';
        feature.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(feature);
    });
});