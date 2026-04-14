function getReleasePageParams() {
    const params = new URLSearchParams(window.location.search);

    return {
        artist: params.get("artist"),
        submission: params.get("submission"),
    };
}

async function fetchMyUser() {
    return await getCurrentUser();
}

function isPrivilegedRole(role) {
    return role === "admin" || role === "developer";
}
