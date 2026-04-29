document.addEventListener("DOMContentLoaded", async () => {
    const grid = document.getElementById("artistDirectory");
    const filterButtons = document.querySelectorAll(".filter-chip");
    const base = (window.SSE_ASSET_BASE_URL || "https://pub-4d4f2d565e844d6fb3e84f51d1093198.r2.dev").trim();

    if (!grid) return;

    let artists = [];
    let activeFilter = "all";

    function resolveAssetUrl(value = "") {
        const raw = String(value || "").trim();
        if (!raw) return "";

        if (/^https?:\/\//i.test(raw) || raw.startsWith("/")) {
            return raw;
        }

        const base = (window.SSE_ASSET_BASE_URL || "").trim();
        if (!base) return "";

        return `${base.replace(/\/+$/, "")}/${raw.replace(/^\/+/, "")}`;
    }

    function escapeHtml(value = "") {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");
    }

    function getTags(profile) {
        return [
            profile.primary_genre,
            profile.genre2,
            profile.genre3,
            profile.primary_instrument,
            profile.role2,
            profile.role3,
            profile.primary_vibe,
        ]
            .map((tag) => String(tag || "").trim())
            .filter(Boolean);
    }

    function artistMatchesFilter(profile) {
        if (activeFilter === "all") return true;

        const searchable = getTags(profile)
            .join(" ")
            .toLowerCase();

        return searchable.includes(activeFilter);
    }

    function renderArtists() {
        const visible = artists.filter(artistMatchesFilter);

        if (!visible.length) {
            grid.innerHTML = `
                <article class="artist-directory-card glass glass-depth">
                    <div class="artist-card-body">
                        <h2 class="artist-card-title">No artists found</h2>
                        <p class="artist-card-tagline">No roster profiles match this filter yet.</p>
                    </div>
                </article>
            `;
            return;
        }

        grid.innerHTML = visible.map((artist, index) => {
            const tags = [
                artist.primary_genre,
                artist.primary_instrument,
                artist.primary_vibe
            ].filter(Boolean);
            const imageKey = artist.profile_portrait_key || artist.artist_logo_key || artist.dashboard_banner_key;
            const imageUrl = resolveAssetUrl(imageKey) || "/static/logos/sse.png";
            const slug = artist.artist_page || artist.id;

            const cardClass = [
                "artist-directory-card",
                "glass",
                index % 3 === 0 ? "glass-depth" : index % 3 === 1 ? "glass-rim" : "glass-soft",
            ].join(" ");

            return `
                <article class="${cardClass}" data-tags="${escapeHtml(tags.join(" ").toLowerCase())}">
                    <div class="artist-card-image">
                        <img src="${escapeHtml(imageUrl)}" alt="${escapeHtml(artist.artist_name || "Artist")} artist image">
                    </div>

                    <div class="artist-card-body">
                        <h2 class="artist-card-title">${escapeHtml(artist.artist_name || "Artist")}</h2>
                        <p class="artist-card-tagline">
                            ${escapeHtml(artist.tagline || "SpacedOut Studios artist.")}
                        </p>

                        <div class="tag-row">
                        ${
                         tags.map(tag => `
                            <span class="tag">${escapeHtml(tag)}</span>
                            `).join("")
                       }
                        </div>

                        <div class="artist-card-actions">
                            <a class="button primary artist-read-more" href="/artists/artist?slug=${encodeURIComponent(slug)}" data-artist-slug="${escapeHtml(slug)}">
                                Read More
                            </a>
                        </div>
                    </div>
                </article>
            `;
        }).join("");
    }

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            activeFilter = (button.dataset.filter || "all").trim().toLowerCase();

            filterButtons.forEach((chip) => chip.classList.remove("active"));
            button.classList.add("active");

            renderArtists();
        });
    });

    try {
        grid.innerHTML = `<p class="section-copy">Loading roster...</p>`;

        const data = await apiFetch("/api/artists/public");
        artists = data.artist_profiles || [];

        renderArtists();
    } catch (error) {
        console.error("Failed to load artist directory:", error);
        grid.innerHTML = `<p class="section-copy">Could not load artist directory.</p>`;
    }
});