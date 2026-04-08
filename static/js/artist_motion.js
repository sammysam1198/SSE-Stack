function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

function updateMotionCard(card) {
    const rect = card.getBoundingClientRect();
    const viewportHeight = window.innerHeight;

    const rawProgress = (viewportHeight - rect.top) / (viewportHeight + rect.height);
    const progress = clamp(rawProgress, 0, 1);

    let cyanX, cyanY;
    let magentaX, magentaY;

    // MAGENTA
    // start: top-left
    // move down left side
    // then move right across bottom
    if (progress < 0.5) {
        const p = progress / 0.5;
        magentaX = 0;
        magentaY = p * 100;
    } else {
        const p = (progress - 0.5) / 0.5;
        magentaX = p * 100;
        magentaY = 100;
    }

    // CYAN
    // start: bottom-right
    // move up right side faster
    // then move left across top
    if (progress < 0.5) {
        const p = progress / 0.5;
        cyanX = 100;
        cyanY = 100 - (p * 100);
    } else {
        const p = (progress - 0.5) / 0.5;
        cyanX = 100 - (p * 100);
        cyanY = 0;
    }

    card.style.setProperty("--magenta-x", `${magentaX}%`);
    card.style.setProperty("--magenta-y", `${magentaY}%`);
    card.style.setProperty("--cyan-x", `${cyanX}%`);
    card.style.setProperty("--cyan-y", `${cyanY}%`);
}

function updateAllMotionCards() {
    document.querySelectorAll(".motion-card").forEach(updateMotionCard);
}

window.addEventListener("scroll", updateAllMotionCards, { passive: true });
window.addEventListener("resize", updateAllMotionCards);
window.addEventListener("load", updateAllMotionCards);
document.addEventListener("DOMContentLoaded", updateAllMotionCards);