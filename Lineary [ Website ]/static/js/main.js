document.addEventListener("DOMContentLoaded", () => {
    
    const notificationContainer = document.createElement('div');
    notificationContainer.className = 'notification-container';
    document.body.appendChild(notificationContainer);

    function showNotification(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        
        notificationContainer.appendChild(toast);
        
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    }

    const registerForm = document.getElementById("registerForm");

    // ==========================
// Date of Birth Limits
// Age: 16 - 25
// ==========================

const dobInput = document.getElementById("dob");

if (dobInput) {

    const today = new Date();

    // Youngest: 16 years old
    const maxDate = new Date(
        today.getFullYear() - 16,
        today.getMonth(),
        today.getDate()
    );

    // Oldest: 25 years old
    const minDate = new Date(
        today.getFullYear() - 25,
        today.getMonth(),
        today.getDate()
    );

    dobInput.max = maxDate
        .toISOString()
        .split("T")[0];

    dobInput.min = minDate
        .toISOString()
        .split("T")[0];
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
            
            // ==========================
            // Password Validation
            // ==========================

            const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/;

            if (!passwordRegex.test(password)) {

                showNotification(
                    "Password must be at least 8 characters and include both letters and numbers."
                );

                return;
            }

            if (password !== confirmPassword) {
                showNotification("Your passwords do not match. Please try again.");
                return;
            }

            registerForm.submit();
        });
    }

    // ==========================
    // Flask Notifications
    // ==========================

    if (window.flaskMessages) {

        window.flaskMessages.forEach(message => {

            showNotification(message);

        });

    }

    const observerOptions = {
        threshold: 0.15,
        rootMargin: "0px 0px -20px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const hiddenElements = document.querySelectorAll('.hidden');
    hiddenElements.forEach((el) => observer.observe(el));

    const signUpButton = document.getElementById('signUp');
    const signInButton = document.getElementById('signIn');
    const container = document.getElementById('authContainer');
    const showLogin = document.getElementById('showLogin');
    const showSignUp = document.getElementById('showSignUp');

    if (signUpButton && signInButton && container) {
        signUpButton.addEventListener('click', () => {
            container.classList.add("right-panel-active");
        });

        signInButton.addEventListener('click', () => {
            container.classList.remove("right-panel-active");
        });
    }

    if (showLogin && showSignUp && container) {
        showSignUp.addEventListener('click', () => {
            container.classList.add("right-panel-active");
        });
        showLogin.addEventListener('click', () => {
            container.classList.remove("right-panel-active");
        });
    }
});