class ChatBot {
  constructor() {
    this.chatWindow = document.getElementById("chat-window");
    this.form = document.getElementById("chat-form");
    this.input = document.getElementById("user-input");
    this.sendBtn = document.getElementById("send-btn");
    this.historyList = document.getElementById("history-list");
    this.newChatBtn = document.getElementById("new-chat-btn");
    this.typingIndicator = document.getElementById("typing-indicator");
    
    this.session_id = localStorage.getItem("session_id") || null;
    this.currentSessionElement = null;
    
    this.init();
  }

  init() {
    this.form.addEventListener('submit', this.handleSubmit.bind(this));
    this.newChatBtn.addEventListener('click', this.startNewChat.bind(this));
    this.input.addEventListener('input', this.handleInputChange.bind(this));
    this.input.addEventListener('keydown', this.handleKeyDown.bind(this));
    
    // Load existing session on startup
    if (this.session_id) {
      this.loadExistingSession();
    }
    
    // Load chat history from localStorage
    this.loadChatHistory();
    
    // Focus input on load
    this.input.focus();
  }

  async handleSubmit(e) {
    e.preventDefault();
    const message = this.input.value.trim();
    if (!message || this.sendBtn.disabled) return;

    // Clear welcome message if it exists
    this.clearWelcomeMessage();

    // Add user message
    this.addMessage("user", message);
    this.input.value = "";
    this.toggleSendButton(false);
    this.showTypingIndicator();

    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message, 
          session_id: this.session_id 
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Update session ID
      this.session_id = data.session_id;
      localStorage.setItem("session_id", this.session_id);
      
      // Save to history and add bot response
      this.saveToHistory(this.session_id, message);
      this.addMessage("bot", data.reply);
      
    } catch (error) {
      console.error("Error:", error);
      this.addMessage("bot", "Sorry, I encountered an error. Please try again.");
    } finally {
      this.hideTypingIndicator();
      this.toggleSendButton(true);
      this.input.focus();
    }
  }

  addMessage(role, text) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `chat-msg ${role}`;
    
    // Format text for better display
    messageDiv.innerHTML = this.formatMessage(text);
    
    this.chatWindow.appendChild(messageDiv);
    this.scrollToBottom();
    
    // Add animation
    messageDiv.style.opacity = "0";
    messageDiv.style.transform = "translateY(20px)";
    
    requestAnimationFrame(() => {
      messageDiv.style.transition = "all 0.3s ease";
      messageDiv.style.opacity = "1";
      messageDiv.style.transform = "translateY(0)";
    });
  }

  formatMessage(text) {
    // Basic formatting for better readability
    return text
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>');
  }

  clearWelcomeMessage() {
    const welcomeMsg = this.chatWindow.querySelector('.welcome-message');
    if (welcomeMsg) {
      welcomeMsg.style.opacity = "0";
      setTimeout(() => welcomeMsg.remove(), 300);
    }
  }

  showTypingIndicator() {
    this.typingIndicator.style.display = "flex";
  }

  hideTypingIndicator() {
    this.typingIndicator.style.display = "none";
  }

  toggleSendButton(enabled) {
    this.sendBtn.disabled = !enabled;
    this.sendBtn.style.opacity = enabled ? "1" : "0.5";
  }

  scrollToBottom() {
    this.chatWindow.scrollTop = this.chatWindow.scrollHeight;
  }

  saveToHistory(sessionId, firstMessage) {
    // Check if session already exists
    const existingSession = Array.from(this.historyList.children)
      .find(li => li.dataset.id === sessionId);
    
    if (!existingSession) {
      const li = document.createElement("li");
      li.innerHTML = `
        <div class="session-info">
          <div class="session-title">${this.truncateText(firstMessage, 30)}</div>
          <div class="session-time">${this.formatTime(new Date())}</div>
        </div>
      `;
      li.dataset.id = sessionId;
      li.addEventListener('click', () => this.loadHistory(sessionId, li));
      
      // Insert at the beginning
      this.historyList.insertBefore(li, this.historyList.firstChild);
      
      // Update current session
      this.setActiveSession(li);
      
      // Save to localStorage
      this.saveChatHistory();
    }
  }

  async loadHistory(sessionId, sessionElement) {
    try {
      this.clearWelcomeMessage();
      this.chatWindow.innerHTML = "";
      
      const response = await fetch(`/history/${sessionId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const history = await response.json();
      history.forEach(chat => this.addMessage(chat.role, chat.content));
      
      // Update current session
      this.session_id = sessionId;
      localStorage.setItem("session_id", sessionId);
      this.setActiveSession(sessionElement);
      
    } catch (error) {
      console.error("Error loading history:", error);
      this.addMessage("bot", "Sorry, I couldn't load the chat history.");
    }
  }

  setActiveSession(sessionElement) {
    // Remove active class from all sessions
    Array.from(this.historyList.children).forEach(li => {
      li.classList.remove('active');
    });
    
    // Add active class to current session
    if (sessionElement) {
      sessionElement.classList.add('active');
      this.currentSessionElement = sessionElement;
    }
  }

  startNewChat() {
    this.session_id = null;
    localStorage.removeItem("session_id");
    this.chatWindow.innerHTML = `
      <div class="welcome-message">
        <div class="welcome-icon">
          <i class="fas fa-comments"></i>
        </div>
        <h2>How can I help you today?</h2>
        <p>Ask me anything about script generation, content creation, or YouTube strategies!</p>
      </div>
    `;
    
    // Remove active session
    if (this.currentSessionElement) {
      this.currentSessionElement.classList.remove('active');
      this.currentSessionElement = null;
    }
    
    this.input.focus();
  }

  loadExistingSession() {
    if (this.session_id) {
      // Find existing session in history
      const sessionElement = Array.from(this.historyList.children)
        .find(li => li.dataset.id === this.session_id);
      
      if (sessionElement) {
        this.loadHistory(this.session_id, sessionElement);
      }
    }
  }

  handleInputChange() {
    const hasText = this.input.value.trim().length > 0;
    this.toggleSendButton(hasText);
  }

  handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.form.dispatchEvent(new Event('submit'));
    }
  }

  truncateText(text, maxLength) {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  }

  formatTime(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  saveChatHistory() {
    const sessions = Array.from(this.historyList.children).map(li => ({
      id: li.dataset.id,
      title: li.querySelector('.session-title')?.textContent || 'New Chat',
      time: li.querySelector('.session-time')?.textContent || this.formatTime(new Date())
    }));
    
    localStorage.setItem('chat_history', JSON.stringify(sessions));
  }

  loadChatHistory() {
    const savedHistory = localStorage.getItem('chat_history');
    if (savedHistory) {
      try {
        const sessions = JSON.parse(savedHistory);
        sessions.forEach(session => {
          const li = document.createElement("li");
          li.innerHTML = `
            <div class="session-info">
              <div class="session-title">${session.title}</div>
              <div class="session-time">${session.time}</div>
            </div>
          `;
          li.dataset.id = session.id;
          li.addEventListener('click', () => this.loadHistory(session.id, li));
          this.historyList.appendChild(li);
        });
      } catch (error) {
        console.error("Error loading chat history:", error);
      }
    }
  }
}

// Initialize the chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new ChatBot();
});

// Add some utility functions for enhanced UX
document.addEventListener('keydown', (e) => {
  // ESC key to start new chat
  if (e.key === 'Escape') {
    document.getElementById('new-chat-btn').click();
  }
});

// Add mobile responsiveness
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('open');
}

// Add sidebar toggle for mobile (you can add a hamburger menu button)
if (window.innerWidth <= 600) {
  const header = document.querySelector('header .header-content');
  const toggleBtn = document.createElement('button');
  toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
  toggleBtn.className = 'sidebar-toggle';
  toggleBtn.onclick = toggleSidebar;
  header.insertBefore(toggleBtn, header.firstChild);
}
