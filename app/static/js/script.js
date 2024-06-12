document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('nav a');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            if (link.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);

                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Mobile navigation toggle
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    const navigation = document.querySelector('.navigation ul');

    mobileNavToggle.addEventListener('click', () => {
        navigation.classList.toggle('active');
    });

    // Register form submission
    const registerForm = document.getElementById('registerForm');
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        const response = await fetch('/api/users/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password }),
        });

        const data = await response.json();
        if (response.ok) {
            alert('Registration successful!');
        } else {
            alert(`Registration failed: ${data.message}`);
        }
    });
});

function togglePassword() {
    var password = document.getElementById("password");
    var confirmPassword = document.getElementById("confirm_password");
    if (password.type === "password") {
        password.type = "text";
        if (confirmPassword) {
            confirmPassword.type = "text";
        }
    } else {
        password.type = "password";
        if (confirmPassword) {
            confirmPassword.type = "password";
        }
    }
}