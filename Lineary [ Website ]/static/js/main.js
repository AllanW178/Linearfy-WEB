document.addEventListener("DOMContentLoaded", () => {
    
    // Smooth Page Entry
    setTimeout(() => {
        document.body.classList.add('page-loaded');
    }, 50);

    // Toast Notifications Setup
    const notificationContainer = document.createElement('div');
    notificationContainer.className = 'notification-container';
    document.body.appendChild(notificationContainer);

    function showNotification(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `<span class="toast-icon"></span> ${message}`;
        
        notificationContainer.appendChild(toast);
        
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 500);
        }, 4000);
    }

    // Auth & Form Logic
    const registerForm = document.getElementById("registerForm");
    const dobInput = document.getElementById("dob");

    if (dobInput) {
        const today = new Date();
        const maxDate = new Date(today.getFullYear() - 16, today.getMonth(), today.getDate());
        const minDate = new Date(today.getFullYear() - 25, today.getMonth(), today.getDate());
        dobInput.max = maxDate.toISOString().split("T")[0];
        dobInput.min = minDate.toISOString().split("T")[0];
    }

    if (registerForm) {
        registerForm.setAttribute('novalidate', true);
        registerForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const inputs = registerForm.querySelectorAll('input[required]');
            
            for (let input of inputs) {
                if (!input.value.trim()) {
                    let fieldName = input.placeholder || input.name;
                    showNotification(`Please fill out the ${fieldName} field.`);
                    return;
                }
            }

            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirm_password").value;
            const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/;

            if (!passwordRegex.test(password)) {
                showNotification("Password must be at least 8 characters with letters and numbers.");
                return;
            }

            if (password !== confirmPassword) {
                showNotification("Passwords do not match. Please try again.");
                return;
            }

            registerForm.submit();
        });
    }

    if (window.flaskMessages) {
        window.flaskMessages.forEach(message => showNotification(message));
    }

    // Premium Staggered Intersection Observer
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // If it has a stagger class, extract the number and delay it
                let delay = 0;
                entry.target.classList.forEach(cls => {
                    if (cls.startsWith('stagger-')) {
                        delay = parseInt(cls.split('-')[1]) * 100; // 100ms per index
                    }
                });
                
                setTimeout(() => {
                    entry.target.classList.add('show');
                }, delay);
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.hidden').forEach((el) => observer.observe(el));

    // Auth Slider functionality
    const signUpButton = document.getElementById('signUp');
    const signInButton = document.getElementById('signIn');
    const container = document.getElementById('authContainer');
    const showLogin = document.getElementById('showLogin');
    const showSignUp = document.getElementById('showSignUp');

    if (signUpButton && signInButton && container) {
        signUpButton.addEventListener('click', () => container.classList.add("right-panel-active"));
        signInButton.addEventListener('click', () => container.classList.remove("right-panel-active"));
    }

    if (showLogin && showSignUp && container) {
        showSignUp.addEventListener('click', () => container.classList.add("right-panel-active"));
        showLogin.addEventListener('click', () => container.classList.remove("right-panel-active"));
    }
});
