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

    // CYAN
    // starts bottom-right
    // moves to top-right at 2x feel
    // then travels left across the top
    if (progress < 0.5) {
        const p = progress / 0.5;
        cyanX = 100;
        cyanY = 100 - (p * 100);
    } else {
        const p = (progress - 0.5) / 0.5;
        cyanX = 100 - (p * 100);
        cyanY = 0;
    }

    // MAGENTA
    // starts top-left
    // moves to bottom-left
    // then travels right across the bottom
    if (progress < 0.5) {
        const p = progress / 0.5;
        magentaX = 0;
        magentaY = p * 100;
    } else {
        const p = (progress - 0.5) / 0.5;
        magentaX = p * 100;
        magentaY = 100;
    }

    card.style.setProperty("--cyan-x", `${cyanX}%`);
    card.style.setProperty("--cyan-y", `${cyanY}%`);
    card.style.setProperty("--magenta-x", `${magentaX}%`);
    card.style.setProperty("--magenta-y", `${magentaY}%`);
}

function updateAllMotionCards() {
    document.querySelectorAll(".motion-card").forEach(updateMotionCard);
}

window.addEventListener("scroll", updateAllMotionCards, { passive: true });
window.addEventListener("resize", updateAllMotionCards);
window.addEventListener("load", updateAllMotionCards);
document.addEventListener("DOMContentLoaded", updateAllMotionCards);