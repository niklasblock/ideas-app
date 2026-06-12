// State
const state = {
    ideas: [],
    tabs: [],
    activeTab: null,
    darkMode: false,
    activeNav: 'ideas'
};

// API
const api = {
    async getIdeas() {
        const r = await fetch('/api/ideas');
        return r.json();
    },
    async addIdea(title) {
        const r = await fetch('/api/ideas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title })
        });
        return r.json();
    },
    async getIdea(id) {
        const r = await fetch(`/api/ideas/${id}`);
        return r.json();
    },
    async saveIdea(id, content) {
        await fetch(`/api/ideas/${id}/content`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
    },
    async saveMeta(id, data) {
        await fetch(`/api/ideas/${id}/meta`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    },
    async deleteIdea(id) {
        await fetch(`/api/ideas/${id}`, { method: 'DELETE' });
    },
    async addLink(id, toId, linkType) {
        await fetch(`/api/ideas/${id}/link`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ to_id: toId, link_type: linkType })
        });
    },
    async removeLink(id, toId, linkType) {
        await fetch(`/api/ideas/${id}/unlink`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ to_id: toId, link_type: linkType })
        });
    },
    async getRecall() {
        const r = await fetch('/api/recall');
        return r.json();
    },
    async getSimilar(id) {
        const r = await fetch(`/api/ideas/${id}/similar`);
        return r.json();
    }
};

// Tabs
function openTab(id, title, type = 'idea') {
    const existing = state.tabs.find(t => t.id === id);
    if (!existing) {
        state.tabs.push({ id, title, type });
    }
    state.activeTab = id;
    renderTabs();
    if (type === 'idea') loadDetailView(id);
    else if (type === 'ideas') loadIdeasView();
    else if (type === 'recall') loadRecallView();
    else if (type === 'graph') loadGraphView();
}

function closeTab(id) {
    state.tabs = state.tabs.filter(t => t.id !== id && String(t.id) !== String(id));
    if (state.activeTab === id || String(state.activeTab) === String(id)) {
        state.activeTab = state.tabs.length ? state.tabs[state.tabs.length - 1].id : null;
        if (state.activeTab) {
            const tab = state.tabs.find(t => t.id === state.activeTab);
            if (tab.type === 'idea') loadDetailView(state.activeTab);
            else if (tab.type === 'ideas') loadIdeasView();
            else if (tab.type === 'recall') loadRecallView();
            else if (tab.type === 'graph') loadGraphView();
        } else {
            loadIdeasView();
        }
    }
    renderTabs();
}

function renderTabs() {
    const bar = document.getElementById('tabs-bar');
    bar.innerHTML = state.tabs.map(tab => `
        <div class="tab ${state.activeTab === tab.id ? 'active' : ''}" data-tab-id="${tab.id}" data-tab-type="${tab.type}" data-tab-title="${tab.title.replace(/"/g, '&quot;')}">
            <i class="ti ti-file-text"></i>
            <span>${String(tab.title).length > 20 ? String(tab.title).slice(0, 20) + '…' : tab.title}</span>
            <span class="tab-close" data-close-id="${tab.id}"><i class="ti ti-x"></i></span>
        </div>
    `).join('');

    bar.querySelectorAll('.tab').forEach(el => {
        el.addEventListener('click', () => {
            const id = el.dataset.tabId;
            const type = el.dataset.tabType;
            const title = el.dataset.tabTitle;
            openTab(type === 'idea' ? parseInt(id) : id, title, type);
        });
    });

    bar.querySelectorAll('.tab-close').forEach(el => {
        el.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = el.dataset.closeId;
            closeTab(isNaN(id) ? id : parseInt(id));
        });
    });
}


