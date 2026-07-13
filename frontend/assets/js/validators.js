// Field-level checks shared by every create/edit form. Each validator
// returns an error message string, or null when the value is valid.
export function required(value, label = "This field") {
  if (value === undefined || value === null || String(value).trim() === "") {
    return `${label} is required.`;
  }
  return null;
}

export function isEmail(value) {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(value) ? null : "Enter a valid email address.";
}

export function minLength(value, min, label = "This field") {
  return String(value ?? "").length >= min
    ? null
    : `${label} must be at least ${min} characters.`;
}

export function positiveInteger(value, label = "This field") {
  const n = Number(value);
  return Number.isInteger(n) && n > 0 ? null : `${label} must be a positive number.`;
}

export function endAfterStart(startTime, endTime) {
  return startTime && endTime && endTime > startTime
    ? null
    : "End time must be after start time.";
}

// Applies a list of [fieldEl, validatorFns[]] pairs, toggling .has-error /
// .error-text on the closest .field wrapper. Returns true if the whole form is valid.
export function validateForm(fieldChecks) {
  let isValid = true;
  for (const [fieldEl, checks] of fieldChecks) {
    const wrapper = fieldEl.closest(".field");
    let message = null;
    for (const check of checks) {
      message = check(fieldEl.value);
      if (message) break;
    }
    if (wrapper) {
      wrapper.classList.toggle("has-error", Boolean(message));
      const errorEl = wrapper.querySelector(".error-text");
      if (errorEl) errorEl.textContent = message || "";
    }
    if (message) isValid = false;
  }
  return isValid;
}
