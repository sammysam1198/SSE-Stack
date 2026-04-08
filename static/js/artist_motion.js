function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function updateMotionCard(card) {
  const rect = card.getBoundingClientRect();
  const viewportHeight = window.innerHeight;

  const rawProgress = (viewportHeight - rect.top) / (viewportHeight + rect.height);
  const progress = clamp(rawProgress, 0, 1);

  let magentaX, magentaY;
  let cyanX, cyanY;

  // MAGENTA
  // top-left -> bottom-left -> bottom-right
  if (progress < 0.8) {
    const p = progress / 0.8;
    magentaX = 0;
    magentaY = p * 100;
  } else {
    const p = (progress - 0.8) / 0.8;
    magentaX = p * 100;
    magentaY = 100;
  }

  // CYAN
  // bottom-right -> top-right -> top-left
  if (progress < 0.8) {
    const p = progress / 0.8;
    cyanX = 100;
    cyanY = 100 - (p * 100);
  } else {
    const p = (progress - 0.8) / 0.8;
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