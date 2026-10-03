'use strict';
const form = document.querySelector('#login-form');
if (form) {
  form.addEventListener('submit', (event) => {
    const email = document.querySelector('#email').value.trim();
    const password = document.querySelector('#password').value;
    const emailError = document.querySelector('#email-error');
    const passwordError = document.querySelector('#password-error');
    emailError.textContent = !email ? 'Email is required.' : (!email.includes('@') ? 'Email must contain @.' : '');
    passwordError.textContent = !password ? 'Password is required.' : (password.length < 8 ? 'Password must be at least 8 characters.' : '');
    if (emailError.textContent || passwordError.textContent) event.preventDefault();
  });
}
