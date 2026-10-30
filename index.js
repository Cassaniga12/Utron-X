document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chatBox');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    
    // Lista local para rastrear piadas já exibidas e evitar repetições
    let shownJokesHistory = [];

    // Injeta os botões de atalho rápido acima da caixa de digitação
    createCategoryChips();

    function createCategoryChips() {
        const inputArea = document.querySelector('.chat-input-area');
        const chipsContainer = document.createElement('div');
        chipsContainer.className = 'chips-container';
        chipsContainer.style.cssText = `
            display: flex;
            gap: 6px;
            padding: 8px 12px;
            background: #0f172a;
            overflow-x: auto;
            border-top: 1px solid #334155;
        `;

        const categories = [
            { label: '🎲 Aleatória', query: 'Me conte qualquer piada' },
            { label: '💻 Tech', query: 'Piada de tecnologia' },
            { label: '🐶 Animais', query: 'Piada de animais' },
            { label: '🏫 Escola', query: 'Piada de escola' },
            { label: '🧪 Ciência', query: 'Piada de ciência' },
            { label: '💼 Trabalho', query: 'Piada de trabalho' },
            { label: '⚡ Cúmulos', query: 'Piada de cúmulos' }
        ];

        categories.forEach(cat => {
            const btn = document.createElement('button');
            btn.textContent = cat.label;
            btn.style.cssText = `
                background: #1e293b;
                color: #94a3b8;
                border: 1px solid #334155;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 0.8rem;
                cursor: pointer;
                white-space: nowrap;
            `;
            btn.onclick = () => sendQuery(cat.query);
            chipsContainer.appendChild(btn);
        });

        inputArea.parentNode.insertBefore(chipsContainer, inputArea);
    }

    function appendMessage(text, sender, isJoke = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);

        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('bubble');
        bubbleDiv.innerHTML = text;

        // Adiciona botões de reação se for uma piada do bot
        if (sender === 'bot' && isJoke) {
            const reactionDiv = document.createElement('div');
            reactionDiv.style.cssText = 'margin-top: 6px; display: flex; gap: 8px; font-size: 0.8rem; color: #94a3b8;';
            reactionDiv.innerHTML = `
                <button class="react-btn" style="background:none;border:none;cursor:pointer;padding:0;">😂</button>
                <button class="react-btn" style="background:none;border:none;cursor:pointer;padding:0;">🔄 Mais uma!</button>
            `;
            
            const buttons = reactionDiv.querySelectorAll('button');
            buttons[0].onclick = () => buttons[0].textContent = '❤️ Valeu!';
            buttons[1].onclick = () => sendQuery('Me conte outra piada!');

            bubbleDiv.appendChild(reactionDiv);
        }

        messageDiv.appendChild(bubbleDiv);
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.classList.add('message', 'bot');
        typingDiv.innerHTML = `<div class="bubble" style="font-style: italic; opacity: 0.7;">Utron X está pensando em uma piada... 🤔</div>`;
        chatBox.appendChild(typingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingDiv = document.getElementById('typingIndicator');
        if (typingDiv) typingDiv.remove();
    }

    async function sendQuery(text) {
        if (!text) return;

        appendMessage(text, 'user');
        userInput.value = '';
        showTypingIndicator();

        try {
            const response = await fetch('http://localhost:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    history: shownJokesHistory
                })
            });

            const data = await response.json();
            removeTypingIndicator();

            if (data.status === 'success') {
                shownJokesHistory.push(data.bot); // Registra no histórico para evitar repetição
                appendMessage(data.bot, 'bot', true);
            } else {
                appendMessage('Ops! Tive um curto-circuito e esqueci a piada.', 'bot');
            }
        } catch (error) {
            removeTypingIndicator();
            console.error('Erro de conexão:', error);
            appendMessage('⚠️ Não consegui me conectar ao backend Python. Certifique-se de que o app.py está rodando!', 'bot');
        }
    }

    sendBtn.addEventListener('click', () => sendQuery(userInput.value.trim()));
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendQuery(userInput.value.trim());
    });
});