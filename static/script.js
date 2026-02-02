// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const welcomeMessage = document.getElementById('welcomeMessage');
const charCount = document.getElementById('charCount');
const chatContainer = document.querySelector('.chat-container');

// Auto-resize textarea
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
    
    // Update character count
    charCount.textContent = this.value.length;
    
    // Enable/disable send button
    sendButton.disabled = this.value.trim().length === 0;
});

// Send message on Enter (but allow Shift+Enter for new line)
messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send message function
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Hide welcome message if visible
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }
    
    // Add user message to chat
    addUserMessage(message);
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    charCount.textContent = '0';
    sendButton.disabled = true;
    
    // Show typing indicator
    const typingId = showTypingIndicator();
    
    try {
        // Send message to API
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: message })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get response');
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        // Add bot response
        addBotMessage(data.answer, data.category);
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator(typingId);
        addBotMessage(
            "I apologize, but I'm having trouble connecting to the server. Please check if the server is running and try again.",
            'error'
        );
    }
}

// Send suggested question
function sendSuggestion(question) {
    messageInput.value = question;
    messageInput.dispatchEvent(new Event('input'));
    sendMessage();
}

// Add user message to chat
function addUserMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="message-bubble">${escapeHtml(message)}</div>
            <div class="message-meta">
                <span>${getCurrentTime()}</span>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    // Ensure scroll happens after DOM update
    setTimeout(() => scrollToBottom(), 0);
}

// Add bot message to chat
function addBotMessage(message, category) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    
    const categoryIcon = getCategoryIcon(category);
    const categoryLabel = getCategoryLabel(category);
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="message-bubble">${formatMessage(message)}</div>
            <div class="message-meta">
                <span>${getCurrentTime()}</span>
                ${category && category !== 'error' ? `
                    <span class="message-category">
                        ${categoryIcon}
                        ${categoryLabel}
                    </span>
                ` : ''}
            </div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    // Ensure scroll happens after DOM update
    setTimeout(() => scrollToBottom(), 0);
}

// Show typing indicator
function showTypingIndicator() {
    const typingId = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = typingId;
    typingDiv.className = 'message bot-message';
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="message-bubble">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    // Ensure scroll happens after DOM update
    setTimeout(() => scrollToBottom(), 0);
    return typingId;
}

// Remove typing indicator
function removeTypingIndicator(typingId) {
    const typingDiv = document.getElementById(typingId);
    if (typingDiv) {
        typingDiv.remove();
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatMessage(text) {
    // Escape HTML
    text = escapeHtml(text);
    
    // Convert line breaks to <br>
    text = text.replace(/\n/g, '<br>');
    
    // Convert **bold** to <strong>
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert URLs to links
    text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    
    return text;
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

function getCategoryIcon(category) {
    const icons = {
        'products': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="14" height="14"><rect x="3" y="3" width="7" height="7" stroke="currentColor" stroke-width="2"/><rect x="14" y="3" width="7" height="7" stroke="currentColor" stroke-width="2"/><rect x="3" y="14" width="7" height="7" stroke="currentColor" stroke-width="2"/><rect x="14" y="14" width="7" height="7" stroke="currentColor" stroke-width="2"/></svg>',
        'returns': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="14" height="14"><path d="M3 12L9 6M3 12L9 18M3 12H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        'general': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="14" height="14"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><path d="M12 16V12M12 8H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
        'unknown': '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="14" height="14"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><path d="M9.09 9C9.325 8.33 9.785 7.768 10.394 7.409C11.003 7.05 11.723 6.918 12.426 7.038C13.129 7.158 13.768 7.522 14.229 8.066C14.69 8.61 14.944 9.298 14.944 10.009C14.944 12.009 11.944 13.009 11.944 13.009M12 17H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
    };
    return icons[category] || icons['unknown'];
}

function getCategoryLabel(category) {
    const labels = {
        'products': 'Products',
        'returns': 'Returns',
        'general': 'General',
        'unknown': 'Escalated'
    };
    return labels[category] || 'Support';
}

function scrollToBottom() {
    // Scroll the chat container (which has overflow-y: auto)
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // Use setTimeout with multiple delays to handle any async rendering
        setTimeout(() => {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 10);
        
        setTimeout(() => {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 50);
        
        setTimeout(() => {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 100);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    messageInput.focus();
    sendButton.disabled = true;
});
