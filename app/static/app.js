/* ═══════════════════════════════════════════════════
   CLOUDOPS AI — app.js v4 (Fully Audited)
   Senior Frontend Engineer Pass — All JS Issues Fixed
═══════════════════════════════════════════════════ */

/* ── Constants ── */
const API_URL       = '/api/chat';
const MAX_SESSIONS  = 50;   // FIX: cap session count so localStorage doesn't grow unbounded
const MAX_CHARS     = 4000;
const STORAGE_KEY   = 'co_sessions';
const ACTIVE_KEY    = 'co_active_session';
const PREFS_KEY     = 'co_prefs';

/* ── DOM References ── */
const html          = document.documentElement;
const chatArea      = document.getElementById('chat-area');
const chatForm      = document.getElementById('chat-form');
const userInput     = document.getElementById('user-input');
const sendBtn       = document.getElementById('send-btn');
const charHint      = document.getElementById('char-hint');
const historyList   = document.getElementById('history-list');
const newChatBtn    = document.getElementById('new-chat-btn');
const sidebar       = document.getElementById('sidebar');
const sidebarOpenBtn  = document.getElementById('sidebar-open-btn');
const sidebarCloseBtn = document.getElementById('sidebar-close');
const themeToggle   = document.getElementById('theme-toggle');
const clearBtn      = document.getElementById('clear-btn');
const customizeBtn  = document.getElementById('customize-btn');
const customizePanel  = document.getElementById('customize-panel');
const customizeClose  = document.getElementById('customize-close');
const customizeOverlay = document.getElementById('customize-overlay');
const fontSizeSlider  = document.getElementById('font-size-slider');
const fontSizeVal     = document.getElementById('font-size-val');
const cpReset         = document.getElementById('cp-reset');

/* ── Settings Modal DOM References ── */
const settingsBtn         = document.getElementById('settings-btn');
const sidebarSettingsBtn  = document.getElementById('sidebar-settings-btn');
const settingsModal       = document.getElementById('settings-modal');
const settingsOverlay     = document.getElementById('settings-overlay');
const settingsClose       = document.getElementById('settings-close');
const cfgBaseUrl          = document.getElementById('cfg-base-url');
const cfgSpaceKey         = document.getElementById('cfg-space-key');
const cfgUserEmail        = document.getElementById('cfg-user-email');
const cfgApiToken         = document.getElementById('cfg-api-token');
const cfgTokenToggle      = document.getElementById('cfg-token-toggle');
const cfgModeLive         = document.getElementById('cfg-mode-live');
const cfgModeMock         = document.getElementById('cfg-mode-mock');
const settingsBadge       = document.getElementById('settings-badge');
const settingsBadgeText   = document.getElementById('settings-badge-text');
const settingsStatusMode  = document.getElementById('settings-status-mode');
const settingsActiveSpace = document.getElementById('settings-active-space');
const settingsActiveDomain= document.getElementById('settings-active-domain');
const settingsActiveUser  = document.getElementById('settings-active-user');
const settingsAlert       = document.getElementById('settings-alert');
const settingsAlertTitle  = document.getElementById('settings-alert-title');
const settingsAlertMsg    = document.getElementById('settings-alert-msg');
const settingsAlertIcon   = document.getElementById('settings-alert-icon');
const settingsAlertClose  = document.getElementById('settings-alert-close');
const settingsTestBtn     = document.getElementById('settings-test-btn');
const settingsSaveBtn     = document.getElementById('settings-save-btn');
const settingsResetBtn    = document.getElementById('settings-reset-btn');
const testSpinner         = document.getElementById('test-spinner');
const saveSpinner         = document.getElementById('save-spinner');
const testBtnText         = document.getElementById('test-btn-text');
const saveBtnText         = document.getElementById('save-btn-text');
const sidebarStatusDot    = document.getElementById('sidebar-status-dot');
const sidebarStatusText   = document.getElementById('sidebar-status-text');
const sidebarFooterMeta   = document.getElementById('sidebar-footer-meta');
const topbarBadge         = document.getElementById('topbar-badge');

/* ── State ── */
let allSessions      = {};   // { [uuid]: { id, title, timestamp, messages[] } }
let currentSessionId = null;
let isStreaming      = false;
let animRef          = null; // particle canvas RAF id
let activeConfig     = null;

/* ══════════════════════════════════════
   SESSION PERSISTENCE (localStorage)
══════════════════════════════════════ */
function loadSessions() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    allSessions = raw ? JSON.parse(raw) : {};
  } catch {
    allSessions = {};
  }
}

function saveSessions() {
  try {
    // FIX: prune to MAX_SESSIONS — keep newest ones
    const keys = Object.keys(allSessions).sort((a, b) =>
      (allSessions[b].timestamp || 0) - (allSessions[a].timestamp || 0)
    );
    if (keys.length > MAX_SESSIONS) {
      keys.slice(MAX_SESSIONS).forEach(k => delete allSessions[k]);
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(allSessions));
  } catch (e) {
    console.warn('[CloudOps AI] localStorage quota exceeded — clearing oldest sessions', e);
    // Fallback: clear all sessions if quota exceeded
    try { localStorage.removeItem(STORAGE_KEY); } catch {}
  }
}

function genId() {
  return 'co_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 7);
}

