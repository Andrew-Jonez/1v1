async function makeMove(action, steal = false) {
    const controls = document.getElementById("controls");
    controls.style.pointerEvents = "none";

    const response = await fetch("/action", {
        method: "POST",
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            action: action,
            steal: steal
        })
    });

    const data = await response.json();

    const messageBox = document.getElementById("messageBox");
    messageBox.innerHTML = "";

    for (let i = 0; i < data.messages.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        messageBox.innerHTML += `<p>${data.messages[i]}</p>`;
    }

    document.getElementById("my_score").textContent = data.my_score;
    document.getElementById("opponent_score").textContent = data.opponent_score;

    if (data.game_over) {
        controls.innerHTML = "";  // Remove all buttons
    } else {
        controls.style.pointerEvents = "auto";
    }
}
