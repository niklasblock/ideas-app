const toggle = document.getElementById('theme-toggle');
let dark = window.matchMedia('(prefers-color-scheme: dark)').matches;

function applyTheme() {
    document.body.setAttribute('data-theme', dark ? 'dark' : 'light');
    toggle.textContent = dark ? '☀' : '☾';
}

toggle.addEventListener('click', () => {
    dark = !dark;
    applyTheme();
});

applyTheme();