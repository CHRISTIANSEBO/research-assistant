// ---------- State ----------
let messages = [];          // current conversation: {role, content}
let conversations = [];     // archived: {title, messages}
let activeIndex = null;     // index in conversations of loaded chat
let busy = false;

const STORAGE_KEY = "ra_conversations";

// ---------- Elements ----------
const landing = document.getElementById("landing");
const chat = document.getElementById("chat");
const form = document.getElementById("composerForm");
const input = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");
const newChatBtn = document.getElementById("newChat");
const historyList = document.getElementById("historyList");
const historyWrap = document.getElementById("history");
const sidebar = document.getElementById("sidebar");
const menuToggle = document.getElementById("menuToggle");

// ---------- Init ----------
loadConversations();
renderHistory();
updateSendState();

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    input.value = chip.dataset.query;
    autoGrow();
    submitQuery();
  });
});

form.addEventListener("submit", (e) => {
  e.preventDefault();
  submitQuery();
});

input.addEventListener("input", () => {
  autoGrow();
  updateSendState();
});

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    submitQuery();
  }
});

newChatBtn.addEventListener("click", () => {
  archiveCurrent();
  messages = [];
  activeIndex = null;
  renderChat();
  renderHistory();
  closeSidebarOnMobile();
});

menuToggle.addEventListener("click", () => sidebar.classList.toggle("open"));

// ---------- Core ----------
async function submitQuery() {
  const query = input.value.trim();
  if (!query || busy) return;

  messages.push({ role: "user", content: query });
  input.value = "";
  autoGrow();
  renderChat();

  busy = true;
  updateSendState();
  const typingEl = appendTyping();

  try {
    // Send prior history (everything except the message we just added).
    const history = messages.slice(0, -1);
    const res = await fetch("/api/research", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, history }),
    });
    const data = await res.json();
    typingEl.remove();

    if (!res.ok || data.error) {
      appendError(data.error || `Request failed (${res.status})`);
    } else {
      messages.push({ role: "assistant", content: data.answer, savedTo: data.saved_to });
      renderChat();
      persistActive();
    }
  } catch (err) {
    typingEl.remove();
    appendError("Network error. Please check your connection and try again.");
  } finally {
    busy = false;
    updateSendState();
  }
}

// ---------- Rendering ----------
function renderChat() {
  if (messages.length === 0) {
    landing.hidden = false;
    chat.hidden = true;
    chat.innerHTML = "";
    return;
  }
  landing.hidden = true;
  chat.hidden = false;
  chat.innerHTML = "";

  for (const m of messages) {
    const wrap = document.createElement("div");
    wrap.className = `msg ${m.role}`;
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = m.role === "assistant" ? renderMarkdown(m.content) : escapeHtml(m.content);
    wrap.appendChild(bubble);
    chat.appendChild(wrap);

    if (m.savedTo) {
      const note = document.createElement("div");
      note.className = "saved-note";
      note.textContent = `Saved to ${m.savedTo}`;
      chat.appendChild(note);
    }
  }
  scrollToBottom();
}

function appendTyping() {
  landing.hidden = true;
  chat.hidden = false;
  const wrap = document.createElement("div");
  wrap.className = "msg assistant";
  wrap.innerHTML = `<div class="bubble"><span class="typing"><span></span><span></span><span></span></span></div>`;
  chat.appendChild(wrap);
  scrollToBottom();
  return wrap;
}

function appendError(text) {
  const el = document.createElement("div");
  el.className = "error";
  el.textContent = text;
  chat.appendChild(el);
  scrollToBottom();
}

function scrollToBottom() {
  chat.scrollTop = chat.scrollHeight;
}

// ---------- History (localStorage) ----------
function archiveCurrent() {
  if (messages.length === 0) return;
  if (activeIndex !== null) {
    conversations[activeIndex].messages = [...messages];
    return;
  }
  const firstUser = messages.find((m) => m.role === "user");
  let title = firstUser ? firstUser.content : "Conversation";
  if (title.length > 45) title = title.slice(0, 45) + "...";
  conversations.unshift({ title, messages: [...messages] });
  saveConversations();
}

