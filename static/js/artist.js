const flipSheenCards = document.querySelectorAll('.flip-sheen');

function updateFlipSheen() {
    const viewportHeight = window.innerHeight;

    flipSheenCards.forEach((card) => {
        const rect = card.getBoundingClientRect();
        const center = rect.top + rect.height / 2;

        let progress = center / viewportHeight;
        progress = Math.max(0, Math.min(1, progress));

        const leftY = progress * 100;
        const rightY = 100 - (progress * 100);

        card.style.setProperty('--glow-left-y', `${leftY}%`);
        card.style.setProperty('--glow-right-y', `${rightY}%`);
    });
}

window.addEventListener('scroll', updateFlipSheen, { passive: true });
window.addEventListener('resize', updateFlipSheen);
window.addEventListener('load', updateFlipSheen);




