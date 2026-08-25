/**
 * DocuAgent AI Frontend Application Logic
 * Interacts with FastAPI backend endpoints:
 *  - POST /api/upload (PDF file upload and ingestion)
 *  - POST /api/chat (Standard JSON Q&A)
 *  - POST /api/chat/stream (SSE streaming Q&A)
 *  - POST /api/clear (Reset chat memory)
 *  - GET  /api/health (Server health check)
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
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

  // Auto-resize textarea
  chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 160) + 'px';
    sendBtn.disabled = !chatInput.value.trim() || isGenerating;
  });

  // Handle Enter vs Shift+Enter
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!sendBtn.disabled) {
        chatForm.dispatchEvent(new Event('submit'));
      }
    }
  });

  // Quick suggestion click handler
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

  // File Upload Handlers (Click & Drag-Drop)
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

  // Upload PDF to FastAPI backend
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
        body: formData,
      });

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

  // Clear Chat Conversation
  clearChatBtn.addEventListener('click', async () => {
    if (isGenerating) return;
    try {
      await fetch('/api/clear', { method: 'POST' }).catch(() => {});
      messagesContainer.innerHTML = '';
      messagesContainer.appendChild(welcomeContainer);
      welcomeContainer.style.display = 'flex';
      showToast('Conversation cleared', 'info');
    } catch (e) {
      console.warn('Failed to clear on server:', e);
    }
  });

  // Main Chat Submission Handler
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query || isGenerating) return;

    // Hide welcome banner if visible
    if (welcomeContainer) {
      welcomeContainer.style.display = 'none';
    }

    // Reset input
    chatInput.value = '';
    chatInput.style.height = 'auto';
    sendBtn.disabled = true;
    isGenerating = true;

    // Append User Message
    appendMessage(query, 'user');

    // Create AI Placeholder Bubble
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

  // SSE Streaming via fetch + ReadableStream
  async function streamResponse(query, aiBubble) {
    const textContainer = aiBubble.querySelector('.message-bubble');
    textContainer.innerHTML = '<span class="typing-indicator"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></span>';

    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server responded with ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let accumulatedText = '';
    let isFirstChunk = true;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      // SSE format may be raw text or 'data: ...'
      const lines = chunk.split('\n');
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const content = line.replace(/^data:\s*/, '');
          if (content === '[DONE]') continue;
          accumulatedText += content;
        } else if (line.trim()) {
          accumulatedText += line;
        }
      }

      if (isFirstChunk && accumulatedText) {
        textContainer.innerHTML = '';
        isFirstChunk = false;
      }

      textContainer.textContent = accumulatedText;
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    if (!accumulatedText) {
      textContainer.textContent = 'No response generated from the model.';
    }
  }

  // Standard Non-Streaming JSON Response
  async function fetchStandardResponse(query, aiBubble) {
    const textContainer = aiBubble.querySelector('.message-bubble');
    textContainer.innerHTML = '<span class="typing-indicator"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></span>';

    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server responded with ${response.status}`);
    }

    const data = await response.json();
    textContainer.textContent = data.response || 'No response returned.';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Append a message row to chat
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

  // Health check on boot
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

  // Toast Notification Helper
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
});
