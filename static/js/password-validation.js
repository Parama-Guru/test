document.addEventListener('DOMContentLoaded', function() {
    const password = document.getElementById('password');
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
        element.querySelector('.icon').textContent = valid ? '✓' : '✗';
    }

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
}); 