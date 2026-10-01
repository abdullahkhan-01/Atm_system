setTimeout(() => {
    document.querySelectorAll(".alert").forEach((alert) => {
        alert.style.transition = "opacity .4s";
        alert.style.opacity = "0";

        setTimeout(() => alert.remove(), 400);
    });
}, 4500);
