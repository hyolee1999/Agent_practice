/**
 * DocuAgent AI Frontend Application Logic
 */
document.addEventListener('DOMContentLoaded', () => {
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const activeDocName = document.getElementById('activeDocName');
  const activeDocSub = document.getElementById('activeDocSub');
  const docStatusBadge = document.getElementById('docStatusBadge');
  const serverStatusBadge = document.getElementById('serverStatusBadge');
  const clearChatBtn = document.getElementById('clearChatBtn');
  const streamToggle = document.getElementById('streamToggle');
  const messagesContainer = document.getElementById('messagesContainer');
  const welcomeContainer = document.getElementById('welcomeContainer');
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const toastContainer = document.getElementById('toastContainer');
  const suggestionCards = document.querySelectorAll('.suggestion-card');

  let isGenerating = false;
  let hasUploadedDoc = false;

  // ==========================================================================
  // Authentication State & DOM Handlers
  // ==========================================================================
  const authOverlay = document.getElementById('authOverlay');
  const authForm = document.getElementById('authForm');
  const authTitle = document.getElementById('authTitle');
  const authSubtitle = document.getElementById('authSubtitle');
  const tabLogin = document.getElementById('tabLogin');
  const tabRegister = document.getElementById('tabRegister');
  const authError = document.getElementById('authError');
  const nameField = document.getElementById('nameField');
  const authName = document.getElementById('authName');
  const authEmail = document.getElementById('authEmail');
  const authPassword = document.getElementById('authPassword');
  const authSubmitBtn = document.getElementById('authSubmitBtn');
  const userProfileBadge = document.getElementById('userProfileBadge');
  const userAvatar = document.getElementById('userAvatar');
  const userEmail = document.getElementById('userEmail');
  const logoutBtn = document.getElementById('logoutBtn');

  let authMode = 'login'; // 'login' | 'register'

  function getAuthToken() {
    return localStorage.getItem('access_token');
  }

  function getStoredUser() {
    try {
      return JSON.parse(localStorage.getItem('user_data') || 'null');
    } catch {
      return null;
    }
  }

  function setAuthSession(token, user) {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user_data', JSON.stringify(user));
    localStorage.setItem('session_id', 'sess_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9));
    updateAuthUI();
  }

  function clearAuthSession() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('session_id');

    if (messagesContainer) {
      messagesContainer.innerHTML = '';
      if (welcomeContainer) {
        messagesContainer.appendChild(welcomeContainer);
        welcomeContainer.style.display = 'flex';
      }
    }

    if (activeDocName) activeDocName.textContent = 'No document loaded';
    if (activeDocSub) activeDocSub.textContent = 'Upload a PDF to begin indexing';
    if (docStatusBadge) {
      docStatusBadge.textContent = 'None';
      docStatusBadge.style.color = 'var(--text-subtle)';
    }

    updateAuthUI();
  }

  function getSessionId() {
    return localStorage.getItem('session_id');
  }

  function getAuthHeaders(extraHeaders = {}) {
    const token = getAuthToken();
    const headers = { ...extraHeaders };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  function updateAuthUI() {
    const token = getAuthToken();
    const user = getStoredUser();

    if (token && user) {
      authOverlay.classList.add('hidden');
      userProfileBadge.style.display = 'flex';
      const initial = (user.name || user.email || 'U')[0].toUpperCase();
      userAvatar.textContent = initial;
      userEmail.textContent = user.name || user.email;
      userEmail.title = user.email;
    } else {
      authOverlay.classList.remove('hidden');
      userProfileBadge.style.display = 'none';
      setTimeout(() => authEmail.focus(), 150);
    }
  }

  function setAuthError(msg) {
    if (msg) {
      authError.textContent = msg;
      authError.style.display = 'block';
    } else {
      authError.textContent = '';
      authError.style.display = 'none';
    }
  }

  tabLogin.addEventListener('click', () => {
    if (authMode === 'login') return;
    authMode = 'login';
    tabLogin.classList.add('active');
    tabRegister.classList.remove('active');
    nameField.style.display = 'none';
    authName.removeAttribute('required');
    authTitle.textContent = 'Welcome to DocuAgent';
    authSubtitle.textContent = 'Sign in to query your documents with AI';
    authSubmitBtn.querySelector('span').textContent = 'Sign In';
    setAuthError(null);
  });

  tabRegister.addEventListener('click', () => {
    if (authMode === 'register') return;
    authMode = 'register';
    tabRegister.classList.add('active');
    tabLogin.classList.remove('active');
    nameField.style.display = 'flex';
    authName.setAttribute('required', 'true');
    authTitle.textContent = 'Create an Account';
    authSubtitle.textContent = 'Sign up to upload and analyze PDFs';
    authSubmitBtn.querySelector('span').textContent = 'Create Account';
    setAuthError(null);
  });

  authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    setAuthError(null);

    const email = authEmail.value.trim();
    const password = authPassword.value;
    const name = authName.value.trim();

    if (!email || !password) {
      setAuthError('Please fill in all required fields.');
      return;
    }

    authSubmitBtn.disabled = true;
    authSubmitBtn.querySelector('span').textContent = authMode === 'login' ? 'Signing In...' : 'Creating...';

    const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/register';
    const payload = authMode === 'login' ? { email, password } : { email, password, name };

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || 'Authentication failed. Please check your details.');
      }

      setAuthSession(data.access_token, data.user);
      authForm.reset();
      showToast(authMode === 'login' ? 'Welcome back!' : 'Account created successfully!', 'success');
    } catch (err) {
      setAuthError(err.message);
    } finally {
      authSubmitBtn.disabled = false;
      authSubmitBtn.querySelector('span').textContent = authMode === 'login' ? 'Sign In' : 'Create Account';
    }
  });

  logoutBtn.addEventListener('click', () => {
    clearAuthSession();
    showToast('Signed out successfully.', 'info');
  });

  // Check initial authentication state
  updateAuthUI();

  chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 160) + 'px';
    sendBtn.disabled = !chatInput.value.trim() || isGenerating;
  });

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!sendBtn.disabled) {
        chatForm.dispatchEvent(new Event('submit'));
      }
    }
  });

  suggestionCards.forEach((card) => {
    card.addEventListener('click', () => {
      const prompt = card.getAttribute('data-prompt');
      if (prompt && !isGenerating) {
        chatInput.value = prompt;
        chatInput.dispatchEvent(new Event('input'));
        chatForm.dispatchEvent(new Event('submit'));
      }
    });
  });

  dropZone.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
  });
  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
  });
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  });

  async function handleFileUpload(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      showToast('Please select a valid PDF document.', 'error');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    activeDocName.textContent = file.name;
    activeDocSub.textContent = `Indexing (${(file.size / 1024 / 1024).toFixed(2)} MB)...`;
    docStatusBadge.textContent = 'Processing...';
    docStatusBadge.style.color = 'var(--accent-cyan)';
    showToast(`Uploading and indexing "${file.name}"...`, 'info');

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData,
      });

      if (response.status === 401) {
        clearAuthSession();
        throw new Error('Session expired. Please sign in again.');
      }

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Upload failed with status ${response.status}`);
      }

      const data = await response.json();
      hasUploadedDoc = true;
      activeDocName.textContent = file.name;
      activeDocSub.textContent = data.message || 'Ready for questions';
      docStatusBadge.textContent = 'Indexed';
      docStatusBadge.style.color = 'var(--accent-emerald)';
      showToast(`Successfully indexed "${file.name}"!`, 'success');
    } catch (err) {
      console.error('Upload error:', err);
      activeDocSub.textContent = 'Upload/Index error';
      docStatusBadge.textContent = 'Failed';
      docStatusBadge.style.color = 'var(--accent-rose)';
      showToast(`Error: ${err.message}`, 'error');
    }
  }

  clearChatBtn.addEventListener('click', async () => {
    if (isGenerating) return;
    try {
      await fetch('/api/clear', { method: 'POST' }).catch(() => { });
      messagesContainer.innerHTML = '';
      messagesContainer.appendChild(welcomeContainer);
      welcomeContainer.style.display = 'flex';
      showToast('Conversation cleared', 'info');
    } catch (e) {
      console.warn('Failed to clear on server:', e);
    }
  });

  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query || isGenerating) return;

    if (welcomeContainer) {
      welcomeContainer.style.display = 'none';
    }

    chatInput.value = '';
    chatInput.style.height = 'auto';
    sendBtn.disabled = true;
    isGenerating = true;

    appendMessage(query, 'user');
    const aiBubble = appendMessage('', 'ai', true);
    const useStreaming = streamToggle.checked;

    try {
      if (useStreaming) {
        await streamResponse(query, aiBubble);
      } else {
        await fetchStandardResponse(query, aiBubble);
      }
    } catch (err) {
      console.error('Chat error:', err);
      aiBubble.querySelector('.message-bubble').textContent =
        `⚠️ Error: ${err.message || 'Could not connect to FastAPI server. Ensure the server is running on http://127.0.0.1:8000'}`;
      showToast('Request failed. Check console for details.', 'error');
    } finally {
      isGenerating = false;
      sendBtn.disabled = !chatInput.value.trim();
    }
  });

  async function streamResponse(query, aiBubble) {
    const textContainer = aiBubble.querySelector('.message-bubble');
    textContainer.innerHTML = '<span class="typing-indicator"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></span>';

    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ query, session_id: getSessionId() }),
    });

    if (response.status === 401) {
      clearAuthSession();
      throw new Error('Session expired. Please sign in again.');
    }

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server responded with ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let accumulatedText = '';
    let isFirstChunk = true;
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data:')) {
          let content = line.startsWith('data: ') ? line.slice(6) : line.slice(5);
          if (content.trim() === '[DONE]') continue;
          try {
            const parsed = JSON.parse(content);
            const text = parsed.token ?? parsed.text ?? parsed.content;
            if (typeof text === 'string') {
              accumulatedText += text;
              continue;
            }
          } catch { }
          accumulatedText += content;
        }
      }

      if (isFirstChunk && accumulatedText) {
        textContainer.innerHTML = '';
        isFirstChunk = false;
      }

      textContainer.innerHTML = renderMarkdown(accumulatedText);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Final render pass to catch any remaining buffered text
    if (accumulatedText) {
      textContainer.innerHTML = renderMarkdown(accumulatedText);
    } else {
      textContainer.textContent = 'No response generated from the model.';
    }
  }

  async function fetchStandardResponse(query, aiBubble) {
    const textContainer = aiBubble.querySelector('.message-bubble');
    textContainer.innerHTML = '<span class="typing-indicator"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></span>';

    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ query, session_id: getSessionId() }),
    });

    if (response.status === 401) {
      clearAuthSession();
      throw new Error('Session expired. Please sign in again.');
    }

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server responded with ${response.status}`);
    }

    const data = await response.json();
    const rawText = data.response || 'No response returned.';
    textContainer.innerHTML = renderMarkdown(rawText);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function appendMessage(text, sender, isPlaceholder = false) {
    const row = document.createElement('div');
    row.className = `message-row ${sender}`;
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (sender === 'user') {
      row.innerHTML = `
        <div class="message-body">
          <div class="message-bubble">${escapeHtml(text)}</div>
          <div class="message-meta"><span>${timeStr}</span></div>
        </div>
        <div class="avatar user">You</div>
      `;
    } else {
      row.innerHTML = `
        <div class="avatar ai">AI</div>
        <div class="message-body">
          <div class="message-bubble">${isPlaceholder ? text : escapeHtml(text)}</div>
          <div class="message-meta"><span>DocuAgent</span> • <span>${timeStr}</span></div>
        </div>
      `;
    }

    messagesContainer.appendChild(row);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return row;
  }

  async function checkServerHealth() {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        serverStatusBadge.innerHTML = '<span class="pulse-dot"></span> Online';
        serverStatusBadge.className = 'stat-badge';
      } else {
        throw new Error('Unhealthy');
      }
    } catch {
      serverStatusBadge.innerHTML = '<span class="pulse-dot" style="background: var(--text-subtle)"></span> Offline';
      serverStatusBadge.className = 'stat-badge idle';
    }
  }

  checkServerHealth();
  setInterval(checkServerHealth, 15000);

  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  /**
   * Convert markdown text to sanitized HTML.
   * Falls back to escaped plain text if libraries aren't loaded.
   */
  function renderMarkdown(text) {
    if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
      return DOMPurify.sanitize(marked.parse(text));
    }
    // Fallback: plain escaped text
    return escapeHtml(text);
  }
});
