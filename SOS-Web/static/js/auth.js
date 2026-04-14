async function getCurrentUser() {
    try {
        const data = await apiFetch("/api/auth/me");
        return data.user || null;
    } catch (error) {
        return null;
    }
}

async function signin(email, password) {
    const data = await apiFetch("/api/auth/signin", {
        method: "POST",
        body: { email, password }
    });

    return data.user;
}

async function signout() {
    await apiFetch("/api/auth/signout", {
        method: "POST"
    });
}

function getDashboardPathForRole(role) {
    if (role === "developer") return "/dashboard-developer";
    if (role === "admin") return "/dashboard-admin";
    if (role === "artist") return "/dashboard-artist";
    return "/";
}

function roleLabel(role) {
    if (!role) return "";
    return role.charAt(0).toUpperCase() + role.slice(1);
}