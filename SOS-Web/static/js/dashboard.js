function requireRole(user, allowedRoles = []) {
    if (!user) {
        window.location.href = "/";
        return false;
    }

    if (!allowedRoles.includes(user.role)) {
        window.location.href = "/";
        return false;
    }

    return true;
}

function setText(id, value, fallback = "") {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? fallback;
}

function setHeroImage(imageUrl) {
    const hero = document.getElementById("dashboard-hero");
    if (!hero) return;

    if (imageUrl) {
        hero.style.setProperty("--hero-image", `url('${imageUrl}')`);
    } else {
        hero.style.setProperty(
            "--hero-image",
            "radial-gradient(circle at top left, rgba(255,0,170,0.22), transparent 30%), radial-gradient(circle at bottom right, rgba(0,200,255,0.18), transparent 35%), linear-gradient(135deg, #08101d, #0c0f18)"
        );
    }
}