// Views
async function loadIdeasView() {
    document.getElementById('main-content').style.padding = '';
    document.getElementById('main-content').style.overflow = '';
    state.ideas = await api.getIdeas();
    renderSidebarIdeas();
    const content = document.getElementById('main-content');
    content.innerHTML = `
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:24px;">
            <h1 style="font-size:22px; font-weight:500;">Alle Ideen</h1>
            <span style="font-size:13px; color:var(--text-tertiary)">${state.ideas.length} Ideen</span>
        </div>
        <div class="ideas-grid">
            ${state.ideas.map(idea => `
                <div class="idea-row" onclick="openIdeaTab(${idea.id}, '${idea.title.replace(/'/g, "\\'")}')">
                    <span class="idea-row-title">${idea.title}</span>
                    <div class="idea-row-meta">
                        ${idea.tags && idea.tags.length ? `<span class="tag">${idea.tags[0]}</span>` : ''}
                        <span class="status-badge status-${idea.context?.status || 'raw'}">${idea.context?.status || 'raw'}</span>
                        <span class="idea-row-date">${idea.time?.created || ''}</span>
                        <button class="idea-row-delete" onclick="deleteIdea(${idea.id}, event)" title="Löschen"><i class="ti ti-trash"></i></button>
                    </div>
                </div>
            `).join('')}
        </div>
        ${state.ideas.length === 0 ? '<div class="empty-state">Noch keine Ideen. Erstelle deine erste Idee!</div>' : ''}
    `;
}

function openIdeaTab(id, title) {
    openTab(id, title, 'idea');
    document.querySelectorAll('.idea-sidebar-item').forEach(el => {
        el.classList.toggle('active', el.dataset.id == id);
    });
}