/* ══════════════════════════════════════
   PREFERENCES
══════════════════════════════════════ */
const DEFAULT_PREFS = {
  theme: 'light', accent: 'blue', density: 'comfortable',
  anim: 'normal', bg: 'mesh', fontSize: 15
};

function loadPrefs() {
  try {
    const raw = localStorage.getItem(PREFS_KEY);
    return raw ? { ...DEFAULT_PREFS, ...JSON.parse(raw) } : { ...DEFAULT_PREFS };
  } catch { return { ...DEFAULT_PREFS }; }
}

function savePrefs(prefs) {
  try { localStorage.setItem(PREFS_KEY, JSON.stringify(prefs)); } catch {}
}

function applyPrefs(prefs) {
  html.setAttribute('data-theme',   prefs.theme);
  html.setAttribute('data-accent',  prefs.accent);
  html.setAttribute('data-density', prefs.density);
  html.setAttribute('data-anim',    prefs.anim);
  html.setAttribute('data-bg',      prefs.bg);

  // FIX: font size only applied to chat-area via CSS variable, not html root font-size
  const sz = prefs.fontSize || 15;
  chatArea.style.setProperty('--content-size', sz + 'px');
  if (fontSizeSlider) fontSizeSlider.value = sz;
  if (fontSizeVal) fontSizeVal.textContent = sz + 'px';

  // Theme icon sync
  const sunIcon  = document.querySelector('.icon-sun');
  const moonIcon = document.querySelector('.icon-moon');
  if (sunIcon && moonIcon) {
    if (prefs.theme === 'dark') {
      sunIcon.style.display  = 'none';
      moonIcon.style.display = '';
    } else {
      sunIcon.style.display  = '';
      moonIcon.style.display = 'none';
    }
  }

  // Customization panel: sync active states
  // Swatches
  document.querySelectorAll('.swatch').forEach(s => {
    s.classList.toggle('active', s.dataset.accent === prefs.accent);
  });
  // Pills — density
  document.querySelectorAll('.cp-pill[data-density]').forEach(p => {
    p.classList.toggle('active', p.dataset.density === prefs.density);
  });
  // Pills — anim
  document.querySelectorAll('.cp-pill[data-anim]').forEach(p => {
    p.classList.toggle('active', p.dataset.anim === prefs.anim);
  });
  // Pills — bg
  document.querySelectorAll('.cp-pill[data-bg]').forEach(p => {
    p.classList.toggle('active', p.dataset.bg === prefs.bg);
  });

  // Particles canvas
  if (prefs.bg === 'particles') {
    startParticles();
  } else {
    stopParticles();
  }
}

/* ══════════════════════════════════════
   PARTICLE CANVAS
══════════════════════════════════════ */
function startParticles() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas || animRef) return;
  const ctx = canvas.getContext('2d');
  let particles = [];
  const resize = () => {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  };
  resize();
  window.addEventListener('resize', resize, { passive: true });

  const COUNT = 60;
  const accentColor = getComputedStyle(html).getPropertyValue('--accent').trim() || '#3b82f6';
  for (let i = 0; i < COUNT; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      r: Math.random() * 2 + 1
    });
  }

  function draw() {
    animRef = requestAnimationFrame(draw);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const isDark = html.getAttribute('data-theme') === 'dark';
    const dotColor  = isDark ? 'rgba(200,220,255,0.5)' : 'rgba(80,120,200,0.35)';
    const lineColor = isDark ? 'rgba(180,200,255,0.08)' : 'rgba(80,120,200,0.06)';

    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0) p.x = canvas.width;
      if (p.x > canvas.width) p.x = 0;
      if (p.y < 0) p.y = canvas.height;
      if (p.y > canvas.height) p.y = 0;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = dotColor;
      ctx.fill();
    });

    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 110) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = lineColor;
          ctx.lineWidth = (1 - dist / 110) * 1.5;
          ctx.stroke();
        }
      }
    }
  }
  draw();
}

