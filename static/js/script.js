document.addEventListener('DOMContentLoaded', function () {
    const shootBtn = document.getElementById('shoot-btn');
    const passBtn = document.getElementById('pass-btn');
    const stealBtn = document.getElementById('steal-btn');
    const messageDiv = document.getElementById('message');
    const myScoreSpan = document.getElementById('my-score');
    const opponentScoreSpan = document.getElementById('opponent-score');

    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async function displayMessages(messages) {
        messageDiv.innerHTML = "";
        for (let msg of messages) {
            const p = document.createElement('p');
            p.textContent = msg;
            messageDiv.appendChild(p);
            await delay(1000); // ← Change this value to modify delay (e.g. 3000 for 3 seconds)
        }
    }

    function disableButtons() {
        shootBtn.disabled = true;
        passBtn.disabled = true;
        stealBtn.disabled = true;
    }

    function enableButtons() {
        shootBtn.disabled = false;
        passBtn.disabled = false;
        stealBtn.disabled = true; // Start disabled until prompted
    }

    async function sendAction(action, steal = false) {
        disableButtons();
        const response = await fetch('/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, steal })
        });

        const data = await response.json();
        await displayMessages(data.messages);

        myScoreSpan.textContent = data.my_score;
        opponentScoreSpan.textContent = data.opponent_score;

        if (data.messages.some(msg => msg.includes("press Steal"))) {
            stealBtn.disabled = false;
        } else if (!data.game_over) {
            enableButtons();
        }

        if (data.game_over) {
            disableButtons();
        }
    }

    shootBtn.addEventListener('click', () => sendAction('shoot'));
    passBtn.addEventListener('click', () => sendAction('pass'));
    stealBtn.addEventListener('click', () => {
    stealBtn.style.display = 'none';
    sendAction('steal_attempt');
});
