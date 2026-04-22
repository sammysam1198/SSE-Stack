document.addEventListener("DOMContentLoaded", async () => {
    const list = document.getElementById("release-list");
    const errorBox = document.getElementById("release-error");
    const pageTitle = document.getElementById("release-page-title");

    if (!list) return;

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

    function formatStatus(status = "") {
        const normalized = String(status || "draft").replaceAll("_", " ");
        return normalized.charAt(0).toUpperCase() + normalized.slice(1);
    }

    function formatArtists(release) {
        const names = (release.artists || [])
            .map((artist) => artist.display_name)
            .filter(Boolean);

        return names.length ? names.join(", ") : "Unknown Artist";
    }

    function buildAudioPlayer(release) {
        const firstTrackWithAudio = (release.tracks || []).find((track) => track.audio_object_key);

        if (!firstTrackWithAudio) {
            return `<p class="release-audio-empty">No audio preview available yet.</p>`;
        }

        const audioUrl = resolveAssetUrl(firstTrackWithAudio.audio_object_key);
        if (!audioUrl) {
            return `<p class="release-audio-empty">No audio preview available yet.</p>`;
        }

        return `
            <div class="release-player">
                <p class="release-player__label">${escapeHtml(firstTrackWithAudio.track_title || "Track Preview")}</p>
                <audio controls preload="none" class="release-player__audio">
                    <source src="${escapeHtml(audioUrl)}" type="${escapeHtml(firstTrackWithAudio.audio_mime_type || "audio/wav")}" />
                </audio>
            </div>
        `;
    }

    function buildCard(release) {
        const artworkUrl = resolveAssetUrl(release.artwork_object_key);
        const themedStyle = artworkUrl
            ? `style="--release-art: url('${artworkUrl.replaceAll("'", "\\'")}')"`
            : "";

        return `
            <article class="release-card release-card--rich" ${themedStyle}>
                <div class="release-card__bg"></div>

                <div class="release-card__media">
                    <img
                        src="${escapeHtml(artworkUrl || "/static/logos/sse.png")}"
                        alt="${escapeHtml(release.release_title || "Release artwork")}"
                        class="release-card__art"
                    />
                </div>

                <div class="release-card__body">
                    <div class="release-card__topline">
                        <span class="release-pill">${escapeHtml(formatStatus(release.status))}</span>
                        <span class="release-pill release-pill--ghost">${escapeHtml(release.release_type || "—")}</span>
                    </div>

                    <h3 class="release-card__title">${escapeHtml(release.release_title || "Untitled Release")}</h3>
                    <p class="release-card__artists">${escapeHtml(formatArtists(release))}</p>

                    <div class="release-card__meta">
                        <span>Tracks: ${escapeHtml(String((release.tracks || []).length || 0))}</span>
                        <span>Artists: ${escapeHtml(String((release.artists || []).length || 0))}</span>
                    </div>
                    
                            ${
            release.artist_notes
                ? `<div class="release-review-note">
                     <strong>Label Notes:</strong>
                        <p>${escapeHtml(release.artist_notes)}</p>
                   </div>`
                : ""
        }


                    ${buildAudioPlayer(release)}
                    
                    <div class="release-card-actions">
                    
                    
    ${
            String(release.status || "").toLowerCase() === "draft"
                ? `<a href="/releases/edit?submission=${release.id}" class="release-btn secondary">Edit Draft</a>`
                : `<span class="release-btn secondary is-disabled" aria-disabled="true">Locked</span>`
        }
                    </div>
                </div>
            </article>
        `;
    }

    try {
        const user = await getCurrentUser();
        if (!user) {
            window.location.href = "/";
            return;
        }

        const { artist } = getReleasePageParams();

        let query = "/api/releases";
        if (artist && isPrivilegedRole(user.role)) {
            query += `?artist=${encodeURIComponent(artist)}`;
        }

        const data = await apiFetch(query);
        const releases = data.releases || [];

        if (pageTitle && artist && isPrivilegedRole(user.role)) {
            pageTitle.textContent = `Releases for ${artist}`;
        }

        if (!releases.length) {
            list.innerHTML = `<p class="release-empty-state-copy">No releases found.</p>`;
            return;
        }

        list.innerHTML = releases.map(buildCard).join("");
    } catch (error) {
        if (errorBox) {
            errorBox.textContent = error.message || "Failed to load releases.";
        }
    }
});