function stopParticles() {
  if (animRef) {
    cancelAnimationFrame(animRef);
    animRef = null;
  }
  const canvas = document.getElementById('bg-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
}

/* ══════════════════════════════════════
   SIDEBAR
══════════════════════════════════════ */
function isMobile() { return window.innerWidth <= 768; }

// FIX: separate desktop (push layout) vs mobile (overlay) logic
let sidebarBackdrop = null;

function initSidebarBackdrop() {
  sidebarBackdrop = document.createElement('div');
  sidebarBackdrop.className = 'sidebar-backdrop';
  sidebarBackdrop.addEventListener('click', closeSidebar);
  document.body.appendChild(sidebarBackdrop);
}

function openSidebar() {
  if (isMobile()) {
    sidebar.classList.add('mobile-open');
    sidebar.classList.remove('collapsed');
    if (sidebarBackdrop) { sidebarBackdrop.classList.add('show'); }
  } else {
    sidebar.classList.remove('collapsed');
  }
  sidebarOpenBtn.setAttribute('aria-expanded', 'true');
  sidebarOpenBtn.style.display = 'none';
}

function closeSidebar() {
  if (isMobile()) {
    sidebar.classList.remove('mobile-open');
    if (sidebarBackdrop) { sidebarBackdrop.classList.remove('show'); }
  } else {
    sidebar.classList.add('collapsed');
  }
  sidebarOpenBtn.setAttribute('aria-expanded', 'false');
  sidebarOpenBtn.style.display = '';
}

function syncSidebarOnResize() {
  if (!isMobile()) {
    // On desktop, remove mobile-specific classes
    sidebar.classList.remove('mobile-open');
    if (sidebarBackdrop) { sidebarBackdrop.classList.remove('show'); }
    // Keep collapsed state if it was collapsed
  } else {
    // On mobile, desktop collapsed state doesn't apply
    sidebar.classList.remove('collapsed');
  }
}

sidebarOpenBtn.addEventListener('click', openSidebar);
sidebarCloseBtn.addEventListener('click', closeSidebar);
window.addEventListener('resize', syncSidebarOnResize, { passive: true });

/* ══════════════════════════════════════
   HISTORY RENDERING
══════════════════════════════════════ */
function renderHistory() {
  historyList.innerHTML = '';
  const sessions = Object.values(allSessions).sort((a, b) => b.timestamp - a.timestamp);

  if (sessions.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'history-empty';
    empty.innerHTML = `
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.4" aria-hidden="true">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
      <p>Conversations appear here</p>`;
    historyList.appendChild(empty);
    return;
  }

  sessions.forEach((session, idx) => {
    const wrap = document.createElement('div');
    wrap.className = 'history-item-wrap';
    wrap.setAttribute('role', 'listitem');

    const btn = document.createElement('button');
    btn.className = 'history-item' + (session.id === currentSessionId ? ' active' : '');
    btn.style.animationDelay = (idx * 0.04) + 's';
    btn.setAttribute('aria-label', `Switch to: ${session.title}`);
    btn.innerHTML = `
      <svg class="history-item-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
      <span class="history-item-text">${esc(session.title)}</span>`;
    btn.addEventListener('click', () => switchSession(session.id));

    const delBtn = document.createElement('button');
    delBtn.className = 'history-del-btn';
    delBtn.setAttribute('aria-label', `Delete conversation: ${session.title}`);
    delBtn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;
    delBtn.addEventListener('click', (e) => { e.stopPropagation(); deleteSession(session.id); });

    wrap.appendChild(btn);
    wrap.appendChild(delBtn);
    historyList.appendChild(wrap);
  });
}

/* ══════════════════════════════════════
   SESSION SWITCHING
══════════════════════════════════════ */
function switchSession(id) {
  if (id === currentSessionId) {
    if (isMobile()) closeSidebar();
    return;
  }
  currentSessionId = id;
  localStorage.setItem(ACTIVE_KEY, id);
  renderHistory();
  renderCurrentSessionChat();
  if (isMobile()) closeSidebar();
}

function deleteSession(id) {
  delete allSessions[id];
  saveSessions();
  if (id === currentSessionId) {
    startNewChat();
  } else {
    renderHistory();
  }
}

function startNewChat() {
  const id = genId();
  currentSessionId = id;
  allSessions[id] = { id, title: 'New conversation', timestamp: Date.now(), messages: [] };
  localStorage.setItem(ACTIVE_KEY, id);
  saveSessions();
  renderHistory();
  showWelcomeScreen();
  userInput.focus();
  if (isMobile()) closeSidebar();
}

/* ══════════════════════════════════════
   CHAT RENDERING
══════════════════════════════════════ */
function renderCurrentSessionChat() {
  chatArea.innerHTML = '';
  const session = allSessions[currentSessionId];
  if (!session || session.messages.length === 0) {
    showWelcomeScreen();
    return;
  }
  session.messages.forEach(msg => {
    if (msg.role === 'user') {
      chatArea.appendChild(renderUserMsgDOM(msg.content, msg.time));
    } else {
      chatArea.appendChild(renderBotMsgDOM(msg.content, msg.sources || [], msg.latencyMs || null, msg.time));
    }
  });
  scrollToBottom();
}

function showWelcomeScreen() {
  chatArea.innerHTML = '';
  const ws = document.createElement('div');
  ws.className = 'welcome-screen';
  ws.id = 'welcome-screen';
  ws.innerHTML = buildWelcomeHTML();
  chatArea.appendChild(ws);

  // FIX: staggered JS-driven animation delay for dynamically created chips
  const chips = ws.querySelectorAll('.chip');
  chips.forEach((chip, i) => {
    chip.style.animationDelay = (0.04 + i * 0.06) + 's';
    chip.addEventListener('click', () => {
      const q = chip.dataset.q;
      if (q) submitQuery(q);
    });
  });
}

function buildWelcomeHTML() {
  return `
    <div class="welcome-inner">
      <div class="welcome-orb-wrap" aria-hidden="true">
        <div class="welcome-orb">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>
          </svg>
        </div>
        <div class="orb-ring orb-ring-1"></div>
        <div class="orb-ring orb-ring-2"></div>
      </div>
      <h1 class="welcome-title">CloudOps <span class="title-highlight">AI</span> Assistant</h1>
      <p class="welcome-sub">AI-powered operations assistant grounded in your enterprise Confluence runbooks spanning GCP, AWS Networking, Kubernetes, Multi-Cloud, IAM, and Observability.</p>
      <div class="chips-section">
        <div class="chips-label">Explore Architecture &amp; Runbooks</div>
        <div class="chips-wrap">
          <button class="chip" data-q="Explain the GCP Core Services architecture and compare GKE, Cloud Run, and Compute Engine.">
            <span class="chip-tag">GCP</span>GCP Core Services &amp; Matrix
          </button>
          <button class="chip" data-q="How is AWS enterprise networking configured with Transit Gateway and VPC subnets?">
            <span class="chip-tag">AWS</span>AWS VPC &amp; Transit Gateway
          </button>
          <button class="chip" data-q="What is the multi-cloud hybrid mesh between GCP and AWS? Explain the VPN tunnels and BGP routing.">
            <span class="chip-tag">MESH</span>GCP &amp; AWS HA-VPN Mesh
          </button>
          <button class="chip" data-q="What is the CloudOps AI enterprise architecture and how does the reasoning loop work?">
            <span class="chip-tag">AI</span>CloudOps AI Architecture
          </button>
          <button class="chip" data-q="How does BigQuery Omni query data in AWS S3 without data egress fees?">
            <span class="chip-tag">DATA</span>BigQuery Omni Multi-Cloud
          </button>
          <button class="chip" data-q="What are the P1, P2 and P3 incident severity definitions and SLAs?">
            <span class="chip-tag">SLA</span>P1/P2/P3 Incident SLAs
          </button>
          <button class="chip" data-q="How do we implement Workload Identity Federation (WIF) between AWS and GCP?">
            <span class="chip-tag">IAM</span>Multi-Cloud Zero-Trust WIF
          </button>
          <button class="chip" data-q="How should I troubleshoot a GKE production pod that is crashing with CrashLoopBackOff?">
            <span class="chip-tag">K8S</span>GKE Pod CrashLoopBackOff
          </button>
        </div>
      </div>
    </div>`;
}

/* ── DOM Builders (used for live render AND history rehydration) ── */
function renderUserMsgDOM(content, time) {
  const row = document.createElement('div');
  row.className = 'msg-row user-row';
  row.innerHTML = `
    <div class="avatar user-av" aria-hidden="true">U</div>
    <div class="bubble" role="article" aria-label="Your message">
      <div class="bubble-content">${esc(content)}</div>
      ${time ? `<div class="bubble-time" aria-label="Sent at ${time}">${time}</div>` : ''}
    </div>`;
  return row;
}

function renderBotMsgDOM(content, sources, latencyMs, time) {
  const row = document.createElement('div');
  row.className = 'msg-row bot-row';

  const sourcesHTML = buildSourcesHTML(sources);
  const metaHTML = buildMetaHTML(content, latencyMs, time);

  row.innerHTML = `
    <div class="avatar bot-av" aria-hidden="true">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
        <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
      </svg>
    </div>
    <div class="bubble" role="article" aria-label="AI response">
      <div class="bubble-content" data-raw="${encodeURIComponent(content)}">${parseMarkdown(content)}</div>
      ${sourcesHTML}
      ${metaHTML}
    </div>`;

  // Ensure all links inside bot bubble open in a new tab
  row.querySelectorAll('a').forEach(a => {
    a.setAttribute('target', '_blank');
    a.setAttribute('rel', 'noopener noreferrer');
  });

  return row;
}

function buildSourcesHTML(sources) {
  if (!sources || sources.length === 0) return '';
  const cards = sources.map((s, i) => {
    const rel = s.relevance_score >= 0.8 ? 'high' : s.relevance_score >= 0.5 ? 'med' : 'low';
    const relLabel = rel === 'high' ? 'High' : rel === 'med' ? 'Relevant' : 'Related';
    return `
      <a class="source-card" href="${esc(s.url || '#')}" target="_blank" rel="noopener noreferrer"
         style="animation-delay:${(i * 0.05 + 0.04).toFixed(2)}s"
         aria-label="Source: ${esc(s.title)}">
        <div class="sc-title">${esc(s.title || 'Confluence Page')}</div>
        <div class="sc-meta">${esc(s.space_key || 'AITEST')} · Confluence</div>
        <div class="sc-footer">
          <span class="sc-rel ${rel}">${relLabel}</span>
          <span class="sc-link">View<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></span>
        </div>
      </a>`;
  }).join('');
  return `
    <div class="sources-area" aria-label="Source documents">
      <div class="sources-header">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        Sources (${sources.length})
      </div>
      <div class="sources-grid">${cards}</div>
    </div>`;
}

function buildMetaHTML(content, latencyMs, time) {
  const timeStr = time || nowTime();
  const latStr  = latencyMs ? `${(latencyMs / 1000).toFixed(1)}s` : '';
  return `
    <div class="bubble-meta">
      <span class="bubble-time">${timeStr}${latStr ? ' · ' + latStr : ''}</span>
      <button class="copy-btn" data-copy="${encodeURIComponent(content)}" aria-label="Copy response to clipboard">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        Copy
      </button>
    </div>`;
}

/* ── FIX: Copy via event delegation — no window.copyMsg global ── */
chatArea.addEventListener('click', async (e) => {
  const btn = e.target.closest('.copy-btn');
  if (!btn) return;
  const text = decodeURIComponent(btn.dataset.copy || '');
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    const orig = btn.innerHTML;
    btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>Copied`;
    btn.style.color = '#10b981';
    btn.style.borderColor = 'rgba(16,185,129,0.3)';
    setTimeout(() => {
      btn.innerHTML = orig;
      btn.style.color = '';
      btn.style.borderColor = '';
    }, 2000);
  } catch {
    btn.textContent = 'Failed';
    setTimeout(() => { btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>Copy`; }, 1500);
  }
});