function persistActive() {
  // Keep the on-disk copy in sync as the active conversation grows.
  if (activeIndex === null) {
    const firstUser = messages.find((m) => m.role === "user");
    let title = firstUser ? firstUser.content : "Conversation";
    if (title.length > 45) title = title.slice(0, 45) + "...";
    conversations.unshift({ title, messages: [...messages] });
    activeIndex = 0;
  } else {
    conversations[activeIndex].messages = [...messages];
  }
  saveConversations();
  renderHistory();
}

function renderHistory() {
  historyList.innerHTML = "";
  historyWrap.classList.toggle("empty", conversations.length === 0);
  conversations.forEach((c, i) => {
    const li = document.createElement("li");
    li.textContent = c.title;
    li.title = c.title;
    if (i === activeIndex) li.classList.add("active");
    li.addEventListener("click", () => loadConversation(i));
    historyList.appendChild(li);
  });
}

function loadConversation(i) {
  // The active conversation is already persisted via persistActive(), so we can
  // switch directly to the selected one.
  activeIndex = i;
  messages = [...conversations[i].messages];
  renderChat();
  renderHistory();
  closeSidebarOnMobile();
}

function loadConversations() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    conversations = raw ? JSON.parse(raw) : [];
  } catch {
    conversations = [];
  }
}

function saveConversations() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
  } catch {
    /* storage full or unavailable — ignore */
  }
}

// ---------- Helpers ----------
function updateSendState() {
  sendBtn.disabled = busy || input.value.trim().length === 0;
}

function autoGrow() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 200) + "px";
}

function closeSidebarOnMobile() {
  sidebar.classList.remove("open");
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// Minimal, safe markdown renderer (headings, bold, italic, code, lists, links).
function renderMarkdown(md) {
  let text = escapeHtml(md);

  // Fenced code blocks
  text = text.replace(/```([\s\S]*?)```/g, (_, code) => `<pre><code>${code.trim()}</code></pre>`);
  // Inline code
  text = text.replace(/`([^`]+)`/g, "<code>$1</code>");
  // Headings
  text = text.replace(/^###\s+(.*)$/gm, "<h3>$1</h3>");
  text = text.replace(/^##\s+(.*)$/gm, "<h2>$1</h2>");
  text = text.replace(/^#\s+(.*)$/gm, "<h1>$1</h1>");
  // Bold / italic
  text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  // Links [text](url)
  text = text.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  // Bare URLs
  text = text.replace(/(^|[^"=>])(https?:\/\/[^\s<)]+)/g,
    '$1<a href="$2" target="_blank" rel="noopener noreferrer">$2</a>');

  // Lists
  const lines = text.split("\n");
  let html = "";
  let inUl = false;
  let inOl = false;
  for (let line of lines) {
    const ulMatch = /^\s*[-*]\s+(.*)$/.exec(line);
    const olMatch = /^\s*\d+\.\s+(.*)$/.exec(line);
    if (ulMatch) {
      if (!inUl) { html += "<ul>"; inUl = true; }
      if (inOl) { html += "</ol>"; inOl = false; }
      html += `<li>${ulMatch[1]}</li>`;
    } else if (olMatch) {
      if (!inOl) { html += "<ol>"; inOl = true; }
      if (inUl) { html += "</ul>"; inUl = false; }
      html += `<li>${olMatch[1]}</li>`;
    } else {
      if (inUl) { html += "</ul>"; inUl = false; }
      if (inOl) { html += "</ol>"; inOl = false; }
      if (line.trim() === "") {
        html += "";
      } else if (/^<(h\d|pre|ul|ol|li)/.test(line.trim())) {
        html += line;
      } else {
        html += `<p>${line}</p>`;
      }
    }
  }
  if (inUl) html += "</ul>";
  if (inOl) html += "</ol>";
  return html;
}
