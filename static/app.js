const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');

const CHAT_STORAGE_KEY = 'sprint_analytics_chat_history';

// Configure marked.js for markdown rendering
marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: false,
    mangle: false
});

// Load chat history on page load
document.addEventListener('DOMContentLoaded', () => {
    loadChatHistory();
});

// Handle Enter key
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function sendSuggestion(message) {
    messageInput.value = message;
    sendMessage();
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Clear input
    messageInput.value = '';
    
    // Remove welcome message if exists
    const welcomeMsg = chatContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    // Add user message
    addMessage(message, 'user');
    saveChatHistory();

    // Show typing indicator
    const typingId = showTyping();

    // Disable input
    sendButton.disabled = true;
    messageInput.disabled = true;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // Remove typing indicator
        removeTyping(typingId);

        // Add bot response with markdown rendering
        addMessage(data.response, 'bot', true);

        // Add charts if any
        if (data.charts && data.charts.length > 0) {
            data.charts.forEach((chart, index) => {
                addChart(chart, `chart-${Date.now()}-${index}`);
            });
        }

        // Save chat history
        saveChatHistory();
    } catch (error) {
        removeTyping(typingId);
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        console.error('Error:', error);
    } finally {
        // Re-enable input
        sendButton.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
}

function addMessage(text, sender, isMarkdown = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isMarkdown && sender === 'bot') {
        // Render markdown to HTML
        contentDiv.innerHTML = marked.parse(text);
    } else {
        contentDiv.textContent = text;
    }
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typing-indicator';
    
    const typingContent = document.createElement('div');
    typingContent.className = 'typing-indicator';
    typingContent.innerHTML = '<span></span><span></span><span></span>';
    
    typingDiv.appendChild(typingContent);
    chatContainer.appendChild(typingDiv);
    
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return 'typing-indicator';
}

function removeTyping(id) {
    const typingElement = document.getElementById(id);
    if (typingElement) {
        typingElement.remove();
    }
}

function addChart(chartData, id) {
    const chartDiv = document.createElement('div');
    chartDiv.className = 'chart-container';
    chartDiv.id = id;
    
    chatContainer.appendChild(chartDiv);
    
    // Render Plotly chart
    Plotly.newPlot(id, chartData.data, chartData.layout, {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    });
    
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Clear chat function
function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        // Clear localStorage
        localStorage.removeItem(CHAT_STORAGE_KEY);
        
        // Clear chat container
        chatContainer.innerHTML = `
            <div class="welcome-message">
                <h2>👋 Welcome to Sprint Analytics Chatbot!</h2>
                <p>Ask me anything about your sprint data, team performance, or request visualizations.</p>
                <div class="suggestions">
                    <div class="suggestion-chip" onclick="sendSuggestion('Show me overall sprint summary')">
                        📊 Sprint Summary
                    </div>
                    <div class="suggestion-chip" onclick="sendSuggestion('How is the team performing?')">
                        👥 Team Performance
                    </div>
                    <div class="suggestion-chip" onclick="sendSuggestion('Show me bug analysis')">
                        🐛 Bug Analysis
                    </div>
                    <div class="suggestion-chip" onclick="sendSuggestion('Create a velocity chart')">
                        📈 Velocity Chart
                    </div>
                </div>
            </div>
        `;
    }
}

// Save chat history to localStorage
function saveChatHistory() {
    const messages = [];
    const messageElements = chatContainer.querySelectorAll('.message');
    
    messageElements.forEach(msg => {
        const sender = msg.classList.contains('user') ? 'user' : 'bot';
        const content = msg.querySelector('.message-content');
        if (content) {
            messages.push({
                sender: sender,
                content: content.innerHTML,
                isMarkdown: sender === 'bot'
            });
        }
    });
    
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
}

// Load chat history from localStorage
function loadChatHistory() {
    const savedHistory = localStorage.getItem(CHAT_STORAGE_KEY);
    
    if (savedHistory) {
        try {
            const messages = JSON.parse(savedHistory);
            
            if (messages.length > 0) {
                // Remove welcome message
                const welcomeMsg = chatContainer.querySelector('.welcome-message');
                if (welcomeMsg) {
                    welcomeMsg.remove();
                }
                
                // Restore messages
                messages.forEach(msg => {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${msg.sender}`;
                    
                    const contentDiv = document.createElement('div');
                    contentDiv.className = 'message-content';
                    contentDiv.innerHTML = msg.content;
                    
                    messageDiv.appendChild(contentDiv);
                    chatContainer.appendChild(messageDiv);
                });
                
                // Scroll to bottom
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
}

// Focus input on load
window.addEventListener('load', () => {
    messageInput.focus();
});
