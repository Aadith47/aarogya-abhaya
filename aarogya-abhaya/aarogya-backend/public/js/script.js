function login() {
    const username = document.getElementById("username").value;

    if (username.startsWith("asha")) {
        window.location.href = "asha_dashboard.html";
    } else if (username.startsWith("teen")) {
        window.location.href = "teenager.html";
    } else if (username.startsWith("new")) {
        window.location.href = "newborn.html";
    } else if (username.startsWith("preg")) {
        window.location.href = "pregnant.html";
    } else if (username.startsWith("lha")) {
        window.location.href = "lha.html";
    } else {
        window.location.href = "jpha.html";
    }
}


function updateNotice() {
    const noticeText = document.getElementById("noticeInput").value;
    const board = document.getElementById("noticeBoard");

    if (noticeText.trim() === "") {
        alert("Please enter a notice message");
        return;
    }

    board.innerHTML = `<p>${noticeText}</p>`;
    document.getElementById("noticeInput").value = "";
}