// Ensure ANY link clicked anywhere in the app always opens in a new tab
document.addEventListener('click', (e) => {
  const link = e.target.closest('a');
  if (link && link.getAttribute('href') && !link.getAttribute('href').startsWith('#') && !link.getAttribute('href').startsWith('javascript:')) {
    link.setAttribute('target', '_blank');
    link.setAttribute('rel', 'noopener noreferrer');
  }
}, true);

/* ══════════════════════════════════════
   QUERY SUBMISSION
══════════════════════════════════════ */
async function submitQuery(queryText) {
  const q = (queryText || userInput.value).trim();
  if (!q || isStreaming) return;

  isStreaming = true;
  sendBtn.disabled = true;
  userInput.value = '';
  userInput.style.height = 'auto';
  charHint.textContent = '';

  // Hide welcome screen if present
  const ws = document.getElementById('welcome-screen');
  if (ws) {
    ws.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
    ws.style.opacity = '0';
    ws.style.transform = 'translateY(-12px)';
    setTimeout(() => { if (ws.parentNode) ws.parentNode.removeChild(ws); }, 220);
  }

  const now = nowTime();

  // Save user message to session
  const session = allSessions[currentSessionId];
  if (!session) return;
  if (session.messages.length === 0) {
    session.title = q.slice(0, 52) + (q.length > 52 ? '...' : '');
  }
  session.messages.push({ role: 'user', content: q, time: now });
  session.timestamp = Date.now();
  saveSessions();
  renderHistory();

  // Render user bubble
  const userRow = renderUserMsgDOM(q, now);
  chatArea.appendChild(userRow);
  scrollToBottom();

  // Render typing indicator
  const typingRow = document.createElement('div');
  typingRow.className = 'msg-row bot-row';
  typingRow.id = 'typing-indicator';
  typingRow.innerHTML = `
    <div class="avatar bot-av" aria-hidden="true">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
        <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
      </svg>
    </div>
    <div class="typing-bubble" role="status" aria-live="polite" aria-label="AI is thinking">
      <div class="typing-dots" aria-hidden="true">
        <span></span><span></span><span></span>
      </div>
      <span class="typing-text">Querying Confluence and reasoning...</span>
    </div>`;
  chatArea.appendChild(typingRow);
  scrollToBottom();

  try {
    const t0 = Date.now();
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: q, session_id: currentSessionId })
    });
    if (!res.ok) throw new Error(`Server error ${res.status}: ${res.statusText}`);
    const data = await res.json();
    const latencyMs = Date.now() - t0;
    const answer  = data.answer  || 'No answer returned.';
    const sources = data.sources || [];

    // Remove typing indicator
    const ti = document.getElementById('typing-indicator');
    if (ti) ti.parentNode.removeChild(ti);

    // Save bot message
    const botTime = nowTime();
    session.messages.push({ role: 'bot', content: answer, sources, latencyMs, time: botTime });
    saveSessions();

    // Render bot bubble
    const botRow = renderBotMsgDOM(answer, sources, latencyMs, botTime);
    chatArea.appendChild(botRow);
    scrollToBottom();

  } catch (err) {
    const ti = document.getElementById('typing-indicator');
    if (ti) ti.parentNode.removeChild(ti);

    const errDiv = document.createElement('div');
    errDiv.className = 'error-msg';
    errDiv.setAttribute('role', 'alert');
    errDiv.textContent = '[Error] ' + (err.message || 'Request failed. Please try again.');
    chatArea.appendChild(errDiv);

    // Save error to session
    session.messages.push({ role: 'bot', content: '[Error] ' + err.message, sources: [], time: nowTime() });
    saveSessions();
    scrollToBottom();
  } finally {
    isStreaming = false;
    sendBtn.disabled = false;
    userInput.focus();
  }
}

