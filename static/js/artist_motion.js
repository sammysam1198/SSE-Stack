function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

function updateMotionCard(card) {
    const rect = card.getBoundingClientRect();
    const viewportHeight = window.innerHeight;

    // Progress: 0 when card enters lower viewport, 1 when it leaves upper viewport
    const rawProgress = (viewportHeight - rect.top) / (viewportHeight + rect.height);
    const progress = clamp(rawProgress, 0, 1);

    // CYAN OBJECT
    // Phase 1: move up the right side at 2x feel
    // Phase 2: once it reaches top-right, move left across the top
    const cyanPhaseSplit = 0.5;
    let cyanTop;
    let cyanRight;

    if (progress < cyanPhaseSplit) {
        const phaseProgress = progress / cyanPhaseSplit;
        cyanTop = 70 - (phaseProgress * 80);     // 70% down to -10%
        cyanRight = -90;                         // stay on right edge
    } else {
        const phaseProgress = (progress - cyanPhaseSplit) / (1 - cyanPhaseSplit);
        cyanTop = -10;                           // locked at top
        cyanRight = -90 + (phaseProgress * 220); // moves inward/left across top
    }

    // MAGENTA OBJECT
    // Phase 1: move down left side at 1x feel
    // Phase 2: once it reaches lower area, move right across bottom
    const magentaPhaseSplit = 0.5;
    let magentaTop;
    let magentaLeft;

    if (progress < magentaPhaseSplit) {
        const phaseProgress = progress / magentaPhaseSplit;
        magentaTop = -10 + (phaseProgress * 80); // -10% down to 70%
        magentaLeft = -90;                       // stay on left edge
    } else {
        const phaseProgress = (progress - magentaPhaseSplit) / (1 - magentaPhaseSplit);
        magentaTop = 70;                         // locked near bottom
        magentaLeft = -90 + (phaseProgress * 220); // moves inward/right across bottom
    }

    card.style.setProperty("--cyan-top", `${cyanTop}%`);
    card.style.setProperty("--cyan-right", `${cyanRight}px`);
    card.style.setProperty("--magenta-top", `${magentaTop}%`);
    card.style.setProperty("--magenta-left", `${magentaLeft}px`);
}

function updateAllMotionCards() {
    const cards = document.querySelectorAll(".motion-card");
    cards.forEach(updateMotionCard);
}

window.addEventListener("scroll", updateAllMotionCards, { passive: true });
window.addEventListener("resize", updateAllMotionCards);
window.addEventListener("load", updateAllMotionCards);
document.addEventListener("DOMContentLoaded", updateAllMotionCards);