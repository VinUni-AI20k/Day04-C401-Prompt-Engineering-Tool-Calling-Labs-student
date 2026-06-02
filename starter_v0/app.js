document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const eventLogs = document.getElementById('event-logs');
    const typingIndicator = document.getElementById('typing-indicator');
    const providerSelect = document.getElementById('provider-select');
    
    // Conversation history context
    let messagesContext = [];
    
    function logEvent(type, text) {
        const time = new Date().toLocaleTimeString();
        let htmlClass = type === 'tool_event' ? 'tool-call' : 'tool-result';
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${htmlClass}`;
        logEntry.innerHTML = `
            <span class="log-time">${time}</span>
            <span class="log-text">${text}</span>
        `;
        eventLogs.prepend(logEntry);
    }
    
    function formatMessageText(text) {
        // Very basic simple markdown bold parsing for demonstration
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                   .replace(/\n/g, '<br>');
    }
    
    function appendMessage(role, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-msg`;
        
        messageDiv.innerHTML = `
            <div class="message-bubble glass-panel">
                ${formatMessageText(text)}
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const text = userInput.value.trim();
        if (!text) return;
        
        // Disable input
        userInput.value = '';
        userInput.disabled = true;
        
        // Append User Message
        appendMessage('user', text);
        messagesContext.push({ role: 'user', content: text });
        
        // Show typing indicator
        typingIndicator.classList.remove('hidden');
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    messages: messagesContext,
                    provider: providerSelect.value
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                const aiText = data.assistant_text || "Agent đã hoàn thành nhưng không có nội dung phản hồi.";
                appendMessage('bot', aiText);
                messagesContext.push({ role: 'assistant', content: aiText });
                
                // Print tool events if any
                if (data.tool_events && data.tool_events.length > 0) {
                    data.tool_events.forEach(evt => {
                        logEvent('tool_event', `Tool call: ${evt.tool}`);
                        const resSnippet = JSON.stringify(evt.result || {}).substring(0, 50);
                        logEvent('tool_response', `Result: ${resSnippet}...`);
                    });
                }
            } else {
                appendMessage('system', "Lỗi kết nối từ Agent: " + (data.detail || "Không xác định"));
            }
        } catch (error) {
            appendMessage('system', "Không thể kết nối đến Backend: " + error.message);
        } finally {
            typingIndicator.classList.add('hidden');
            userInput.disabled = false;
            userInput.focus();
        }
    });
});