/* ══════════════════════════════════════
   FORM & INPUT
══════════════════════════════════════ */
chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  submitQuery();
});

userInput.addEventListener('keydown', (e) => {
  // FIX: also block Enter submission when disabled
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) submitQuery();
  }
});

userInput.addEventListener('input', () => {
  // Auto-grow textarea
  userInput.style.height = 'auto';
  userInput.style.height = Math.min(userInput.scrollHeight, 160) + 'px';

  // Character count hint
  const len = userInput.value.length;
  if (len > MAX_CHARS * 0.8) {
    charHint.textContent = `${len}/${MAX_CHARS}`;
    charHint.style.color = len >= MAX_CHARS ? '#ef4444' : '';
  } else {
    charHint.textContent = '';
  }
  if (len >= MAX_CHARS) {
    userInput.value = userInput.value.slice(0, MAX_CHARS);
  }
});

/* ══════════════════════════════════════
   TOPBAR CONTROLS
══════════════════════════════════════ */
// Theme toggle
themeToggle.addEventListener('click', () => {
  const prefs = loadPrefs();
  prefs.theme = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
  savePrefs(prefs);
  applyPrefs(prefs);
});

// Clear chat
clearBtn.addEventListener('click', () => {
  if (!currentSessionId) return;
  allSessions[currentSessionId].messages = [];
  allSessions[currentSessionId].title = 'New conversation';
  saveSessions();
  showWelcomeScreen();
  renderHistory();
});

