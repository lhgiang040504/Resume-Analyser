// Disables the submit button to prevent form submission with an invalid information.
const submitBtn = document.querySelector(".submit-btn");

// USERNAME
const usernameField = document.querySelector("#usernameField"); // id
const feedBackArea = document.querySelector(".invalid_feedback"); // class
usernameField.addEventListener("keyup", (e) => {
    const usernameVal = e.target.value;
  
    // clear Previous Validation
    usernameField.classList.remove("is-invalid");
    feedBackArea.style.display = "none";
  
    if (usernameVal.length > 0) {
        fetch("/authentication/username_validation", {
            body: JSON.stringify({ username: usernameVal }),
            method: "POST",
        })
        .then(res => res.json())
        .then((data) => {     
          if (data.username_error) {
            usernameField.classList.add("is-invalid");
            feedBackArea.style.display = "block";
            feedBackArea.innerHTML = `<p>${data.username_error}</p>`;
            submitBtn.disabled = true;
          } else {
            usernameField.classList.add("is-valid");
            submitBtn.removeAttribute("disabled");
          }
        });
    } else {
        usernameField.classList.remove("is-invalid");
        usernameField.classList.remove("is-valid");
        feedBackArea.style.display = "none";
    }
  });

// EMAIL
const emailField = document.querySelector("#emailField"); // id
const emailfeedBackArea = document.querySelector(".emailfeedBackArea"); // class
emailField.addEventListener("keyup", (e) => {
    const emailVal = e.target.value;
  
    // clear Previous Validation
    emailField.classList.remove("is-invalid");
    emailfeedBackArea.style.display = "none";
  
    if (emailVal.length > 0) {
        fetch("/authentication/email_validation", {
            body: JSON.stringify({ email: emailVal }),
            method: "POST",
        })
        .then(res => res.json())
        .then((data) => {     
          if (data.email_error) {
            emailField.classList.add("is-invalid");
            emailfeedBackArea.style.display = "block";
            emailfeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
            submitBtn.disabled = true;
          } else {
            emailField.classList.add("is-valid");
            submitBtn.removeAttribute("disabled");
          }
        });
    } else {
        emailField.classList.remove("is-invalid");
        emailField.classList.remove("is-valid");
        emailfeedBackArea.style.display = "none";
    }
  });

// PASSWORD
const passwordField = document.querySelector("#passwordField"); // id
const passwordFeedBackArea = document.querySelector(".passwordFeedBackArea"); // class
passwordField.addEventListener("keyup", (e) => {
    const passwordVal = e.target.value;
  
    // clear Previous Validation
    passwordField.classList.remove("is-invalid");
    passwordFeedBackArea.style.display = "none";
  
    if (passwordVal.length > 0) {
        fetch("/authentication/password_validation", {
            body: JSON.stringify({ password: passwordVal }),
            method: "POST",
        })
        .then(res => res.json())
        .then((data) => {     
          if (data.password_error) {
            passwordField.classList.add("is-invalid");
            passwordFeedBackArea.style.display = "block";
            passwordFeedBackArea.innerHTML = `<p>${data.password_error}</p>`;
            submitBtn.disabled = true;
          } else {
            passwordField.classList.add("is-valid");
            submitBtn.removeAttribute("disabled");
          }
        });
    } else {
      passwordField.classList.remove("is-invalid");
      passwordField.classList.remove("is-valid");
      passwordFeedBackArea.style.display = "none";
    }
  });
