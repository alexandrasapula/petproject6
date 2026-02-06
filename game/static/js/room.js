async function loadRoomData(roomId) {
    const token = localStorage.getItem("token");

    const res = await fetch(`/game/api/room/${roomId}/data`, {
        headers: { "Authorization": "Bearer " + token }
    });

    const data = await res.json();

    document.getElementById("room-title").textContent = data.room_name;

    document.getElementById("status-text").textContent =
        "Waiting for other players...";

    const list = document.getElementById("players-list");
    list.innerHTML = "";

    data.players.forEach(p => {
        const li = document.createElement("li");
        li.textContent = `${p.seat_number}. ${p.username}`;
        list.appendChild(li);
    });

    const startBtn = document.getElementById("start-btn");

    if (data.is_owner && data.players.length >= 2) {
        startBtn.style.display = "block";
    } 
    else {
        startBtn.style.display = "none";
    }
}


document.getElementById("start-btn").addEventListener("click", async () => {
    const token = localStorage.getItem("token");

    await fetch(`/game/api/room/${roomId}/start`, {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token
        }
    });
});


const {roomId} = document.getElementById("status").dataset;
setInterval(() => loadRoomData(roomId), 2000);
