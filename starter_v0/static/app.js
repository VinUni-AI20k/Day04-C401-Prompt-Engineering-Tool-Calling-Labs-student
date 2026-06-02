document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const providerSelect = document.getElementById('provider-select');
    const modelSelect = document.getElementById('model-select');
    const versionSelect = document.getElementById('version-select');
    const runsContainer = document.getElementById('runs-container');
    const messagesContainer = document.getElementById('messages-container');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    
    const activeModelVal = document.getElementById('active-model-val');
    const activeVersionVal = document.getElementById('active-version-val');
    
    const inspectorEmptyState = document.getElementById('inspector-empty-state');
    const inspectorLoopContainer = document.getElementById('inspector-loop-container');
    
    // Modal elements
    const clarifyModal = document.getElementById('clarify-modal');
    const modalQuestionText = document.getElementById('modal-question-text');
    const modalInputsContainer = document.getElementById('modal-inputs-container');
    const modalCancelBtn = document.getElementById('modal-cancel-btn');
    const modalSubmitBtn = document.getElementById('modal-submit-btn');

    // App state
    let chatHistory = [];
    let isWaitingForResponse = false;
    let pendingClarifyResponse = null; // Stored value for yes/no or text

    // Enable/disable send button based on input content
    chatInput.addEventListener('input', () => {
        sendBtn.disabled = chatInput.value.trim() === '' || isWaitingForResponse;
    });

    // Handle shift+enter for new line, enter for send
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (chatInput.value.trim() !== '' && !isWaitingForResponse) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Suggestion chips
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            chatInput.value = chip.textContent;
            chatInput.focus();
            sendBtn.disabled = false;
        });
    });

    // Change listeners for headers
    providerSelect.addEventListener('change', () => {
        updateHeaderInfo();
    });
    versionSelect.addEventListener('change', () => {
        activeVersionVal.textContent = versionSelect.value;
    });

    function updateHeaderInfo() {
        const prov = providerSelect.value;
        const modelOverride = modelSelect.value.trim();
        if (modelOverride) {
            activeModelVal.textContent = modelOverride;
        } else {
            activeModelVal.textContent = prov === 'gemini' ? 'gemini-3.5-flash' : (prov === 'openai' ? 'gpt-4o-mini' : 'openai/gpt-4o-mini');
        }
    }
    modelSelect.addEventListener('input', updateHeaderInfo);

    // Load runs history
    async function loadRuns() {
        try {
            const resp = await fetch('/api/runs');
            if (resp.ok) {
                const runs = await resp.json();
                renderRuns(runs);
            }
        } catch (err) {
            console.error('Failed to load runs:', err);
        }
    }

    function renderRuns(runs) {
        if (runs.length === 0) {
            runsContainer.innerHTML = '<div class="loading-runs">No evaluation runs recorded yet.</div>';
            return;
        }
        
        // Sort runs by time descending
        runs.sort((a, b) => b.generated_at.localeCompare(a.generated_at));
        
        runsContainer.innerHTML = runs.map(run => {
            const acc = run.summary.case_accuracy !== undefined ? (run.summary.case_accuracy * 100).toFixed(0) + '%' : 'N/A';
            const date = new Date(run.generated_at).toLocaleString('vi-VN', { hour: '2-digit', minute:'2-digit', day:'2-digit', month:'2-digit' });
            return `
                <div class="run-card">
                    <div class="run-card-header">
                        <span class="run-version">${run.version} - ${run.provider}</span>
                        <span class="run-suite">${run.suite}</span>
                    </div>
                    <div class="run-card-metrics">
                        <div class="metric-item">Accuracy: <span>${acc}</span></div>
                        <div class="metric-item">Time: <span>${date}</span></div>
                    </div>
                </div>
            `;
        }).join('');
    }

    // Clear Chat
    clearChatBtn.addEventListener('click', () => {
        if (confirm('Clear current conversation history?')) {
            chatHistory = [];
            // Keep only first welcome message
            const welcomeMsg = messagesContainer.querySelector('.system-msg');
            messagesContainer.innerHTML = '';
            if (welcomeMsg) messagesContainer.appendChild(welcomeMsg);
            
            // Clear inspector
            inspectorEmptyState.style.display = 'flex';
            inspectorLoopContainer.style.display = 'none';
            inspectorLoopContainer.innerHTML = '';
        }
    });

    // Handle Chat Submit
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text || isWaitingForResponse) return;

        appendUserMessage(text);
        chatInput.value = '';
        sendBtn.disabled = true;
        
        await sendChatToAgent(text);
    });

    function appendUserMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message user-msg';
        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-user"></i></div>
            <div class="message-content">
                <p>${escapeHtml(text)}</p>
            </div>
        `;
        messagesContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendAgentMessage(text, isSystemPrompt = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = isSystemPrompt ? 'message system-msg' : 'message agent-msg';
        
        const avatarHtml = isSystemPrompt 
            ? '<div class="avatar"><i class="fa-solid fa-robot"></i></div>' 
            : '<div class="avatar" style="background-color: var(--color-secondary); color: var(--text-dark)"><i class="fa-solid fa-magic"></i></div>';
            
        msgDiv.innerHTML = `
            ${avatarHtml}
            <div class="message-content">
                <p>${formatMarkdown(text)}</p>
            </div>
        `;
        messagesContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendLoadingMessage() {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message agent-msg loading-msg';
        msgDiv.innerHTML = `
            <div class="avatar" style="background-color: var(--color-secondary); color: var(--text-dark)"><i class="fa-solid fa-magic"></i></div>
            <div class="message-content">
                <p><i class="fa-solid fa-circle-notch fa-spin"></i> Research Agent is thinking and executing tools...</p>
            </div>
        `;
        messagesContainer.appendChild(msgDiv);
        scrollToBottom();
        return msgDiv;
    }

    async function sendChatToAgent(userText) {
        isWaitingForResponse = true;
        const loadingDiv = appendLoadingMessage();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userText,
                    history: chatHistory,
                    provider: providerSelect.value,
                    version: versionSelect.value,
                    model: modelSelect.value.trim() || null
                })
            });

            loadingDiv.remove();

            if (response.ok) {
                const data = await response.json();
                
                // Add to history
                chatHistory.push({ role: 'user', content: userText });
                chatHistory.push({ role: 'assistant', content: data.assistant_text });

                // Render agent response
                appendAgentMessage(data.assistant_text);
                
                // Render mind inspector
                renderMindInspector(data.rounds);
                
                // Handle clarification/confirmation modal trigger
                if (data.status === 'waiting_for_user') {
                    // Find the last round tool call that requested clarification
                    const lastRound = data.rounds[data.rounds.length - 1];
                    const clarifyCall = lastRound.tool_calls.find(c => c.name === 'clarify');
                    
                    if (clarifyCall) {
                        triggerClarifyModal(clarifyCall.args);
                    }
                }
            } else {
                const errData = await response.json();
                appendErrorMessage(errData.detail || 'An error occurred during agent execution.');
            }
        } catch (err) {
            loadingDiv.remove();
            appendErrorMessage(err.message || 'Failed to connect to the agent server.');
        } finally {
            isWaitingForResponse = false;
            sendBtn.disabled = chatInput.value.trim() === '';
        }
    }

    function appendErrorMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message system-msg';
        msgDiv.innerHTML = `
            <div class="avatar" style="background-color: var(--color-danger); color: #ffffff"><i class="fa-solid fa-triangle-exclamation"></i></div>
            <div class="message-content" style="border-color: var(--color-danger)">
                <h3 style="color: var(--color-danger)">Execution Error</h3>
                <p>${escapeHtml(text)}</p>
            </div>
        `;
        messagesContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    // Modal control
    function triggerClarifyModal(args) {
        const question = args.question || 'Vui lòng cung cấp thêm thông tin:';
        const type = args.response_type || 'text';
        const options = args.options || [];

        modalQuestionText.textContent = question;
        modalInputsContainer.innerHTML = '';
        pendingClarifyResponse = null;

        if (type === 'yes_no') {
            modalInputsContainer.innerHTML = `
                <div class="choice-grid">
                    <div class="choice-btn" data-val="yes">Đồng ý (Yes)</div>
                    <div class="choice-btn" data-val="no">Hủy bỏ (No)</div>
                </div>
            `;
            
            const btns = modalInputsContainer.querySelectorAll('.choice-btn');
            btns.forEach(btn => {
                btn.addEventListener('click', () => {
                    btns.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    pendingClarifyResponse = btn.getAttribute('data-val');
                });
            });
        } else if (type === 'choice' && options.length > 0) {
            modalInputsContainer.innerHTML = options.map((opt, i) => `
                <div class="choice-btn" data-val="${opt}">${opt}</div>
            `).join('');
            
            const btns = modalInputsContainer.querySelectorAll('.choice-btn');
            btns.forEach(btn => {
                btn.addEventListener('click', () => {
                    btns.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    pendingClarifyResponse = btn.getAttribute('data-val');
                });
            });
        } else {
            // Text input
            modalInputsContainer.innerHTML = `
                <input type="text" id="modal-text-input" placeholder="Type your response here..." autofocus>
            `;
            
            // Enter sends
            document.getElementById('modal-text-input').addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    modalSubmitBtn.click();
                }
            });
        }

        clarifyModal.style.display = 'flex';
    }

    modalSubmitBtn.addEventListener('click', () => {
        let value = '';
        const textInput = document.getElementById('modal-text-input');
        
        if (textInput) {
            value = textInput.value.trim();
        } else {
            value = pendingClarifyResponse;
        }

        if (!value) {
            alert('Vui lòng nhập hoặc chọn câu trả lời.');
            return;
        }

        clarifyModal.style.display = 'none';
        
        // Append response as a user message in chat
        appendUserMessage(value);
        
        // Send back to agent
        sendChatToAgent(value);
    });

    modalCancelBtn.addEventListener('click', () => {
        clarifyModal.style.display = 'none';
    });

    // Render Mind Inspector Accordion
    function renderMindInspector(rounds) {
        inspectorEmptyState.style.display = 'none';
        inspectorLoopContainer.style.display = 'flex';
        
        inspectorLoopContainer.innerHTML = rounds.map((r, i) => {
            const hasTools = r.tool_calls.length > 0;
            const statusIcon = hasTools ? '🔧' : '✅';
            const roundNum = r.round;
            const openClass = (i === rounds.length - 1) ? 'round-block open' : 'round-block'; // Open last round by default
            
            const thoughtHtml = r.assistant_text 
                ? `
                    <div class="thought-area">
                        <div class="section-label"><i class="fa-solid fa-comment-dots"></i> Thought</div>
                        <div class="thought-text">${escapeHtml(r.assistant_text)}</div>
                    </div>
                ` : '';

            const toolsHtml = hasTools 
                ? `
                    <div class="calls-area">
                        <div class="section-label"><i class="fa-solid fa-gears"></i> Called Tools</div>
                        ${r.tool_calls.map((call, callIdx) => {
                            const resultEvent = r.tool_results[callIdx] || {};
                            const resultJson = JSON.stringify(resultEvent.result || {}, null, 2);
                            return `
                                <div class="call-item">
                                    <div class="call-item-header">
                                        <span class="tool-badge ${call.name}">${call.name}</span>
                                        <span class="call-args">${escapeHtml(JSON.stringify(call.args))}</span>
                                    </div>
                                    <div class="call-result-panel">
                                        <pre><code>${escapeHtml(resultJson)}</code></pre>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                ` : '<div class="section-label"><i class="fa-solid fa-flag-checkered"></i> Round ended without tools</div>';

            return `
                <div class="${openClass}">
                    <div class="round-header" onclick="this.parentElement.classList.toggle('open')">
                        <span class="round-title">
                            <span>${statusIcon} Round ${roundNum}</span>
                            <span class="round-badge">${hasTools ? r.tool_calls.length + ' Call(s)' : 'Answer'}</span>
                        </span>
                        <i class="fa-solid fa-chevron-down chevron"></i>
                    </div>
                    <div class="round-content">
                        ${thoughtHtml}
                        ${toolsHtml}
                    </div>
                </div>
            `;
        }).join('');
    }

    // Helper functions
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function formatMarkdown(text) {
        if (!text) return '';
        let html = escapeHtml(text);
        
        // Bullet points
        html = html.replace(/^\s*-\s+(.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.+<\/li>)+/g, '<ul>$&</ul>');

        // Bold text
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Code blocks
        html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Inline code
        html = html.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // New lines
        html = html.replace(/\n/g, '<br>');
        
        return html;
    }

    // Init
    updateHeaderInfo();
    loadRuns();
});
