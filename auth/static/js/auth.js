function clearForm(form) {
    form.reset();
}

function clearMessage() {
    message.textContent = '';
    message.style.color = '';
}

const loginTab = document.getElementById('login-tab');
const registerTab = document.getElementById('register-tab');

const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');

const message = document.getElementById('message');

loginTab.onclick = () => {
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
    loginTab.classList.add('active');
    registerTab.classList.remove('active');
    clearForm(registerForm);
    clearMessage();
};

registerTab.onclick = () => {
    registerForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
    registerTab.classList.add('active');
    loginTab.classList.remove('active');
    clearForm(loginForm);
    clearMessage();
};

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const response = await fetch('/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: document.getElementById('login-username').value,
            password: document.getElementById('login-password').value
        })
    });

    const data = await response.json();

    if (response.ok) {
        localStorage.setItem('token', data.access_token);
        window.location.href = '/lobby';
    } 
    else {
        message.style.color = 'red';
        message.textContent = data.detail || 'Login error';
    }
});

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const response = await fetch('/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: document.getElementById('reg-username').value,
            email: document.getElementById('reg-email').value,
            password: document.getElementById('reg-password').value
        })
    });

    const data = await response.json();

    if (response.ok) {
        localStorage.setItem('token', data.access_token);
        window.location.href = '/lobby';
    } 
    else {
        message.style.color = 'red';
        message.textContent = data.detail || 'Registration error';
    }
});
