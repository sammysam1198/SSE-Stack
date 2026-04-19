document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("release-form");
    const artistContext = document.getElementById("artist-context");
    const errorBox = document.getElementById("release-error");
    const successBox = document.getElementById("release-success");
    const artistsContainer = document.getElementById("artists-container");
    const addArtistButton = document.getElementById("add-artist-button");

    if (!form) return;

    let artistCount = 0;
    let currentUser = null;
    let artistProfile = null;

    function clearMessages() {
        if (errorBox) errorBox.textContent = "";
        if (successBox) successBox.textContent = "";
    }

    function addArtistCard(initialData = {}, isMain = false) {
        if (!artistsContainer) return;
        if (artistCount >= 5) return;

        artistCount += 1;

        const card = document.createElement("div");
        card.className = "artist-card";
        card.dataset.artistIndex = String(artistCount);
        card.dataset.roleType = isMain ? "main" : "featured";

        card.innerHTML = `
            <div class="section-row">
                <h3>${isMain ? "Main Artist" : `Featured Artist ${artistCount}`}</h3>
                ${isMain ? "" : `<button type="button" class="remove-artist-button">Remove</button>`}
            </div>

            <label>
                Artist Name
                <input type="text" class="artist-display-name" value="${escapeHtml(initialData.display_name || "")}" ${isMain ? "required" : ""} />
            </label>

            <label>
                Email
                <input type="email" class="artist-email" value="${escapeHtml(initialData.email || "")}" required />
            </label>

            <label>
                First Name
                <input type="text" class="artist-first-name" value="${escapeHtml(initialData.first_name || "")}" />
            </label>

            <label>
                Last Name
                <input type="text" class="artist-last-name" value="${escapeHtml(initialData.last_name || "")}" />
            </label>

            <label>
                IPI
                <input type="text" class="artist-ipi" placeholder="A number from your PRO" value="${escapeHtml(initialData.ipi || "")}" />
            </label>

            <label>
                PRO
                <input type="text" class="artist-pro" placeholder="ASCAP, BMI etc" value="${escapeHtml(initialData.pro || "")}" />
            </label>

            <label>
                Publisher
                <input type="text" class="artist-publisher" value="${escapeHtml(initialData.publisher || "")}" />
            </label>

            <label>
                Spotify Link
                <input type="url" class="artist-spotify-url" value="${escapeHtml(initialData.spotify_url || "")}" />
            </label>

            <label>
                Apple Music Link
                <input type="url" class="artist-apple-music-url" value="${escapeHtml(initialData.apple_music_url || "")}" />
            </label>

            <label>
                YouTube Link
                <input type="url" class="artist-youtube-url" value="${escapeHtml(initialData.youtube_url || "")}" />
            </label>

            <label>
                SoundCloud Link
                <input type="url" class="artist-soundcloud-url" value="${escapeHtml(initialData.soundcloud_url || "")}" />
            </label>
        `;

        artistsContainer.appendChild(card);

        const removeButton = card.querySelector(".remove-artist-button");
        if (removeButton) {
            removeButton.addEventListener("click", () => {
                card.remove();
                artistCount -= 1;
            });
        }
    }

    function collectArtists() {
        const cards = Array.from(document.querySelectorAll(".artist-card"));

        return cards.map((card, index) => ({
            role_type: index === 0 ? "main" : "featured",
            display_name: card.querySelector(".artist-display-name")?.value?.trim() || "",
            email: card.querySelector(".artist-email")?.value?.trim() || "",
            first_name: card.querySelector(".artist-first-name")?.value?.trim() || "",
            last_name: card.querySelector(".artist-last-name")?.value?.trim() || "",
            ipi: card.querySelector(".artist-ipi")?.value?.trim() || "",
            pro: card.querySelector(".artist-pro")?.value?.trim() || "",
            publisher: card.querySelector(".artist-publisher")?.value?.trim() || "",
            spotify_url: card.querySelector(".artist-spotify-url")?.value?.trim() || "",
            apple_music_url: card.querySelector(".artist-apple-music-url")?.value?.trim() || "",
            youtube_url: card.querySelector(".artist-youtube-url")?.value?.trim() || "",
            soundcloud_url: card.querySelector(".artist-soundcloud-url")?.value?.trim() || "",
        }));
    }

    try {
        currentUser = await getCurrentUser();
        if (!currentUser) {
            window.location.href = "/";
            return;
        }

        if (currentUser.role === "artist") {
            const profileData = await apiFetch("/api/artists/me");
            artistProfile = profileData.artist || profileData.profile || profileData;

            addArtistCard({
                display_name: artistProfile.artist_name || "",
                email: currentUser.email || "",
                first_name: artistProfile.first_name || "",
                last_name: artistProfile.last_name || "",
                ipi: artistProfile.ipi || "",
                pro: artistProfile.pro || "",
                publisher: artistProfile.publisher || "",
                spotify_url: artistProfile.spotify_url || "",
                apple_music_url: artistProfile.apple_music_url || "",
                youtube_url: artistProfile.youtube_channel_url || "",
                soundcloud_url: artistProfile.soundcloud_url || "",
            }, true);

            if (artistContext) {
                artistContext.textContent = `Creating release for ${artistProfile.artist_name || "your artist profile"}`;
            }
        } else {
            addArtistCard({}, true);

            if (artistContext) {
                artistContext.textContent = "Creating new release";
            }
        }

        if (addArtistButton) {
            addArtistButton.addEventListener("click", () => {
                if (artistCount >= 5) {
                    errorBox.textContent = "You can add up to 5 artists for now.";
                    return;
                }
                clearMessages();
                addArtistCard({}, false);
            });
        }

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            clearMessages();

            const formData = new FormData(form);
            const artists = collectArtists();

            const payload = {
                release_title: formData.get("release_title")?.trim(),
                release_type: formData.get("release_type")?.trim(),
                preferred_release_date: formData.get("preferred_release_date")?.trim(),
                primary_genre: formData.get("primary_genre")?.trim(),
                other_genres: formData.get("other_genres")?.trim(),
                release_pitch: formData.get("release_pitch")?.trim(),
                artists,
            };

            try {
                const data = await apiFetch("/api/releases", {
                    method: "POST",
                    body: payload,
                });

                successBox.textContent = "Release draft created successfully.";

                if (data.release && data.release.id) {
                    window.location.href = `/releases/edit?submission=${data.release.id}`;
                }
            } catch (error) {
                errorBox.textContent = error.message || "Failed to create release draft.";
            }
        });
    } catch (error) {
        if (errorBox) {
            errorBox.textContent = error.message || "Failed to load release page.";
        }
    }
});