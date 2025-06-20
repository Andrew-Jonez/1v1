// Elements
const myScoreSpan = document.getElementById('myScore');
const opponentScoreSpan = document.getElementById('opponentScore');
const messageBox = document.getElementById('messageBox');
const shootBtn = document.getElementById('shootBtn');
const dribbleBtn = document.getElementById('dribbleBtn');
const stealBtn = document.getElementById('stealBtn');
const overlay = document.getElementById('welcomeOverlay');
const closeOverlayBtn = document.getElementById('closeOverlayBtn');
const gameMusic = document.getElementById('gameMusic');
const swishSound = document.getElementById("swish-sound");

// Disable or enable all buttons (shoot, pass, steal)
function disableButtons(disable = true) {
    shootBtn.disabled = disable;
    dribbleBtn.disabled = disable;
    stealBtn.disabled = disable;

    if (disable) {
        shootBtn.classList.add('disabled');
        dribbleBtn.classList.add('disabled');
        stealBtn.classList.add('disabled');
    } else {
        shootBtn.classList.remove('disabled');
        dribbleBtn.classList.remove('disabled');
        stealBtn.classList.remove('disabled');
    }
}

// Show or hide steal button
function setStealVisibility(show) {
    stealBtn.style.display = show ? 'inline-block' : 'none';
}

// Display messages in messageBox, show max 3 messages at a time, then call callback
function displayMessages(messages, callback) {
    if (messages.length === 0) {
        if (callback) callback();
        return;
    }

    const message = messages.shift();

    const p = document.createElement('p');
    p.textContent = message;
    messageBox.appendChild(p);

    // Only show the last 3 messages
    while (messageBox.children.length > 3) {
        messageBox.removeChild(messageBox.firstChild);
    }

    if (message.includes("Press 'Steal'")) {
        stealBtn.style.display = 'inline-block';
        stealBtn.disabled = false;
        if (callback) callback();
        return;
    }

    setTimeout(() => displayMessages(messages, callback), 1000);
}

// Send action to server: action can be 'shoot', 'dribble', 'auto', or null; steal is boolean
function sendAction(action, steal = false) {
    disableButtons(true);

    fetch('/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action, steal: steal })
    })
    .then(response => response.json())
    .then(data => {
        // Steal button visibility
        setStealVisibility(data.messages.some(msg => msg.toLowerCase().includes('steal')));

        // Play swish if points were scored
        if (data.messages.some(msg => msg.toLowerCase().includes("scored 2 points"))) {
            swishSound.currentTime = 0;
            swishSound.play().catch(err => console.warn("Playback blocked:", err));
        }

        displayMessages([...data.messages], () => {
            if (!data.game_over) {
                if (data.auto_continue) {
                    setTimeout(() => sendAction('auto'), 1000);
                } else {
                    disableButtons(false);
                }
            } else {
                disableButtons(true);
                setStealVisibility(false);

                if (data.messages.some(m => m.toLowerCase().includes('you won'))) {
                    fetch('/leaderboard')
                        .then(res => res.json())
                        .then(scores => {
                            const board = document.getElementById('leaderboardList');
                            board.innerHTML = '';

                            scores.forEach((entry, index) => {
                                const li = document.createElement('li');
                                li.textContent = `${index + 1}. ${entry.name} - ${entry.time}s`;
                                board.appendChild(li);
                            });

                            document.getElementById('leaderboardOverlay').style.display = 'flex';
                        })
                        .catch(err => console.error('Failed to load leaderboard', err));
                }
            }
        });

        myScoreSpan.textContent = data.my_score;
        opponentScoreSpan.textContent = data.opponent_score;
    })
    .catch(err => {
        console.error('Error sending action:', err);
        disableButtons(false);
    });
}

// Button click event handlers
shootBtn.addEventListener('click', () => sendAction('shoot'));
dribbleBtn.addEventListener('click', () => sendAction('dribble'));
stealBtn.addEventListener('click', () => {
    stealBtn.style.display = 'none';
    sendAction(null, true);
});

// Overlay start game button handler
closeOverlayBtn.addEventListener('click', () => {
    const playerNameInput = document.getElementById('playerName');
    const playerName = playerNameInput.value.trim();

    const nameRegex = /^[a-zA-Z0-9 _-]{1,20}$/;
    if (!nameRegex.test(playerName)) {
        alert("Invalid name. Only letters, numbers, space, dash and underscore (max 20 chars).");
        return;
    }

    fetch('/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: playerName })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            overlay.style.display = 'none';
            disableButtons(false);
            setStealVisibility(false);
            gameMusic.volume = 0.3;
            gameMusic.play().catch(e => console.log("Autoplay blocked:", e));
        } else {
            alert(data.error || "Unexpected error");
        }
    })
    .catch(err => {
        console.error("Error sending player name:", err);
    });
});

// On page load
window.onload = () => {
    overlay.style.display = 'flex';
    disableButtons(false);
    setStealVisibility(false);
};
