async function loadRoomData(roomId) {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "/lobby/";
        return;
    }

    try {
        const res = await fetch(`/lobby/api/room/${roomId}/data`, {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (res.ok) {
            const data = await res.json();
            document.getElementById("username").textContent = data.username;
            document.getElementById("status").textContent = "Waiting for other players...";
        } else if (res.status === 403) {
            alert("You are not allowed in this room");
            window.location.href = "/lobby/";
        }
    } catch (err) {
        console.error(err);
    }
}

const roomId = document.getElementById("status").dataset.roomId;
loadRoomData(roomId);
