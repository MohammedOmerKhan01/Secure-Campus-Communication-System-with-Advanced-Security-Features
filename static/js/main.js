'use strict';

// ═══════════════════════════════════════════════════════════════════════════
// PARTICLES
// ═══════════════════════════════════════════════════════════════════════════
function initParticles() {
  const c = document.createElement('div');
  c.className = 'particles';
  document.body.prepend(c);
  const colors = ['#00d4ff','#a855f7','#00ff88','#0066cc','#7c3aed'];
  const n = window.innerWidth < 600 ? 10 : 20;
  for (let i = 0; i < n; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const s = Math.random() * 5 + 2;
    Object.assign(p.style, {
      width: s+'px', height: s+'px',
      left: Math.random()*100+'%', top: Math.random()*100+'%',
      background: colors[Math.floor(Math.random()*colors.length)],
      animationDuration: (Math.random()*12+8)+'s',
      animationDelay: (Math.random()*5)+'s',
    });
    c.appendChild(p);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// RIPPLE
// ═══════════════════════════════════════════════════════════════════════════
function initRipple() {
  document.addEventListener('click', e => {
    const btn = e.target.closest('.btn,.btn-broadcast,.btn-steg');
    if (!btn || btn.disabled) return;
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const r = document.createElement('span');
    r.className = 'ripple-effect';
    Object.assign(r.style, {
      width: size+'px', height: size+'px',
      left: (e.clientX - rect.left - size/2)+'px',
      top:  (e.clientY - rect.top  - size/2)+'px',
    });
    btn.appendChild(r);
    r.addEventListener('animationend', () => r.remove());
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// COUNTER ANIMATION
// ═══════════════════════════════════════════════════════════════════════════
function animateCounters() {
  document.querySelectorAll('.stat-num').forEach(el => {
    const target = parseInt(el.textContent, 10);
    if (isNaN(target) || target === 0) return;
    let cur = 0;
    const step = Math.ceil(target / 30);
    const t = setInterval(() => {
      cur = Math.min(cur + step, target);
      el.textContent = cur;
      if (cur >= target) clearInterval(t);
    }, 40);
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SCROLL ANIMATIONS
// ═══════════════════════════════════════════════════════════════════════════
function initScrollAnimations() {
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.card,.stat-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity .5s ease, transform .5s ease';
    obs.observe(el);
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// PASSWORD STRENGTH METER
// ═══════════════════════════════════════════════════════════════════════════
function initPasswordStrength() {
  const input = document.getElementById('regPassword');
  if (!input) return;

  const fill  = document.getElementById('strengthFill');
  const label = document.getElementById('strengthLabel');
  const rules = {
    len:     { el: document.getElementById('rule-len'),     test: p => p.length >= 8 },
    upper:   { el: document.getElementById('rule-upper'),   test: p => /[A-Z]/.test(p) },
    lower:   { el: document.getElementById('rule-lower'),   test: p => /[a-z]/.test(p) },
    num:     { el: document.getElementById('rule-num'),     test: p => /\d/.test(p) },
    special: { el: document.getElementById('rule-special'), test: p => /[!@#$%^&*(),.?":{}|<>_\-]/.test(p) },
  };

  input.addEventListener('input', () => {
    const pw = input.value;
    let score = 0;

    Object.values(rules).forEach(r => {
      const pass = r.test(pw);
      if (r.el) r.el.classList.toggle('pass', pass);
      if (pass) score++;
    });

    const wrap = input.closest('.form-group');
    wrap.classList.remove('strength-weak','strength-medium','strength-strong');

    if (pw.length === 0) {
      if (fill)  fill.style.width = '0';
      if (label) label.textContent = '';
      return;
    }

    if (score <= 2) {
      wrap.classList.add('strength-weak');
      if (label) label.textContent = '🔴 Weak';
    } else if (score <= 4) {
      wrap.classList.add('strength-medium');
      if (label) label.textContent = '🟡 Medium';
    } else {
      wrap.classList.add('strength-strong');
      if (label) label.textContent = '🟢 Strong';
    }
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════════════════
function setLoading(btn, on) {
  if (!btn) return;
  btn.classList.toggle('loading', on);
  btn.disabled = on;
}

function showStatus(el, msg, ok) {
  if (!el) return;
  el.textContent = msg;
  el.className = 'status-msg ' + (ok ? 'status-ok' : 'status-err');
  setTimeout(() => { if (el.textContent === msg) el.textContent = ''; }, 4500);
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

function makeCounter(inputId, counterId, max) {
  const inp = document.getElementById(inputId);
  const cnt = document.getElementById(counterId);
  if (!inp || !cnt) return;
  inp.addEventListener('input', () => {
    const l = inp.value.length;
    cnt.textContent = `${l} / ${max}`;
    cnt.style.color = l > max * .9 ? 'var(--danger)' : l > max * .75 ? 'var(--warning)' : 'var(--muted)';
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// MESSAGING
// ═══════════════════════════════════════════════════════════════════════════
async function sendMessage() {
  const receiver = document.getElementById('receiverSelect')?.value;
  const message  = document.getElementById('messageInput')?.value.trim();
  const status   = document.getElementById('sendStatus');
  const btn      = document.getElementById('sendBtn');

  if (!receiver) { showStatus(status, '⚠️ Select a recipient.', false); return; }
  if (!message)  { showStatus(status, '⚠️ Message cannot be empty.', false); return; }

  setLoading(btn, true);
  try {
    const res  = await fetch('/send-message', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({receiver,message}) });
    const data = await res.json();
    if (res.ok) {
      showStatus(status, '✅ Message sent!', true);
      document.getElementById('messageInput').value = '';
      document.getElementById('charCount').textContent = '0 / 2000';
      await loadMessages();
    } else {
      showStatus(status, `⚠️ ${data.error}`, false);
    }
  } catch { showStatus(status, '⚠️ Network error.', false); }
  finally  { setLoading(btn, false); }
}

async function loadMessages() {
  const withUser = document.getElementById('filterUser')?.value.trim() || '';
  const list     = document.getElementById('messageList');
  if (!list) return;

  const typing = document.createElement('div');
  typing.id = 'typingInd';
  typing.className = 'message-item';
  typing.style.cssText = 'opacity:.5;font-size:.82rem;color:var(--muted)';
  typing.innerHTML = '<span class="typing-dots">Loading<span>.</span><span>.</span><span>.</span></span>';
  list.prepend(typing);

  const url = withUser ? `/get-messages?with=${encodeURIComponent(withUser)}` : '/get-messages';
  try {
    const res  = await fetch(url);
    const data = await res.json();
    document.getElementById('typingInd')?.remove();
    if (!res.ok) { list.innerHTML = `<p class="empty-state">${escapeHtml(data.error)}</p>`; return; }
    if (!data.messages.length) { list.innerHTML = '<p class="empty-state">No messages yet.</p>'; return; }
    list.innerHTML = data.messages.map((m,i) => renderMessage(m,i)).join('');
  } catch {
    document.getElementById('typingInd')?.remove();
    list.innerHTML = '<p class="empty-state">Network error.</p>';
  }
}

function renderMessage(msg, i=0) {
  const me   = document.querySelector('meta[name="current-user"]')?.content || '';
  const sent = msg.sender === me;
  const tag  = c => `<span class="campus-tag campus-${escapeHtml(c)}">${escapeHtml(c)}</span>`;
  const from = sent
    ? `You → ${escapeHtml(msg.receiver)} ${tag(msg.receiver_campus)}`
    : `${escapeHtml(msg.sender)} ${tag(msg.sender_campus)} → You`;
  return `<div class="message-item ${sent?'sent':'received'}" style="animation-delay:${Math.min(i*.05,.5)}s">
    <div class="msg-meta"><span class="msg-from">${from}</span><span class="msg-time">${escapeHtml(msg.timestamp)}</span></div>
    <p class="msg-content">${escapeHtml(msg.content)}</p>
  </div>`;
}

// ═══════════════════════════════════════════════════════════════════════════
// ADMIN MESSAGING
// ═══════════════════════════════════════════════════════════════════════════
async function adminSendMessage() {
  const receiver = document.getElementById('adminReceiverSelect')?.value;
  const message  = document.getElementById('adminMessageInput')?.value.trim();
  const status   = document.getElementById('adminSendStatus');
  const btn      = document.getElementById('adminSendBtn');
  if (!receiver) { showStatus(status, '⚠️ Select a recipient.', false); return; }
  if (!message)  { showStatus(status, '⚠️ Message cannot be empty.', false); return; }
  setLoading(btn, true);
  try {
    const res  = await fetch('/send-message', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({receiver,message}) });
    const data = await res.json();
    if (res.ok) {
      showStatus(status, '✅ Message sent!', true);
      document.getElementById('adminMessageInput').value = '';
      setTimeout(() => location.reload(), 1200);
    } else { showStatus(status, `⚠️ ${data.error}`, false); }
  } catch { showStatus(status, '⚠️ Network error.', false); }
  finally  { setLoading(btn, false); }
}

async function sendBroadcast() {
  const target  = document.getElementById('broadcastTarget')?.value;
  const message = document.getElementById('broadcastMessageInput')?.value.trim();
  const status  = document.getElementById('broadcastStatus');
  const btn     = document.getElementById('broadcastBtn');
  if (!message) { showStatus(status, '⚠️ Message cannot be empty.', false); return; }
  setLoading(btn, true);
  try {
    const res  = await fetch('/admin/broadcast', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({target,message}) });
    const data = await res.json();
    if (res.ok) {
      showStatus(status, `✅ ${data.message}`, true);
      document.getElementById('broadcastMessageInput').value = '';
      setTimeout(() => location.reload(), 1400);
    } else { showStatus(status, `⚠️ ${data.error}`, false); }
  } catch { showStatus(status, '⚠️ Network error.', false); }
  finally  { setLoading(btn, false); }
}

// ═══════════════════════════════════════════════════════════════════════════
// STEGANOGRAPHY
// ═══════════════════════════════════════════════════════════════════════════
function initDropZone(dropId, inputId, fileNameId, previewId, previewImgId) {
  const drop    = document.getElementById(dropId);
  const input   = document.getElementById(inputId);
  const fname   = document.getElementById(fileNameId);
  const preview = document.getElementById(previewId);
  const prevImg = document.getElementById(previewImgId);
  if (!drop || !input) return;

  input.addEventListener('change', () => handleFile(input.files[0]));
  drop.addEventListener('dragover',  e => { e.preventDefault(); drop.classList.add('dragover'); });
  drop.addEventListener('dragleave', () => drop.classList.remove('dragover'));
  drop.addEventListener('drop', e => {
    e.preventDefault(); drop.classList.remove('dragover');
    if (e.dataTransfer.files[0]) { input.files = e.dataTransfer.files; handleFile(e.dataTransfer.files[0]); }
  });

  function handleFile(file) {
    if (!file) return;
    if (fname) fname.textContent = file.name;
    if (preview && prevImg) {
      const reader = new FileReader();
      reader.onload = e => { prevImg.src = e.target.result; preview.style.display = 'block'; };
      reader.readAsDataURL(file);
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// STEGANOGRAPHY — SEND TO USER
// ═══════════════════════════════════════════════════════════════════════════
async function sendStegImage() {
  const image    = document.getElementById('hideImageInput');
  const message  = document.getElementById('hideMessage')?.value.trim();
  const receiver = document.getElementById('stegReceiver')?.value;
  const caption  = document.getElementById('stegCaption')?.value.trim() || '';
  const status   = document.getElementById('stegSendStatus');
  const btn      = document.getElementById('stegSendBtn');

  if (!image?.files[0]) { showStatus(status, '⚠️ Please upload an image.', false); return; }
  if (!message)          { showStatus(status, '⚠️ Enter a secret message.', false); return; }
  if (!receiver)         { showStatus(status, '⚠️ Select a recipient.', false); return; }

  setLoading(btn, true);
  const fd = new FormData();
  fd.append('image',    image.files[0]);
  fd.append('message',  message);
  fd.append('receiver', receiver);
  fd.append('caption',  caption);

  try {
    const res  = await fetch('/steg-send', { method: 'POST', body: fd });
    const data = await res.json();
    if (res.ok) {
      showStatus(status, `✅ ${data.message}`, true);
      document.getElementById('hideMessage').value  = '';
      document.getElementById('stegCaption').value  = '';
      document.getElementById('stegReceiver').value = '';
      document.getElementById('hideFileName').textContent = '';
      document.getElementById('hidePreview').style.display = 'none';
    } else {
      showStatus(status, `⚠️ ${data.error}`, false);
    }
  } catch { showStatus(status, '⚠️ Network error.', false); }
  finally  { setLoading(btn, false); }
}

// ── Hide locally (download only) ──────────────────────────────────────────────
async function hideLocalOnly() {
  const input   = document.getElementById('hideImageInput');
  const message = document.getElementById('hideMessage')?.value.trim();
  const btn     = document.getElementById('hideBtn');
  const result  = document.getElementById('hideResult');
  const text    = document.getElementById('hideResultText');
  const dlBtn   = document.getElementById('hideDownloadBtn');

  if (!input?.files[0]) { showStegResult(result, text, '⚠️ Please upload an image.', true); return; }
  if (!message)          { showStegResult(result, text, '⚠️ Enter a secret message.', true); return; }

  setLoading(btn, true);
  const fd = new FormData();
  fd.append('image',   input.files[0]);
  fd.append('message', message);

  try {
    const res  = await fetch('/steg-hide', { method: 'POST', body: fd });
    const data = await res.json();
    if (res.ok) {
      showStegResult(result, text, `✅ ${data.message}`, false);
      if (dlBtn) { dlBtn.href = data.download_url; dlBtn.style.display = 'inline-flex'; }
    } else {
      showStegResult(result, text, `⚠️ ${data.error}`, true);
      if (dlBtn) dlBtn.style.display = 'none';
    }
  } catch { showStegResult(result, text, '⚠️ Network error.', true); }
  finally  { setLoading(btn, false); }
}

// ── Extract from inbox item (by filename via server) ─────────────────────────
async function extractFromInbox(msgId, filename) {
  const result = document.getElementById(`inbox-result-${msgId}`);
  const text   = document.getElementById(`inbox-text-${msgId}`);
  if (!result || !text) return;

  // Download the file as blob, then POST it to /steg-extract
  try {
    const dlRes  = await fetch(`/download/${encodeURIComponent(filename)}`);
    if (!dlRes.ok) { showStegResult(result, text, '⚠️ Could not fetch image.', true); return; }
    const blob   = await dlRes.blob();
    const file   = new File([blob], filename, { type: 'image/png' });
    const fd     = new FormData();
    fd.append('image', file);

    const res  = await fetch('/steg-extract', { method: 'POST', body: fd });
    const data = await res.json();
    if (res.ok) {
      showStegResult(result, text, data.hidden_message || '(No hidden message found)', false);
      markRead(msgId);
    } else {
      showStegResult(result, text, `⚠️ ${data.error}`, true);
    }
  } catch { showStegResult(result, text, '⚠️ Network error.', true); }
}

// ── Mark inbox item as read ───────────────────────────────────────────────────
async function markRead(msgId) {
  await fetch(`/steg-mark-read/${msgId}`, { method: 'POST' }).catch(() => {});
  const item = document.getElementById(`steg-item-${msgId}`);
  if (item) {
    item.classList.remove('unread');
    item.querySelector('.unread-dot')?.remove();
  }
}

async function hideMessage() {
  const input   = document.getElementById('hideImageInput');
  const message = document.getElementById('hideMessage')?.value.trim();
  const btn     = document.getElementById('hideBtn');
  const result  = document.getElementById('hideResult');
  const text    = document.getElementById('hideResultText');
  const dlBtn   = document.getElementById('hideDownloadBtn');

  if (!input?.files[0]) { showStegResult(result, text, '⚠️ Please upload an image.', true); return; }
  if (!message)          { showStegResult(result, text, '⚠️ Please enter a secret message.', true); return; }

  setLoading(btn, true);
  const fd = new FormData();
  fd.append('image', input.files[0]);
  fd.append('message', message);

  try {
    const res  = await fetch('/steg-hide', { method:'POST', body:fd });
    const data = await res.json();
    if (res.ok) {
      showStegResult(result, text, `✅ ${data.message}`, false);
      if (dlBtn) { dlBtn.href = data.download_url; dlBtn.style.display = 'inline-flex'; }
    } else {
      showStegResult(result, text, `⚠️ ${data.error}`, true);
      if (dlBtn) dlBtn.style.display = 'none';
    }
  } catch { showStegResult(result, text, '⚠️ Network error.', true); }
  finally  { setLoading(btn, false); }
}

async function extractMessage() {
  const input  = document.getElementById('extractImageInput');
  const btn    = document.getElementById('extractBtn');
  const result = document.getElementById('extractResult');
  const text   = document.getElementById('extractResultText');

  if (!input?.files[0]) { showStegResult(result, text, '⚠️ Please upload an image.', true); return; }

  setLoading(btn, true);
  const fd = new FormData();
  fd.append('image', input.files[0]);

  try {
    const res  = await fetch('/steg-extract', { method:'POST', body:fd });
    const data = await res.json();
    if (res.ok) {
      showStegResult(result, text, data.hidden_message || '(No hidden message found)', false);
    } else {
      showStegResult(result, text, `⚠️ ${data.error}`, true);
    }
  } catch { showStegResult(result, text, '⚠️ Network error.', true); }
  finally  { setLoading(btn, false); }
}

function showStegResult(box, textEl, msg, isError) {
  if (!box || !textEl) return;
  box.classList.add('show');
  textEl.textContent = msg;
  textEl.className = 'result-text' + (isError ? ' result-error' : '');
}

// ═══════════════════════════════════════════════════════════════════════════
// BROADCAST PREVIEW
// ═══════════════════════════════════════════════════════════════════════════
function initBroadcastPreview() {
  const sel     = document.getElementById('broadcastTarget');
  const preview = document.getElementById('broadcastPreview');
  if (!sel || !preview) return;
  const counts = { ALL: 0, A: 0, B: 0 };
  fetch('/admin/users').then(r => r.json()).then(d => {
    counts.A   = d.users.filter(u => u.campus === 'A').length;
    counts.B   = d.users.filter(u => u.campus === 'B').length;
    counts.ALL = d.users.length;
    update();
  }).catch(() => {});
  function update() { preview.innerHTML = `Will reach <strong>${counts[sel.value] ?? 0}</strong> user(s)`; }
  sel.addEventListener('change', update);
}

// ═══════════════════════════════════════════════════════════════════════════
// AUTO-DISMISS ALERTS
// ═══════════════════════════════════════════════════════════════════════════
function initAlerts() {
  document.querySelectorAll('.alert').forEach((a, i) => {
    setTimeout(() => {
      a.style.transition = 'opacity .5s ease, transform .5s ease, max-height .5s ease, padding .5s ease, margin .5s ease';
      a.style.opacity = '0'; a.style.transform = 'translateX(30px)';
      a.style.maxHeight = '0'; a.style.padding = '0'; a.style.margin = '0';
      setTimeout(() => a.remove(), 500);
    }, 3500 + i * 300);
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// FORM SUBMIT SPINNER
// ═══════════════════════════════════════════════════════════════════════════
document.querySelectorAll('form').forEach(f => {
  f.addEventListener('submit', () => {
    const btn = f.querySelector('.btn');
    if (btn) setLoading(btn, true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// AUTO-REFRESH MESSAGES
// ═══════════════════════════════════════════════════════════════════════════
if (document.getElementById('messageList')) {
  setInterval(loadMessages, 15000);
}

// ═══════════════════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  initParticles();
  initRipple();
  initScrollAnimations();
  animateCounters();
  initPasswordStrength();
  initAlerts();
  initBroadcastPreview();
  makeCounter('messageInput',          'charCount',          2000);
  makeCounter('adminMessageInput',     'adminCharCount',     2000);
  makeCounter('broadcastMessageInput', 'broadcastCharCount', 2000);
  makeCounter('hideMessage',           'hideCharCount',       500);
  initDropZone('hideDropZone',    'hideImageInput',    'hideFileName',    'hidePreview',    'hidePreviewImg');
  initDropZone('extractDropZone', 'extractImageInput', 'extractFileName', 'extractPreview', 'extractPreviewImg');
});
