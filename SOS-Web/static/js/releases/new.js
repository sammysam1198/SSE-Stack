document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("release-form");
    const artistContext = document.getElementById("artist-context");
    const errorBox = document.getElementById("release-error");
    const successBox = document.getElementById("release-success");
    const artistsContainer = document.getElementById("artists-container");
    const tracksContainer = document.getElementById("tracks-container");
    const addArtistButton = document.getElementById("add-artist-button");
    const addTrackButton = document.getElementById("add-track-button");
    const artworkInput = document.getElementById("release-artwork-file");
    const artworkStatus = document.getElementById("release-artwork-status");

    let uploadedArtwork = null;

    let artistCount = 0;
    let trackCount = 0;
    let currentUser = null;
    let mainArtistProfile = null;

    function clearMessages() {
        if (errorBox) errorBox.textContent = "";
        if (successBox) successBox.textContent = "";
    }

    function escapeHtml(value = "") {
        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function artistLooksComplete(data) {
        return Boolean(
            data.display_name &&
            data.email &&
            (
                data.first_name ||
                data.last_name ||
                data.spotify_url ||
                data.apple_music_url ||
                data.youtube_url ||
                data.soundcloud_url
            )
        );
    }

    function updateSplitVisibility() {
        const cards = Array.from(document.querySelectorAll(".artist-card"));
        const showSplit = cards.length > 1;

        cards.forEach((card, index) => {
            const splitInput = card.querySelector(".split-box");
            const trashButton = card.querySelector(".artist-delete-button");

            if (splitInput) {
                splitInput.style.display = showSplit ? "inline-flex" : "none";
            }

            if (trashButton) {
                trashButton.style.display = index === 0 ? "none" : "inline-flex";
            }
        });
    }

    function validateSplitTotals() {
        const visibleSplits = Array.from(document.querySelectorAll(".split-box"))
            .filter(input => input.style.display !== "none");

        if (visibleSplits.length === 0) return true;

        const total = visibleSplits.reduce((sum, input) => {
            const value = Number(input.value || 0);
            return sum + value;
        }, 0);

        return total === 100;
    }

    function buildArtistCard(initialData = {}, { isMain = false, collapsed = false } = {}) {
        artistCount += 1;

        const roleLabel = isMain ? "Main Artist" : `Featured Artist ${artistCount}`;
        const complete = artistLooksComplete(initialData);

        const card = document.createElement("div");
        card.className = `artist-card${collapsed ? " is-collapsed" : ""}`;
        card.dataset.isMain = isMain ? "true" : "false";
        card.dataset.saved = complete ? "true" : "false";

        card.innerHTML = `
            <div class="artist-card__header">
                <div class="artist-card__title-wrap">
                    <span class="artist-check ${complete ? "is-complete" : ""}">✓</span>
                    <div>
                        <div class="artist-summary-name">${escapeHtml(initialData.display_name || roleLabel)}</div>
                        <div class="artist-summary-role">${roleLabel}</div>
                    </div>
                </div>

                <div class="artist-card__actions">
                    <input class="split-box" type="number" min="0" max="100" step="1" value="${isMain ? "100" : "0"}" title="Split" style="display:none;" />
                    <button type="button" class="small-action-button artist-edit-button">Edit</button>
                    <button type="button" class="icon-button artist-delete-button" title="Delete">🗑</button>
                </div>
            </div>

            <div class="artist-card__body">
                <div class="artist-grid">
                    <label>
                        Artist Name
                        <input type="text" class="artist-display-name" value="${escapeHtml(initialData.display_name || "")}" />
                    </label>

                    <label>
                        Email
                        <input type="email" class="artist-email" value="${escapeHtml(initialData.email || "")}" />
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
                        <input type="text" class="artist-ipi" value="${escapeHtml(initialData.ipi || "")}" />
                    </label>

                    <label>
                        PRO
                        <input type="text" class="artist-pro" value="${escapeHtml(initialData.pro || "")}" />
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
                </div>

                <button type="button" class="save-pane-button artist-save-button">Save Changes</button>
            </div>
        `;

        const editButton = card.querySelector(".artist-edit-button");
        const deleteButton = card.querySelector(".artist-delete-button");
        const saveButton = card.querySelector(".artist-save-button");

        editButton.addEventListener("click", () => {
            card.classList.toggle("is-collapsed");
        });

        deleteButton.addEventListener("click", () => {
            if (card.dataset.isMain === "true") return;
            card.remove();
            updateSplitVisibility();
        });

        saveButton.addEventListener("click", () => {
            const data = collectArtistCard(card);
            const completeNow = artistLooksComplete(data);

            card.querySelector(".artist-summary-name").textContent = data.display_name || roleLabel;

            const check = card.querySelector(".artist-check");
            check.classList.toggle("is-complete", completeNow);

            card.dataset.saved = completeNow ? "true" : "false";
            card.classList.add("is-collapsed");
            updateSplitVisibility();
        });

        artistsContainer.appendChild(card);
        updateSplitVisibility();
    }

    function collectArtistCard(card) {
        return {
            role_type: card.dataset.isMain === "true" ? "main" : "featured",
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
            split_percent: Number(card.querySelector(".split-box")?.value || 0),
        };
    }

    function addCreditCard(container, type) {
        const card = document.createElement("div");
        card.className = "credit-card";

        card.innerHTML = `
            <div class="credit-grid">
                <label>
                    Artist Name
                    <input type="text" class="credit-artist-name" />
                </label>
                <label>
                    Email
                    <input type="email" class="credit-email" />
                </label>
                <label>
                    First Name
                    <input type="text" class="credit-first-name" />
                </label>
                <label>
                    Last Name
                    <input type="text" class="credit-last-name" />
                </label>
                <label>
                    IPI
                    <input type="text" class="credit-ipi" />
                </label>
                <label>
                    PRO
                    <input type="text" class="credit-pro" />
                </label>
                <label class="full-span">
                    Publisher
                    <input type="text" class="credit-publisher" />
                </label>
            </div>

            <div class="credit-tools">
                <button type="button" class="small-action-button remove-credit-button">Remove ${type}</button>
            </div>
        `;

        card.dataset.creditType = type.toLowerCase();

        card.querySelector(".remove-credit-button").addEventListener("click", () => {
            card.remove();
        });

        container.appendChild(card);
    }

    function buildTrackCard() {
        trackCount += 1;

        const card = document.createElement("div");
        card.className = "track-card";

        card.innerHTML = `
            <div class="track-card__header">
                <div class="track-card__title-wrap">
                    <div>
                        <div class="track-summary-name">Track ${trackCount}</div>
                    </div>
                </div>

                <div class="track-card__actions">
                    <button type="button" class="small-action-button track-toggle-button">Collapse</button>
                    <button type="button" class="icon-button track-delete-button" title="Delete">🗑</button>
                </div>
            </div>

            <div class="track-card__body">
                <div class="track-grid">
                    <label>
                        Track Number
                        <input type="number" class="track-number" min="1" value="${trackCount}" />
                    </label>

                    <label>
                        Track Name
                        <input type="text" class="track-title" />
                    </label>

                    <label>
                        Track Artist(s)
                        <input type="text" class="track-artists-text" />
                    </label>

                    <label>
                        Track Length
                        <input type="text" class="track-length" placeholder="03:42" />
                    </label>

                    <label>
                        Language
                        <input type="text" class="track-language" placeholder="English or Instrumental" />
                    </label>

                    <label>
                        Instrumental
                        <input type="checkbox" class="track-is-instrumental" />
                    </label>

                    <label class="full-span">
                        Lyrics
                        <textarea class="track-lyrics" rows="5"></textarea>
                    </label>

                    <label class="full-span">
                        Track Pitch
                        <textarea class="track-pitch" rows="4"></textarea>
                    </label>

                    <div class="upload-box full-span">
                        <label>
                            Audio Upload
                            <input type="file" class="track-audio-file" accept=".wav,.flac,.aac,audio/wav,audio/flac,audio/aac" />
                        </label>
                    </div>
                </div>

                <div class="track-tools">
                    <button type="button" class="small-action-button add-writer-button">+ Add Writer</button>
                    <button type="button" class="small-action-button add-producer-button">+ Add Producer</button>
                    <button type="button" class="small-action-button add-performer-button">+ Add Performer</button>
                    <button type="button" class="small-action-button add-composer-button">+ Add Composer</button>
                </div>

                <div class="credit-list"></div>
            </div>
        `;

        const toggleButton = card.querySelector(".track-toggle-button");
        const deleteButton = card.querySelector(".track-delete-button");
        const creditList = card.querySelector(".credit-list");

        const audioInput = card.querySelector(".track-audio-file");

        const audioStatus = document.createElement("div");
        audioStatus.className = "track-audio-status";
        audioStatus.style.marginTop = "0.55rem";
        audioStatus.style.color = "rgba(255,255,255,0.75)";

        const uploadBox = card.querySelector(".upload-box");
        if (uploadBox) {
            uploadBox.appendChild(audioStatus);
        }

        toggleButton.addEventListener("click", () => {
            const collapsed = card.classList.toggle("is-collapsed");
            toggleButton.textContent = collapsed ? "Expand" : "Collapse";
        });

        deleteButton.addEventListener("click", () => {
            card.remove();
        });

        card.querySelector(".add-writer-button").addEventListener("click", () => addCreditCard(creditList, "Writer"));
        card.querySelector(".add-producer-button").addEventListener("click", () => addCreditCard(creditList, "Producer"));
        card.querySelector(".add-performer-button").addEventListener("click", () => addCreditCard(creditList, "Performer"));
        card.querySelector(".add-composer-button").addEventListener("click", () => addCreditCard(creditList, "Composer"));

        audioInput?.addEventListener("change", async () => {
            clearMessages();

            const file = audioInput.files?.[0];
            if (!file) {
                card._uploadedAudio = null;
                audioStatus.textContent = "";
                return;
            }

            const mainArtistName =
                document.querySelector(".artist-card .artist-display-name")?.value?.trim() || "artist";

            const trackTitle =
                card.querySelector(".track-title")?.value?.trim() || `track_${trackCount}`;

            try {
                audioStatus.textContent = "Uploading audio...";
                const uploadedAudio = await uploadTrackAudio(file, mainArtistName, trackTitle);
                card._uploadedAudio = uploadedAudio;
                audioStatus.textContent = `Audio uploaded: ${uploadedAudio.original_filename}`;
            } catch (error) {
                card._uploadedAudio = null;
                audioStatus.textContent = "";
                errorBox.textContent = error.message || "Audio upload failed.";
            }
        });

        tracksContainer.appendChild(card);
    }

    function collectTracks() {
        return Array.from(document.querySelectorAll(".track-card")).map((card) => {
            const credits = Array.from(card.querySelectorAll(".credit-card")).map((creditCard, index) => ({
                credit_type: creditCard.dataset.creditType,
                credit_order: index + 1,
                artist_name: creditCard.querySelector(".credit-artist-name")?.value?.trim() || "",
                email: creditCard.querySelector(".credit-email")?.value?.trim() || "",
                first_name: creditCard.querySelector(".credit-first-name")?.value?.trim() || "",
                last_name: creditCard.querySelector(".credit-last-name")?.value?.trim() || "",
                ipi: creditCard.querySelector(".credit-ipi")?.value?.trim() || "",
                pro: creditCard.querySelector(".credit-pro")?.value?.trim() || "",
                publisher: creditCard.querySelector(".credit-publisher")?.value?.trim() || "",
            }));

            return {
                track_number: Number(card.querySelector(".track-number")?.value || 0),
                track_title: card.querySelector(".track-title")?.value?.trim() || "",
                track_artists_text: card.querySelector(".track-artists-text")?.value?.trim() || "",
                track_length: card.querySelector(".track-length")?.value?.trim() || "",
                language: card.querySelector(".track-language")?.value?.trim() || "",
                is_instrumental: card.querySelector(".track-is-instrumental")?.checked || false,
                lyrics: card.querySelector(".track-lyrics")?.value?.trim() || "",
                track_pitch: card.querySelector(".track-pitch")?.value?.trim() || "",
                audio: card._uploadedAudio || null,
                credits,
            };
        });
    }

    async function uploadArtwork() {
        if (!artworkInput?.files?.length) {
            uploadedArtwork = null;
            if (artworkStatus) artworkStatus.textContent = "";
            return;
        }

        const file = artworkInput.files[0];
        const releaseTitle = document.querySelector('[name="release_title"]')?.value?.trim() || "untitled_release";
        const mainArtistName =
            document.querySelector(".artist-card .artist-display-name")?.value?.trim() || "artist";

        const formData = new FormData();
        formData.append("artwork", file);
        formData.append("release_title", releaseTitle);
        formData.append("artist_name", mainArtistName);

        if (artworkStatus) {
            artworkStatus.textContent = "Uploading artwork...";
        }

        const response = await fetch(`${API_BASE}/api/releases/upload-artwork`, {
            method: "POST",
            body: formData,
            credentials: "include",
        });

        let data = {};
        try {
            data = await response.json();
        } catch (error) {
            data = {};
        }

        if (!response.ok) {
            throw new Error(data.error || "Artwork upload failed.");
        }

        uploadedArtwork = data.artwork;

        if (artworkStatus) {
            artworkStatus.textContent = `Artwork uploaded: ${uploadedArtwork.original_filename} (${uploadedArtwork.width}x${uploadedArtwork.height})`;
        }
    }

    async function uploadTrackAudio(file, artistName, trackTitle) {
        const formData = new FormData();
        formData.append("audio", file);
        formData.append("artist_name", artistName || "artist");
        formData.append("track_title", trackTitle || "track");

        const response = await fetch(`${API_BASE}/api/releases/upload-audio`, {
            method: "POST",
            body: formData,
            credentials: "include",
        });

        let data = {};
        try {
            data = await response.json();
        } catch (error) {
            data = {};
        }

        if (!response.ok) {
            throw new Error(data.error || "Audio upload failed.");
        }

        return data.audio;
    }

    async function loadMainArtist() {
        currentUser = await getCurrentUser();
        if (!currentUser) {
            window.location.href = "/";
            return;
        }

        if (currentUser.role === "artist") {
            const profileResponse = await apiFetch("/api/artists/me");
            const profile = profileResponse.artist || profileResponse.profile || profileResponse;
            mainArtistProfile = profile;

            const mainArtistData = {
                display_name: profile.artist_name || "",
                email: currentUser.email || "",
                first_name: profile.first_name || "",
                last_name: profile.last_name || "",
                ipi: profile.ipi || "",
                pro: profile.pro || "",
                publisher: profile.publisher || "",
                spotify_url: profile.spotify_url || "",
                apple_music_url: profile.apple_music_url || "",
                youtube_url: profile.youtube_channel_url || "",
                soundcloud_url: profile.soundcloud_url || "",
            };

            buildArtistCard(mainArtistData, { isMain: true, collapsed: true });

            if (artistContext) {
                artistContext.textContent = `Creating release for ${profile.artist_name || "your artist profile"}`;
            }
        } else {
            buildArtistCard({}, { isMain: true, collapsed: false });

            if (artistContext) {
                artistContext.textContent = "Creating new release";
            }
        }
    }

    artworkInput?.addEventListener("change", async () => {
        clearMessages();
        try {
            await uploadArtwork();
        } catch (error) {
            uploadedArtwork = null;
            if (artworkStatus) {
                artworkStatus.textContent = "";
            }
            if (errorBox) {
                errorBox.textContent = error.message || "Artwork upload failed.";
            }
        }
    });

    addArtistButton?.addEventListener("click", () => {
        clearMessages();

        const currentCards = document.querySelectorAll(".artist-card").length;
        if (currentCards >= 5) {
            errorBox.textContent = "You can add up to 5 artists for now.";
            return;
        }

        buildArtistCard({}, { isMain: false, collapsed: false });
    });

    addTrackButton?.addEventListener("click", () => {
        clearMessages();
        buildTrackCard();
    });

    form?.addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessages();

        const formData = new FormData(form);
        const artists = Array.from(document.querySelectorAll(".artist-card")).map(collectArtistCard);
        const tracks = collectTracks();
        const missingTrackAudio = tracks.find(
            (track) => !track.audio?.object_key
        );

        if (missingTrackAudio) {
            errorBox.textContent = "Every track must have an uploaded audio file.";
            return;
        }

        if (!validateSplitTotals()) {
            errorBox.textContent = "Artist splits must add up to 100.";
            return;

        }

        if (!uploadedArtwork?.object_key) {
            errorBox.textContent = "Release artwork is required.";
            return;
        }

        const payload = {
            release_title: formData.get("release_title")?.trim(),
            release_type: formData.get("release_type")?.trim(),
            preferred_release_date: formData.get("preferred_release_date")?.trim(),
            primary_genre: formData.get("primary_genre")?.trim(),
            other_genres: formData.get("other_genres")?.trim(),
            release_pitch: formData.get("release_pitch")?.trim(),
            artwork: uploadedArtwork,
            artists,
            tracks,
        };


        try {
            const data = await apiFetch("/api/releases", {
                method: "POST",
                body: payload,
            });

            successBox.textContent = "Release draft created successfully.";

            if (data.release?.id) {
                window.location.href = `/releases/edit?submission=${data.release.id}`;
            }
        } catch (error) {
            errorBox.textContent = error.message || "Failed to create release draft.";
        }
    });

    try {
        await loadMainArtist();
        buildTrackCard();
    } catch (error) {
        if (errorBox) {
            errorBox.textContent = error.message || "Failed to load release form.";
        }
    }
});