const sheenCards = document.querySelectorAll('.sheen-card');

function updateSheen() {
    const scrollY = window.scrollY;
    const viewportH = window.innerHeight;

    sheenCards.forEach((card) => {
    const rect = card.getBoundingClientRect();
    const centerY = rect.top + rect.height / 2;
    const progress = Math.max(0, Math.min(1, centerY / viewportH));

    const sheenX = 20 + (progress * 60);
    const sheenY = 12 + (progress * 28);

    card.style.setProperty('--sheen-x', `${sheenX}%`);
    card.style.setProperty('--sheen-y', `${sheenY}%`);
});
}

    window.addEventListener('scroll', updateSheen, { passive: true });
    window.addEventListener('resize', updateSheen);
    window.addEventListener('load', updateSheen);
