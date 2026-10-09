/*
   LINEARFY - main.js
   A small amount of motion to make the site feel smoother.
   It uses normal browser JavaScript only, so it is easy to explain and edit.
*/

document.addEventListener('DOMContentLoaded', () => {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const navbar = document.querySelector('.navbar');

    // Let the page fade in after the browser has drawn it once.
    requestAnimationFrame(() => {
        document.body.classList.add('page-loaded');
    });

    // Make the sticky navigation feel slightly more solid after scrolling.
    function updateNavigation() {
        if (navbar) {
            navbar.classList.toggle('nav-scrolled', window.scrollY > 18);
        }
    }

    updateNavigation();
    window.addEventListener('scroll', updateNavigation, { passive: true });

    // Toast notifications. textContent is used so messages are treated as text, not HTML.
    const notificationContainer = document.createElement('div');
    notificationContainer.className = 'notification-container';
    notificationContainer.setAttribute('aria-live', 'polite');
    document.body.appendChild(notificationContainer);

    function showNotification(message) {
        const toast = document.createElement('div');
        const icon = document.createElement('span');
        const messageText = document.createElement('span');

        toast.className = 'toast';
        icon.className = 'toast-icon';
        messageText.textContent = message;

        toast.append(icon, messageText);
        notificationContainer.appendChild(toast);

        requestAnimationFrame(() => toast.classList.add('show'));

        window.setTimeout(() => {
            toast.classList.remove('show');
            window.setTimeout(() => toast.remove(), reduceMotion ? 0 : 350);
        }, 3600);
    }

    if (window.flaskMessages) {
        window.flaskMessages.forEach(showNotification);
    }

    // Registration checks give friendly feedback before the form reaches Flask.
    const registerForm = document.getElementById('registerForm');
    const dobInput = document.getElementById('dob');

    if (dobInput) {
        const today = new Date();
        const minimumAgeDate = new Date(today.getFullYear() - 18, today.getMonth(), today.getDate());
        dobInput.max = minimumAgeDate.toISOString().split('T')[0];
    }

    if (registerForm) {
        registerForm.setAttribute('novalidate', 'true');

        registerForm.addEventListener('submit', (event) => {
            const requiredInputs = registerForm.querySelectorAll('input[required]');

            for (const input of requiredInputs) {
                if (!input.value.trim()) {
                    event.preventDefault();
                    showNotification(`Please fill out the ${input.placeholder || input.name} field.`);
                    input.focus();
                    return;
                }
            }

            const password = document.getElementById('password');
            const confirmation = document.getElementById('confirm_password');
            const passwordRule = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/;

            if (!passwordRule.test(password.value)) {
                event.preventDefault();
                showNotification('Use at least 8 characters, including letters and numbers.');
                password.focus();
                return;
            }

            if (password.value !== confirmation.value) {
                event.preventDefault();
                showNotification('Your passwords do not match yet.');
                confirmation.focus();
            }
        });
    }

    // Reveal sections as they enter the screen. On reduced-motion devices, show them immediately.
    const hiddenElements = document.querySelectorAll('.hidden');

    if (reduceMotion || !('IntersectionObserver' in window)) {
        hiddenElements.forEach((element) => element.classList.add('show'));
    } else {
        const observer = new IntersectionObserver((entries, currentObserver) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;

                const staggerClass = [...entry.target.classList].find((className) =>
                    className.startsWith('stagger-')
                );
                const step = staggerClass ? Number(staggerClass.replace('stagger-', '')) : 0;

                window.setTimeout(() => {
                    entry.target.classList.add('show');
                }, step * 90);

                currentObserver.unobserve(entry.target);
            });
        }, {
            threshold: 0.12,
            rootMargin: '0px 0px -35px 0px'
        });

        hiddenElements.forEach((element) => observer.observe(element));
    }

    // Register/login panel controls.
    const authContainer = document.getElementById('authContainer');
    const signUpButton = document.getElementById('signUp');
    const signInButton = document.getElementById('signIn');
    const showLogin = document.getElementById('showLogin');
    const showSignUp = document.getElementById('showSignUp');

    if (authContainer) {
        signUpButton?.addEventListener('click', () => authContainer.classList.add('right-panel-active'));
        signInButton?.addEventListener('click', () => authContainer.classList.remove('right-panel-active'));
        showSignUp?.addEventListener('click', () => authContainer.classList.add('right-panel-active'));
        showLogin?.addEventListener('click', () => authContainer.classList.remove('right-panel-active'));
    }

    // Prevent accidental double clicks on checkout, add-to-cart and admin submit buttons.
    document.querySelectorAll('form').forEach((form) => {
        form.addEventListener('submit', () => {
            const submitButton = form.querySelector('button[type="submit"]');
            if (!submitButton || submitButton.dataset.keepEnabled === 'true') return;

            submitButton.disabled = true;
            submitButton.classList.add('is-submitting');
            window.setTimeout(() => {
                // Re-enable if the browser keeps the current page because the form was invalid.
                submitButton.disabled = false;
                submitButton.classList.remove('is-submitting');
            }, 1800);
        });
    });
});