// New chat
newChatBtn.addEventListener('click', startNewChat);

/* ══════════════════════════════════════
   CUSTOMIZATION PANEL
══════════════════════════════════════ */
function openCustomizePanel() {
  customizePanel.classList.add('open');
  customizeOverlay.classList.add('show');
  customizeBtn.setAttribute('aria-expanded', 'true');
  // Focus first interactive element in panel
  setTimeout(() => { const f = customizePanel.querySelector('button, input'); if (f) f.focus(); }, 80);
}
function closeCustomizePanel() {
  customizePanel.classList.remove('open');
  customizeOverlay.classList.remove('show');
  customizeBtn.setAttribute('aria-expanded', 'false');
  customizeBtn.focus();
}

customizeBtn.addEventListener('click', () => {
  if (customizePanel.classList.contains('open')) closeCustomizePanel();
  else openCustomizePanel();
});
customizeClose.addEventListener('click', closeCustomizePanel);
customizeOverlay.addEventListener('click', closeCustomizePanel);

// FIX: Escape key closes settings modal, customize panel, or sidebar
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if (settingsModal && settingsModal.classList.contains('open')) { closeSettingsModal(); return; }
    if (customizePanel && customizePanel.classList.contains('open')) { closeCustomizePanel(); return; }
    if (isMobile() && sidebar && sidebar.classList.contains('mobile-open')) { closeSidebar(); }
  }
});

/* ══════════════════════════════════════
   SETTINGS MODAL CONTROLLER
══════════════════════════════════════ */
async function loadSettings(populateForm = true) {
  try {
    const res = await fetch('/api/settings');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    activeConfig = data;

    if (populateForm) {
      if (cfgBaseUrl) cfgBaseUrl.value = data.base_url || '';
      if (cfgSpaceKey) cfgSpaceKey.value = data.space_key || '';
      if (cfgUserEmail) cfgUserEmail.value = data.user_email || '';
      if (cfgApiToken) {
        cfgApiToken.value = '';
        cfgApiToken.placeholder = data.has_token ? `Stored: ${data.masked_token} (leave empty to keep)` : 'Enter Atlassian API Token';
      }
      if (data.use_mock) {
        if (cfgModeMock) cfgModeMock.checked = true;
      } else {
        if (cfgModeLive) cfgModeLive.checked = true;
      }
    }

    updateSettingsUIState(data);
    return data;
  } catch (err) {
    console.warn('Could not load settings:', err);
    return null;
  }
}

function updateSettingsUIState(data) {
  if (!data) return;
  const isOk = data.health && data.health.status === 'ok';
  const isLive = data.health && data.health.mode === 'live';
  const space = data.space_key || 'AITEST';
  const domain = (data.base_url || '').replace(/^https?:\/\//, '').replace(/\/.*$/, '') || 'confluence';

  if (settingsBadge && settingsBadgeText) {
    if (isOk && isLive) {
      settingsBadge.className = 'status-badge live';
      settingsBadgeText.textContent = 'CONNECTED (LIVE)';
      if (settingsStatusMode) settingsStatusMode.textContent = 'Mode: Live Cloud REST API';
    } else if (isOk && !isLive) {
      settingsBadge.className = 'status-badge mock';
      settingsBadgeText.textContent = 'OFFLINE (MOCK)';
      if (settingsStatusMode) settingsStatusMode.textContent = 'Mode: Local Mock Store';
    } else {
      settingsBadge.className = 'status-badge error';
      settingsBadgeText.textContent = 'DISCONNECTED / ERROR';
      if (settingsStatusMode) settingsStatusMode.textContent = 'Mode: Unavailable';
    }
  }

  if (settingsActiveSpace) settingsActiveSpace.textContent = space;
  if (settingsActiveDomain) settingsActiveDomain.textContent = domain;
  if (settingsActiveUser) settingsActiveUser.textContent = data.user_email || '--';

  // Update sidebar status & topbar badge
  if (sidebarStatusDot && sidebarStatusText) {
    if (isOk && isLive) {
      sidebarStatusDot.style.background = '#10b981';
      sidebarStatusText.textContent = 'Live Connected';
    } else if (isOk) {
      sidebarStatusDot.style.background = '#f59e0b';
      sidebarStatusText.textContent = 'Mock Fallback';
    } else {
      sidebarStatusDot.style.background = '#ef4444';
      sidebarStatusText.textContent = 'Connection Error';
    }
  }
  if (sidebarFooterMeta) {
    sidebarFooterMeta.textContent = `Space: ${space} · Confluence`;
  }
  if (topbarBadge) {
    topbarBadge.textContent = `${space} · ${isLive ? 'Live Runbooks' : 'Mock Runbooks'}`;
  }
}

function openSettingsModal() {
  hideSettingsAlert();
  if (settingsModal) settingsModal.classList.add('open');
  if (settingsOverlay) settingsOverlay.classList.add('show');
  loadSettings(true);
  setTimeout(() => { if (cfgBaseUrl) cfgBaseUrl.focus(); }, 100);
}

function closeSettingsModal() {
  if (settingsModal) settingsModal.classList.remove('open');
  if (settingsOverlay) settingsOverlay.classList.remove('show');
}

function showSettingsAlert(type, title, msg) {
  if (!settingsAlert) return;
  settingsAlert.className = `settings-alert ${type}`;
  if (settingsAlertTitle) settingsAlertTitle.textContent = title;
  if (settingsAlertMsg) settingsAlertMsg.textContent = msg;

  if (settingsAlertIcon) {
    if (type === 'success') {
      settingsAlertIcon.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`;
    } else if (type === 'error') {
      settingsAlertIcon.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;
    } else {
      settingsAlertIcon.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`;
    }
  }
  settingsAlert.classList.remove('hidden');
}

function hideSettingsAlert() {
  if (settingsAlert) settingsAlert.classList.add('hidden');
}

async function handleTestConnection() {
  const url = cfgBaseUrl.value.trim();
  const email = cfgUserEmail.value.trim();
  const token = cfgApiToken.value.trim();
  const space = cfgSpaceKey.value.trim();

  if (!url) {
    showSettingsAlert('error', 'Missing URL', 'Please provide a valid Confluence Base URL.');
    cfgBaseUrl.focus();
    return;
  }
  if (!email) {
    showSettingsAlert('error', 'Missing Email', 'Please provide your Atlassian user email.');
    cfgUserEmail.focus();
    return;
  }
  if (!space) {
    showSettingsAlert('error', 'Missing Space Key', 'Please specify the target Confluence Space Key.');
    cfgSpaceKey.focus();
    return;
  }

  settingsTestBtn.disabled = true;
  if (testSpinner) testSpinner.classList.remove('hidden');
  if (testBtnText) testBtnText.textContent = 'Verifying...';
  hideSettingsAlert();

  try {
    const res = await fetch('/api/settings/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        base_url: url,
        user_email: email,
        api_token: token || undefined,
        space_key: space
      })
    });
    const result = await res.json();
    if (result.success) {
      showSettingsAlert('success', 'Connection Verified ✓', result.message);
    } else {
      showSettingsAlert('error', 'Verification Failed ✕', result.message || 'Could not verify Confluence connectivity.');
    }
  } catch (err) {
    showSettingsAlert('error', 'Network Error', `Could not contact server: ${err.message}`);
  } finally {
    settingsTestBtn.disabled = false;
    if (testSpinner) testSpinner.classList.add('hidden');
    if (testBtnText) testBtnText.textContent = 'Test Connection';
  }
}

