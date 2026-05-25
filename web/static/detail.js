const editor = document.getElementById('editor');
const preview = document.getElementById('preview');
const previewContent = document.getElementById('preview-content');
const previewToggle = document.getElementById('preview-toggle');
const copyBtn = document.getElementById('copy-btn');

let previewVisible = false;

const copySVG = copyBtn.innerHTML;
const checkSVG = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;

const eyeSVG = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
const eyeOffSVG = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;

function updatePreview() {
    previewContent.innerHTML = marked.parse(editor.value);
}

previewToggle.addEventListener('click', () => {
    previewVisible = !previewVisible;
    preview.classList.toggle('hidden', !previewVisible);
    previewToggle.innerHTML = previewVisible
        ? `${eyeOffSVG}<span>Vorschau aus</span>`
        : `${eyeSVG}<span>Vorschau</span>`;
    if (previewVisible) updatePreview();
});

editor.addEventListener('input', () => {
    if (previewVisible) updatePreview();
});

copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(editor.value);
    copyBtn.innerHTML = checkSVG;
    setTimeout(() => { copyBtn.innerHTML = copySVG; }, 3000);
});