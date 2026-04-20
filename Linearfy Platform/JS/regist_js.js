
// We firstly build a simple UI switching.
function switchForm() {
    let signUpDiv = document.getElementById("signup-div");
    let signInDiv = document.getElementById("signin-div");

    if (signUpDiv.style.display !== "none") {
        signUpDiv.style.display = "none";
        signInDiv.style.display = "block";

    } else {
        signInDiv.style.display = "none";
        signUpDiv.style.display = "block";
    }

}