async function handleSaveSettings() {
  const url = cfgBaseUrl.value.trim();
  const email = cfgUserEmail.value.trim();
  const token = cfgApiToken.value.trim();
  const space = cfgSpaceKey.value.trim();
  const useMock = cfgModeMock && cfgModeMock.checked;

  if (!url) {
    showSettingsAlert('error', 'Validation Error', 'Confluence Base URL is required.');
    cfgBaseUrl.focus();
    return;
  }
  if (!email) {
    showSettingsAlert('error', 'Validation Error', 'Atlassian account email is required.');
    cfgUserEmail.focus();
    return;
  }
  if (!space) {
    showSettingsAlert('error', 'Validation Error', 'Target space key is required.');
    cfgSpaceKey.focus();
    return;
  }

  settingsSaveBtn.disabled = true;
  if (saveSpinner) saveSpinner.classList.remove('hidden');
  if (saveBtnText) saveBtnText.textContent = 'Applying...';
  hideSettingsAlert();

  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        base_url: url,
        user_email: email,
        api_token: token || undefined,
        space_key: space,
        use_mock: useMock
      })
    });
    const result = await res.json();
    if (result.success) {
      showSettingsAlert('success', 'Environment Switched ✓', result.message);
      await loadSettings(false);
    } else {
      showSettingsAlert('error', 'Update Failed', result.message || 'Could not save settings.');
    }
  } catch (err) {
    showSettingsAlert('error', 'Save Error', `Request failed: ${err.message}`);
  } finally {
    settingsSaveBtn.disabled = false;
    if (saveSpinner) saveSpinner.classList.add('hidden');
    if (saveBtnText) saveBtnText.textContent = 'Save & Switch Environment';
  }
}

function toggleTokenVisibility() {
  if (!cfgApiToken) return;
  const isPass = cfgApiToken.type === 'password';
  cfgApiToken.type = isPass ? 'text' : 'password';
  const openEye = cfgTokenToggle.querySelector('.eye-open');
  const closedEye = cfgTokenToggle.querySelector('.eye-closed');
  if (openEye && closedEye) {
    if (isPass) {
      openEye.classList.add('hidden');
      closedEye.classList.remove('hidden');
    } else {
      openEye.classList.remove('hidden');
      closedEye.classList.add('hidden');
    }
  }
}

// Bind Settings Event Listeners
if (settingsBtn) settingsBtn.addEventListener('click', openSettingsModal);
if (sidebarSettingsBtn) sidebarSettingsBtn.addEventListener('click', openSettingsModal);
if (settingsClose) settingsClose.addEventListener('click', closeSettingsModal);
if (settingsOverlay) settingsOverlay.addEventListener('click', closeSettingsModal);
if (settingsTestBtn) settingsTestBtn.addEventListener('click', handleTestConnection);
if (settingsSaveBtn) settingsSaveBtn.addEventListener('click', handleSaveSettings);
if (settingsResetBtn) settingsResetBtn.addEventListener('click', () => loadSettings(true));
if (cfgTokenToggle) cfgTokenToggle.addEventListener('click', toggleTokenVisibility);
if (settingsAlertClose) settingsAlertClose.addEventListener('click', hideSettingsAlert);

