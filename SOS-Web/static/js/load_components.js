async function loadFooter() {
    const placeholder = document.getElementById("footer-placeholder");
    if (!placeholder) return;

    try {
        const res = await fetch("/static/partials/footer.html");
        const html = await res.text();

        placeholder.innerHTML = html;

        if (typeof bindSigninButtons === "function") {
            bindSigninButtons();
        }
    } catch (err) {
        console.error("Failed to load footer:", err);
    }
}

document.addEventListener("DOMContentLoaded", loadFooter);