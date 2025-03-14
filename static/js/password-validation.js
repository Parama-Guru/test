document.addEventListener('DOMContentLoaded', function() {
    const password = document.getElementById('password');
    const passwordRequirements = document.getElementById('password-requirements');
    const confirmPassword = document.getElementById('confirm-password');
    
    const requirements = {
        lowercase: document.getElementById('lowercase'),
        uppercase: document.getElementById('uppercase'),
        number: document.getElementById('number'),
        special: document.getElementById('special'),
        length: document.getElementById('length'),
        space: document.getElementById('space')
    };

    const patterns = {
        lowercase: /[a-z]/,
        uppercase: /[A-Z]/,
        number: /[0-9]/,
        special: /[!@#$%^&*(),.?":{}|<>]/,
        length: /.{7,}/,
        space: /^\S*$/
    };

    function updateRequirement(element, valid) {
        element.classList.toggle('valid', valid);
        element.classList.toggle('invalid', !valid);
        element.querySelector('.icon').textContent = valid ? '✓' : '✕';
    }

    // Make password requirements visible by default
    passwordRequirements.style.display = 'block';

    // Remove the focus and click event listeners that show/hide requirements
    // since we want them visible all the time

    password.addEventListener('input', function() {
        const value = this.value;
        
        // Check each requirement
        updateRequirement(requirements.lowercase, patterns.lowercase.test(value));
        updateRequirement(requirements.uppercase, patterns.uppercase.test(value));
        updateRequirement(requirements.number, patterns.number.test(value));
        updateRequirement(requirements.special, patterns.special.test(value));
        updateRequirement(requirements.length, patterns.length.test(value));
        updateRequirement(requirements.space, patterns.space.test(value));
    });
    
    // Initialize validation on page load
    if (password.value) {
        const value = password.value;
        updateRequirement(requirements.lowercase, patterns.lowercase.test(value));
        updateRequirement(requirements.uppercase, patterns.uppercase.test(value));
        updateRequirement(requirements.number, patterns.number.test(value));
        updateRequirement(requirements.special, patterns.special.test(value));
        updateRequirement(requirements.length, patterns.length.test(value));
        updateRequirement(requirements.space, patterns.space.test(value));
    }
    
    // Check if passwords match
    if (confirmPassword) {
        confirmPassword.addEventListener('input', function() {
            const passwordValue = password.value;
            const confirmValue = this.value;
            
            if (confirmValue === '') {
                this.setCustomValidity('');
            } else if (passwordValue !== confirmValue) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
        
        // Update confirm password validation when password changes
        password.addEventListener('input', function() {
            if (confirmPassword.value !== '') {
                if (this.value !== confirmPassword.value) {
                    confirmPassword.setCustomValidity('Passwords do not match');
                } else {
                    confirmPassword.setCustomValidity('');
                }
            }
        });
    }
}); 