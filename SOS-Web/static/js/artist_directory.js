document.addEventListener("DOMContentLoaded", () => {
    const filterButtons = document.querySelectorAll(".filter-chip");
    const artistCards = document.querySelectorAll(".artist-directory-card");
    const artistLinks = document.querySelectorAll(".artist-read-more");

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const filter = (button.dataset.filter || "").trim().toLowerCase();

            filterButtons.forEach((chip) => chip.classList.remove("active"));
            button.classList.add("active");

            artistCards.forEach((card) => {
                const tags = (card.dataset.tags || "").toLowerCase();

                if (filter === "all" || tags.includes(filter)) {
                    card.classList.remove("is-hidden");
                } else {
                    card.classList.add("is-hidden");
                }
            });
        });
    });

    artistLinks.forEach((link) => {
        link.addEventListener("click", (event) => {
            const slug = (link.dataset.artistSlug || "").trim();
            if (!slug) {
                event.preventDefault();
            }
        });
    });
});