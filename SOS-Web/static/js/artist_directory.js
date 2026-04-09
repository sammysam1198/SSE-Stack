const filterButtons = document.querySelectorAll(".filter-chip");
const artistCards = document.querySelectorAll(".artist-directory-card");

filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const filter = button.dataset.filter;

        filterButtons.forEach((chip) => chip.classList.remove("active"));
        button.classList.add("active");

        artistCards.forEach((card) => {
            const tags = card.dataset.tags || "";

            if (filter === "all" || tags.includes(filter)) {
                card.classList.remove("is-hidden");
            } else {
                card.classList.add("is-hidden");
            }
        });
    });
});