async function loadDetailView(id) {
    if (!state.ideas.length) {
        state.ideas = await api.getIdeas();
    }
    document.getElementById('main-content').style.padding = '';
    document.getElementById('main-content').style.overflow = '';
    
    let idea, similar;
    try {
        idea = await api.getIdea(id);
        similar = await api.getSimilar(id);
    } catch(e) {
        console.error('Fehler beim Laden:', e);
        return;
    }
    
    console.log('idea:', idea);
    console.log('similar:', similar);

    const mainContent = document.getElementById('main-content');
    const allIdeas = state.ideas.filter(i => i.id !== id);  // diese Zeile fehlt
    mainContent.innerHTML = `
        <div class="detail-header">
            <h1 class="detail-title">${idea.title}</h1>
            <p class="detail-date">${idea.time?.created || ''} · zuletzt gesehen ${idea.time?.last_viewed || ''}</p>
            <div class="tags-row">
                ${(idea.tags || []).map(t => `<span class="tag">#${t}</span>`).join('')}
            </div>
        </div>

        <div class="meta-bar">
            <div class="meta-item">
                <label>Status</label>
                <select id="meta-status" onchange="saveMeta(${id})">
                    ${['raw','refined','applied','archived'].map(s => `<option ${idea.context?.status === s ? 'selected' : ''}>${s}</option>`).join('')}
                </select>
            </div>
            <div class="meta-item">
                <label>Wichtigkeit</label>
                <select id="meta-importance" onchange="saveMeta(${id})">
                    ${[1,2,3,4,5].map(i => `<option ${idea.context?.importance === i ? 'selected' : ''}>${i}</option>`).join('')}
                </select>
            </div>
            <div class="meta-item">
                <label>Energie</label>
                <select id="meta-energy" onchange="saveMeta(${id})">
                    ${['low','medium','high'].map(e => `<option ${idea.context?.energy === e ? 'selected' : ''}>${e}</option>`).join('')}
                </select>
            </div>
            <div class="meta-item" style="flex:1">
                <label>Tags</label>
                <input type="text" id="meta-tags" value="${(idea.tags || []).join(', ')}" placeholder="ki, business" onblur="saveMeta(${id})">
            </div>
        </div>

        <div class="editor-section">
            <div class="editor-toolbar">
                <button class="btn-sm" onclick="togglePreview()"><i class="ti ti-eye"></i> Vorschau</button>
                <button class="btn-sm" onclick="copyContent()"><i class="ti ti-copy"></i> Kopieren</button>
                <a href="/api/ideas/${id}/export/md" class="btn-sm" style="text-decoration:none;"><i class="ti ti-download"></i> .md</a>
            </div>
            <div style="display:flex; justify-content:flex-end; margin-bottom:8px;">
                <button class="btn-primary" onclick="saveContent(${id})">Speichern</button>
            </div>
            <div class="editor-split" id="editor-split">
                <textarea id="editor-textarea" oninput="updatePreview()">${idea.content || ''}</textarea>
            </div>
        </div>

        <div class="links-section">
            <div class="links-box">
                <h4>VERKNÜPFUNGEN</h4>
                <div id="links-list">
                    ${Object.entries(idea.links || {}).flatMap(([type, ids]) =>
                        ids.map(lid => {
                            const linked = state.ideas.find(i => i.id === lid);
                            return linked ? `
                                <div class="link-item">
                                    <span style="font-size:11px;color:var(--text-tertiary)">[${type}]</span>
                                    <a href="#" onclick="openIdeaTab(${linked.id}, '${linked.title.replace(/'/g, "\\'")}')">${linked.title}</a>
                                    <button onclick="removeLink(${id}, ${lid}, '${type}')" style="background:none;border:none;color:var(--text-tertiary);cursor:pointer;"><i class="ti ti-x"></i></button>
                                </div>` : '';
                        })
                    ).join('')}
                </div>
                <div class="add-link-row">
                    <select id="link-type">
                        ${['related','inspired_by','leads_to','part_of'].map(t => `<option>${t}</option>`).join('')}
                    </select>
                    <select id="link-target">
                        ${allIdeas.map(i => `<option value="${i.id}">${i.title}</option>`).join('')}
                    </select>
                    <button class="btn-sm" onclick="addLink(${id})">+ Verknüpfen</button>
                </div>
            </div>

            <div class="links-box">
                <h4>BACKLINKS</h4>
                ${(idea.backlinks || []).length ? idea.backlinks.map(b => `
                    <div class="link-item">
                        <a href="#" onclick="openIdeaTab(${b.id}, '${b.title.replace(/'/g, "\\'")}')">${b.title}</a>
                    </div>`).join('') : '<p style="color:var(--text-tertiary);font-size:13px;">Keine Backlinks</p>'}
            </div>

            <div class="links-box">
                <h4>ÄHNLICHE IDEEN</h4>
                ${similar.length ? similar.map(s => `
                    <div class="link-item">
                        <a href="#" onclick="openIdeaTab(${s.idea.id}, '${s.idea.title.replace(/'/g, "\\'")}')">${s.idea.title}</a>
                        <span style="font-size:11px;color:var(--text-tertiary)">${s.score}</span>
                    </div>`).join('') : '<p style="color:var(--text-tertiary);font-size:13px;">Keine ähnlichen Ideen</p>'}
            </div>
        </div>
    `;
}

async function loadRecallView() {
    document.getElementById('main-content').style.padding = '';
    document.getElementById('main-content').style.overflow = '';
    const data = await api.getRecall();
    const content = document.getElementById('main-content');
    content.innerHTML = `
        <h1 style="font-size:22px; font-weight:500; margin-bottom:24px;">Recall</h1>
        ${renderRecallSection('Zufällige Idee', data.random ? [data.random] : [], true)}
        ${renderRecallSection('Lange nicht gesehen', data.unseen)}
        ${renderRecallSection('Unverknüpfte Ideen', data.unlinked)}
    `;
}

function renderRecallSection(title, ideas, showRefresh = false) {
    return `
        <div style="margin-bottom:28px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <h3 style="font-size:15px;font-weight:500;">${title}</h3>
                ${!showRefresh ? `<span style="font-size:12px;padding:2px 8px;border-radius:20px;background:var(--bg-secondary);color:var(--text-tertiary);">${ideas.length}</span>` : ''}
                ${showRefresh ? `<button class="btn-sm" onclick="loadRecallView()"><i class="ti ti-refresh"></i></button>` : ''}
            </div>
            ${ideas.length ? ideas.map(idea => `
                <div class="idea-row" style="margin-bottom:6px;" onclick="openIdeaTab(${idea.id}, '${idea.title.replace(/'/g, "\\'")}')">
                    <span class="idea-row-title">${idea.title}</span>
                    <div class="idea-row-meta">
                        <span class="status-badge status-${idea.context?.status || 'raw'}">${idea.context?.status || 'raw'}</span>
                        <span class="idea-row-date">${idea.time?.last_viewed || ''}</span>
                    </div>
                </div>`).join('') : '<p style="color:var(--text-tertiary);font-size:13px;padding:8px 0;">Keine Ideen</p>'}
        </div>
    `;
}

function loadGraphView() {
    const content = document.getElementById('main-content');
    content.style.padding = '0';
    content.style.overflow = 'hidden';
    content.innerHTML = `<iframe src="/graph" style="width:100%;height:100%;border:none;"></iframe>`;
}

// Actions
async function saveContent(id) {
    const content = document.getElementById('editor-textarea').value;
    await api.saveIdea(id, content);
    const btn = document.querySelector('.btn-primary');
    const orig = btn.textContent;
    btn.textContent = '✓ Gespeichert';
    setTimeout(() => btn.textContent = orig, 2000);
}

async function saveMeta(id) {
    const status = document.getElementById('meta-status')?.value;
    const importance = parseInt(document.getElementById('meta-importance')?.value);
    const energy = document.getElementById('meta-energy')?.value;
    const tags = document.getElementById('meta-tags')?.value.split(',').map(t => t.trim()).filter(Boolean);
    await api.saveMeta(id, { status, importance, energy, tags });
}

async function deleteIdea(id, e) {
    e.stopPropagation();
    await api.deleteIdea(id);
    state.tabs = state.tabs.filter(t => t.id !== id);
    renderTabs();
    await loadIdeasView();
}

async function addLink(fromId) {
    const toId = parseInt(document.getElementById('link-target').value);
    const linkType = document.getElementById('link-type').value;
    await api.addLink(fromId, toId, linkType);
    await loadDetailView(fromId);
}

async function removeLink(fromId, toId, linkType) {
    await api.removeLink(fromId, toId, linkType);
    await loadDetailView(fromId);
}

let previewVisible = false;
function togglePreview() {
    previewVisible = !previewVisible;
    const split = document.getElementById('editor-split');
    if (previewVisible) {
        const content = document.getElementById('editor-textarea').value;
        split.innerHTML += `<div class="preview-box" id="preview-box">${marked.parse(content)}</div>`;
    } else {
        document.getElementById('preview-box')?.remove();
    }
}

function updatePreview() {
    const box = document.getElementById('preview-box');
    if (box) box.innerHTML = marked.parse(document.getElementById('editor-textarea').value);
}

function copyContent() {
    const text = document.getElementById('editor-textarea')?.value || '';
    navigator.clipboard.writeText(text);
}

// Sidebar
function renderSidebarIdeas() {
    const list = document.getElementById('ideas-list');
    list.innerHTML = state.ideas.map(idea => `
        <div class="idea-sidebar-item ${state.activeTab === idea.id ? 'active' : ''}" data-id="${idea.id}"
             onclick="openIdeaTab(${idea.id}, '${idea.title.replace(/'/g, "\\'")}')">
            <i class="ti ti-file-text"></i>
            <span style="overflow:hidden;text-overflow:ellipsis;">${idea.title}</span>
        </div>
    `).join('');
}

// Nav
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', e => {
        e.preventDefault();
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        item.classList.add('active');
        const view = item.dataset.view;
        document.getElementById('main-content').style.padding = '';
        if (view === 'ideas') {
            openTab('ideas', 'Alle Ideen', 'ideas');
        } else if (view === 'recall') {
            openTab('recall', 'Recall', 'recall');
        } else if (view === 'graph') {
            openTab('graph', 'Graph', 'graph');
        }
    });
});

// Theme
document.getElementById('theme-btn').addEventListener('click', () => {
    state.darkMode = !state.darkMode;
    document.body.classList.toggle('dark', state.darkMode);
    document.getElementById('theme-btn').innerHTML = state.darkMode ? '<i class="ti ti-sun"></i>' : '<i class="ti ti-moon"></i>';
});

// New Idea Modal
document.getElementById('new-idea-btn').addEventListener('click', () => {
    document.getElementById('modal-overlay').classList.remove('hidden');
    document.getElementById('new-idea-input').focus();
});

document.getElementById('modal-cancel').addEventListener('click', () => {
    document.getElementById('modal-overlay').classList.add('hidden');
    document.getElementById('new-idea-input').value = '';
});

document.getElementById('modal-confirm').addEventListener('click', async () => {
    const title = document.getElementById('new-idea-input').value.trim();
    if (!title) return;
    const idea = await api.addIdea(title);
    document.getElementById('modal-overlay').classList.add('hidden');
    document.getElementById('new-idea-input').value = '';
    state.ideas = await api.getIdeas();
    renderSidebarIdeas();
    openIdeaTab(idea.id, idea.title);
});

document.getElementById('new-idea-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') document.getElementById('modal-confirm').click();
    if (e.key === 'Escape') document.getElementById('modal-cancel').click();
});

// Marked für Markdown
const markedScript = document.createElement('script');
markedScript.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
document.head.appendChild(markedScript);

// Init
loadIdeasView();