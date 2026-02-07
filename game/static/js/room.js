const roomId = document.getElementById("status").dataset.roomId;

async function loadRoomData(roomId) {
    const token = localStorage.getItem("token");

    const res = await fetch(`/game/api/room/${roomId}/data`, {
        headers: { "Authorization": "Bearer " + token }
    });

    const data = await res.json();
    const currentUser = data.players.find(p => p.id === data.user_id);
    document.getElementById("username").textContent = currentUser.username

    document.getElementById("room-title").textContent = data.room_name;
    document.getElementById("status-text").textContent = data.status === "waiting" ? "Waiting for other players..." : "";

    const list = document.getElementById("players-list");
    list.innerHTML = "";
    data.players.forEach(p => {
        const li = document.createElement("li");
        li.textContent = `${p.seat_number}. ${p.username}`;
        list.appendChild(li);
    });

    const startBtn = document.getElementById("start-btn");
    startBtn.style.display = (data.is_owner && data.players.length >= 2) ? "block" : "none";

    if (data.status === "started") {
        clearInterval(pollingId);
        window.location.href = `/game/play/${roomId}`;
    }
}

const pollingId = setInterval(() => loadRoomData(roomId), 2000);

document.getElementById("start-btn").addEventListener("click", async () => {
    const token = localStorage.getItem("token");

    await fetch(`/game/api/room/${roomId}/start`, {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token
        }
    });
});
