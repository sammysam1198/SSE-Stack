function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function updateMotionCard(card) {
  const rect = card.getBoundingClientRect();

  // Start animating only after the card begins moving upward past this line.
  // This keeps the initial state locked to:
  // magenta = top-left
  // cyan = bottom-right
  const startLine = 120;

  // Progress is 0 until the card top reaches startLine.
  // Progress becomes 1 by the time one full card height has scrolled past that line.
  const progress = clamp((startLine - rect.top) / rect.height, 0, 1);

  let cyanX, cyanY;
  let magentaX, magentaY;

  // MAGENTA
  // starts top-left
  // moves down left side at normal speed
  // then moves right across the bottom
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
  // starts bottom-right
  // moves up right side faster
  // then moves left across the top
  if (progress < 0.25) {
    const p = progress / 0.25;
    cyanX = 100;
    cyanY = 100 - (p * 100);
  } else {
    const p = (progress - 0.25) / 0.75;
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