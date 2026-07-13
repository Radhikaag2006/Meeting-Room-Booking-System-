import { apiRequest } from "../api.js";
import { setToken, getToken, getRole, dashboardPathForRole } from "../auth.js";
import { required, isEmail, validateForm } from "../validators.js";

// Already have a valid-looking session? Skip the form.
if (getToken()) {
  window.location.href = dashboardPathForRole(getRole());
}

const form = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const submitBtn = document.getElementById("login-submit");
const errorBox = document.getElementById("login-error");

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.add("visible");
}

function hideError() {
  errorBox.classList.remove("visible");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideError();

  const isValid = validateForm([
    [emailInput, [(v) => required(v, "Email"), isEmail]],
    [passwordInput, [(v) => required(v, "Password")]],
  ]);
  if (!isValid) return;

  submitBtn.disabled = true;
  submitBtn.textContent = "Signing in…";

  try {
    const { access_token } = await apiRequest("/auth/login", {
      method: "POST",
      body: { email: emailInput.value.trim(), password: passwordInput.value },
    });
    setToken(access_token);
    window.location.href = dashboardPathForRole(getRole());
  } catch (err) {
    showError(err.message);
    submitBtn.disabled = false;
    submitBtn.textContent = "Sign in";
  }
});
