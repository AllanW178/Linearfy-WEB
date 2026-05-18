function switchForm() {
    let signUpDiv = document.getElementById("signup-wrapper");
    let signInDiv = document.getElementById("signin-wrapper");

    // If sign-in is hidden, show it and hide sign-up
    if (signInDiv.style.display === "none" || signInDiv.style.display === "") {
        signInDiv.style.display = "flex"; 
        signUpDiv.style.display = "none";
    } else {
        signInDiv.style.display = "none";
        signUpDiv.style.display = "flex";
    }
}


// ======================================================= //

// [ IMPORTANT INFO ] //
let isSignedUpForUser = false;
let isLoggedInForUser = false;


// ======================================================= //

// [ UNIVERSAL POP-UP GUI FOR REMINDER. ] //
function popUpNotificationUI(infoContent) {
    const reminderUIElement = document.createElement("div");
    reminderUIElement.classList.add("pop-up-ui");

    reminderUIElement.innerHTML = `
        <div class="inner-notification-ui">
            <img src="/LINEARFY_IMG_ASSETS/Correct_Info.jpg">
            <span class="reminder-text-content">${infoContent}</span>

            <div class="confirm-action-btn">
                <span class="confirmation-text-btn">OK</span>
                <i class="ri-arrow-right-line"></i>
            </div>
        </div>
    
    `;

    document.body.append(reminderUIElement);

    const getCloseReminderUIBtn = reminderUIElement.querySelector('.confirm-action-btn');
    
    getCloseReminderUIBtn.addEventListener('click', () => {
        reminderUIElement.style.display = 'none'; 
    });
}

// ======================================================= //


// [ USER REGISTRATION (SIGN-UP) SYSTEM ] //
document.addEventListener("DOMContentLoaded", () => {
    const getSignUpAccountBtn = document.getElementById("sign-up-account-action-btn");

    const registFullNameInputField = document.getElementById("regist-full-name-critical-info");
    const registUserEmailInputField = document.getElementById("regist-email-critical-info");
    const registPasswordInputField = document.getElementById("regist-password-critical-info");
    const registPasswordConfirmationField = document.getElementById("login-password-critical-info-repeat");
    
    getSignUpAccountBtn.addEventListener("click", function() {
        let getRegistFullNameValue = registFullNameInputField.value.trim();
        let getRegistEmailValue = registUserEmailInputField.value.trim();
        let getRegistPasswordValue = registPasswordInputField.value.trim();
        let getRegistConfirmationValue = registPasswordConfirmationField.value.trim();
    
        if (!getRegistFullNameValue || !getRegistEmailValue || !getRegistPasswordValue || !getRegistConfirmationValue) {
            popUpNotificationUI("Fields cannot leave as blank.");
            return;

        } else {
            if (getRegistPasswordValue !== getRegistConfirmationValue) {
                popUpNotificationUI("Your passwords are not identical.");
                return;
            }
            isSignedUpForUser = true;
            userRegistrationCheck();
        }
    });
})


// ======================================================= //

// [ USER LOG-IN SYSTEM ] //
document.addEventListener("DOMContentLoaded", () => {
    const getLogInAccountBtn = document.getElementById("sign-in-account-action-btn");

    const loginEmailInputField = document.getElementById("login-email-critical-info");
    const passwordInputField = document.getElementById("login-password-critical-info");
    
    getLogInAccountBtn.addEventListener("click", () => {
        let getLoginEmailValue = loginEmailInputField.value.trim();
        let getLoginPasswordValue = passwordInputField.value.trim();
    
        if (!getLoginEmailValue || !getLoginPasswordValue) {
            popUpNotificationUI("Please make sure that every blank has been filled.");
            return;

        } else {
            isLoggedInForUser = true;
            userRegistrationCheck();
        }
    });
});

// ======================================================= //

// [ REGISTRATION PAGE FADE-OUT AFTER SUCCESSFUL ATTEMPT ] //
function userRegistrationCheck() {
    const registrationWrapperUI = document.getElementById("registration-container-ui");

    if (isSignedUpForUser) {
        registrationWrapperUI.classList.add("pop-out-animation");
        setTimeout(() => {
            registrationWrapperUI.style.display = "none";
        }, 500);

        popUpNotificationUI("Account registered successfully.")
        return;

    }
    
    if (isLoggedInForUser) {
        registrationWrapperUI.classList.add("pop-out-animation");
        setTimeout(() => {
            registrationWrapperUI.style.display = "none";
        }, 500);

        popUpNotificationUI("Logged in successfully.")
        return;
    }
}

// ============================================================ //

document.addEventListener("DOMContentLoaded", () => {
    const acquireAllNavigationBtns = document.querySelectorAll("[data-target]");
    const acquireAllVitalPages = document.querySelectorAll(".crucial-content-page");

    acquireAllVitalPages.forEach(everyPage => {
        if (everyPage.id !== "center-page") {
            everyPage.style.display = "none";
        }

    });

    acquireAllNavigationBtns.forEach(everyNavBtn => {
        everyNavBtn.addEventListener("click", function() {
            const getCorrespondingPageAttribute = everyNavBtn.getAttribute("data-target");
            const getPageHTMLElement = document.getElementById(getCorrespondingPageAttribute);

            const getAllNavigationBtns = document.querySelectorAll(".nav-btn");

            acquireAllVitalPages.forEach(eryPage => {
                eryPage.style.display = "none";
            });

            getPageHTMLElement.style.display = "flex";

            getAllNavigationBtns.forEach(eryNavBtn => {
                eryNavBtn.classList.remove("selected-nav-btn-background");
            });

            everyNavBtn.classList.add("selected-nav-btn-background");

        });

    });


});

document.addEventListener("DOMContentLoaded", () => {
    const settingsIcon = document.getElementById("user-setting-action-btn");
    const signOutBtn = document.querySelector(".user-sign-out-action-btn");

    settingsIcon.addEventListener("click", function() {
        if (signOutBtn.style.display === "none" || signOutBtn.style.display === "") {
            signOutBtn.style.display = "flex";
        } else {
            signOutBtn.style.display = "none";
        }
    });

});