// Accent swatches
document.querySelectorAll('.swatch').forEach(s => {
  s.addEventListener('click', () => {
    const prefs = loadPrefs();
    prefs.accent = s.dataset.accent;
    savePrefs(prefs);
    applyPrefs(prefs);
  });
});

// Pills — density / anim / bg
document.querySelectorAll('.cp-pill').forEach(p => {
  p.addEventListener('click', () => {
    const prefs = loadPrefs();
    if (p.dataset.density) prefs.density = p.dataset.density;
    if (p.dataset.anim)    prefs.anim    = p.dataset.anim;
    if (p.dataset.bg)      prefs.bg      = p.dataset.bg;
    savePrefs(prefs);
    applyPrefs(prefs);
  });
});

// FIX: Font size slider — only affects .chat-area via --content-size var
fontSizeSlider.addEventListener('input', () => {
  const sz = parseInt(fontSizeSlider.value, 10);
  fontSizeVal.textContent = sz + 'px';
  // Only sets the variable on chat-area, not on html root
  chatArea.style.setProperty('--content-size', sz + 'px');
  const prefs = loadPrefs();
  prefs.fontSize = sz;
  savePrefs(prefs);
});

// Reset
cpReset.addEventListener('click', () => {
  savePrefs({ ...DEFAULT_PREFS });
  applyPrefs({ ...DEFAULT_PREFS });
  fontSizeSlider.value = DEFAULT_PREFS.fontSize;
  fontSizeVal.textContent = DEFAULT_PREFS.fontSize + 'px';
  chatArea.style.setProperty('--content-size', DEFAULT_PREFS.fontSize + 'px');
});

/* ══════════════════════════════════════
   UTILITIES
══════════════════════════════════════ */
function esc(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function nowTime() {
  return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
}

function scrollToBottom() {
  chatArea.scrollTo({ top: chatArea.scrollHeight, behavior: 'smooth' });
}

function setupMarkedRenderer() {
  if (typeof marked === 'undefined') return;
  const renderer = new marked.Renderer();
  renderer.link = function(href, title, text) {
    let url = typeof href === 'object' ? href.href : href;
    let t = typeof href === 'object' ? href.title : title;
    let label = typeof href === 'object' ? href.text : text;

    // Shorten long naked URLs in display so they never overflow
    if (label && /^https?:\/\//i.test(label)) {
      try {
        const u = new URL(label);
        const segs = u.pathname.split('/').filter(Boolean);
        const last = segs[segs.length - 1] || '';
        const cleanName = decodeURIComponent(last).replace(/\+/g, ' ').slice(0, 32);
        label = cleanName ? `${cleanName} ↗` : `${u.hostname} ↗`;
      } catch {
        label = label.slice(0, 32) + '... ↗';
      }
    }

    return `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer"${t ? ` title="${esc(t)}"` : ''}>${label}</a>`;
  };
  marked.use({ renderer });
}

function parseMarkdown(text) {
  if (typeof marked === 'undefined') return esc(text);

  // Pre-process naked Confluence URLs so they don't render as raw 100-character strings
  let processed = text.replace(/URL:\s*(https?:\/\/[^\s\)]+)/gi, (match, url) => {
    return `URL: [Open Confluence Runbook ↗](${url})`;
  });

  marked.setOptions({
    breaks: true,
    gfm: true
  });
  return marked.parse(processed);
}

/* ══════════════════════════════════════
   INITIALIZATION
══════════════════════════════════════ */
function init() {
  // Configure markdown renderer
  setupMarkedRenderer();

  // Load and apply preferences first
  const prefs = loadPrefs();

  // Load sessions
  loadSessions();

  // Restore or start active session
  const savedActive = localStorage.getItem(ACTIVE_KEY);
  if (savedActive && allSessions[savedActive]) {
    currentSessionId = savedActive;
  } else {
    // Start a fresh session
    const id = genId();
    currentSessionId = id;
    allSessions[id] = { id, title: 'New conversation', timestamp: Date.now(), messages: [] };
    localStorage.setItem(ACTIVE_KEY, id);
    saveSessions();
  }

  // Apply prefs (this also syncs panel active states)
  applyPrefs(prefs);

  // Load Confluence settings and environment status
  loadSettings(true);

  // Render history sidebar
  renderHistory();

  // Render current session
  renderCurrentSessionChat();

  // Init mobile sidebar backdrop
  initSidebarBackdrop();

  // Sidebar initial state: visible on desktop, closed on mobile
  if (isMobile()) {
    // sidebar starts hidden on mobile (CSS handles it via mobile-open class)
  } else {
    // Desktop: sidebar is visible by default (no collapsed class)
    sidebarOpenBtn.style.display = 'none';
  }

  // Focus input on load
  userInput.focus();
}

// Wait for marked to be available (it's deferred), then init
function waitForMarkedThenInit() {
  if (typeof marked !== 'undefined') {
    init();
  } else {
    // marked.js hasn't loaded yet — wait a tick
    setTimeout(waitForMarkedThenInit, 30);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', waitForMarkedThenInit);
} else {
  waitForMarkedThenInit();
}
