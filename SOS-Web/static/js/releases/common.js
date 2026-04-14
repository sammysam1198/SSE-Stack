function getReleasePageParams() {
    const params = new URLSearchParams(window.location.search);

    return {
        artist: params.get("artist"),
        submission: params.get("submission"),
    };
}

function isPrivilegedRole(role) {
    return role === "admin" || role === "developer";
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}