async function loadUserData() {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "/";
        return;
    }

    try {
        const res = await fetch("/lobby/api/lobby-data", {
            headers: { "Authorization": "Bearer " + token }
        });

        if (res.ok) {
            const data = await res.json();
            document.getElementById("username").textContent = data.username;
            renderRooms(data.rooms);
        } 
        else {
            localStorage.removeItem("token");
            window.location.href = "/";
        }
    } 
    catch (err) {
        console.error(err);
    }
}

function renderRooms(rooms) {
    const roomsDiv = document.getElementById("rooms");
    roomsDiv.innerHTML = "";

    rooms.forEach(room => {
        const div = document.createElement("div");
        div.className = "room";
        div.textContent = room.name;;
        div.addEventListener("click", async () => {
            const token = localStorage.getItem("token");
            const res = await fetch("/lobby/api/join-room", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({ room_id: room.id })
            });

            if (res.ok) {
                const data = await res.json();
                console.log("Joined room:", data);
                window.location.href = `/lobby/room/${room.id}`;
            } 
            else {
                alert("Failed to join room");
            }
        });

        roomsDiv.appendChild(div);
    });
}

document.getElementById("create-room-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const roomName = document.getElementById("room-name").value;
    const token = localStorage.getItem("token");

    try {
        const res = await fetch("/lobby/api/create-room", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ name: roomName })
        });

        if (!res.ok) throw new Error("Failed to create room");

        const newRoom = await res.json();
        window.location.href = `/lobby/room/${newRoom.id}`;
    } 
    catch (err) {
        console.error(err);
        alert("Error creating room");
    }
});

loadUserData();
