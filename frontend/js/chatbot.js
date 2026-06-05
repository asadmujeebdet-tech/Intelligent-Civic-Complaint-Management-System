// Floating AI Chatbot Widget

function initChatbot() {
    if (document.getElementById('civicChatbot')) return;

    const widget = document.createElement('div');
    widget.id = 'civicChatbot';
    widget.innerHTML = `
        <button id="chatbotFab" class="chatbot-fab" aria-label="AI Assistant">
            <i class="fas fa-robot"></i>
            <span>AI Assistant</span>
        </button>
        <div id="chatbotWindow" class="chatbot-window d-none">
            <div class="chatbot-header">
                <div>
                    <strong><i class="fas fa-robot"></i> CivicLens AI Assistant</strong>
                    <small class="d-block text-white-50">Analytics & insights for officials</small>
                </div>
                <button id="chatbotClose" class="btn btn-sm btn-light"><i class="fas fa-times"></i></button>
            </div>
            <div id="chatbotMessages" class="chatbot-messages">
                <div class="chat-msg bot">Hello! Ask me about complaints, trends, hotspots, or reports.</div>
            </div>
            <div class="chatbot-input">
                <input type="text" id="chatbotInput" placeholder="Ask a question..." maxlength="500">
                <button id="chatbotSend" class="btn btn-primary"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>
    `;
    document.body.appendChild(widget);

    const fab = document.getElementById('chatbotFab');
    const windowEl = document.getElementById('chatbotWindow');
    const closeBtn = document.getElementById('chatbotClose');
    const input = document.getElementById('chatbotInput');
    const sendBtn = document.getElementById('chatbotSend');
    const messages = document.getElementById('chatbotMessages');

    fab.addEventListener('click', () => windowEl.classList.toggle('d-none'));
    closeBtn.addEventListener('click', () => windowEl.classList.add('d-none'));

    async function sendMessage() {
        const question = input.value.trim();
        if (!question) return;

        appendMessage(question, 'user');
        input.value = '';
        sendBtn.disabled = true;

        const loadingId = appendMessage('Thinking...', 'bot loading');
        try {
            const answer = await apiClient.chatWithAI(question);
            document.getElementById(loadingId)?.remove();
            appendMessage(answer, 'bot');
        } catch (err) {
            document.getElementById(loadingId)?.remove();
            appendMessage('Sorry, I could not process that request. Please try again.', 'bot error');
        } finally {
            sendBtn.disabled = false;
        }
    }

    function appendMessage(text, type) {
        const id = 'msg-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = `chat-msg ${type}`;
        div.textContent = text;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return id;
    }

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
}

document.addEventListener('DOMContentLoaded', initChatbot);
