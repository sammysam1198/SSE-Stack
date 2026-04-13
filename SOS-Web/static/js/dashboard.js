function requireRole(user, allowedRoles = []) {
    if (!user) {
        window.location.href = "/";
        return false;
    }

    if (user.role === "developer") return true;

    if (!allowedRoles.includes(user.role)) {
        window.location.href = "/";
        return false;
    }

    return true;
}

function setText(id, value, fallback = "") {
    const el = document.getElementById(id);
    if (el) el.textContent = value || fallback;
}

function setHeroImage(imageUrl) {
    const hero = document.getElementById("dashboard-hero");
    if (!hero) return;

    if (imageUrl) {
        hero.style.setProperty("--hero-image", `url('${imageUrl}')`);
    } else {
        hero.style.setProperty(
            "--hero-image",
            "radial-gradient(circle at top left, rgba(255,0,170,0.18), transparent 30%), radial-gradient(circle at bottom right, rgba(0,200,255,0.14), transparent 35%), linear-gradient(135deg, #08101d, #0c0f18)"
        );
    }
}

async function getMyArtistProfile() {
    const data = await apiFetch("/api/artists/me");
    return data.artist_profile;
}

async function saveMyArtistProfile(payload) {
    const data = await apiFetch("/api/artists/me", {
        method: "PATCH",
        body: payload
    });
    return data.artist_profile;
}

function collectArtistProfilePayload() {
    const artistNameInput = document.getElementById("artist-name-input");
    const taglineInput = document.getElementById("artist-tagline-input");
    const bioInput = document.getElementById("artist-bio-input");

    const tag1Input = document.getElementById("artist-tag-1-input");
    const tag2Input = document.getElementById("artist-tag-2-input");
    const tag3Input = document.getElementById("artist-tag-3-input");

    const spotifyInput = document.getElementById("artist-spotify-input");
    const youtubeInput = document.getElementById("artist-youtube-input");
    const instagramInput = document.getElementById("artist-instagram-input");
    const soundcloudInput = document.getElementById("artist-soundcloud-input");
    const appleMusicInput = document.getElementById("artist-apple-music-input");

    const locationInput = document.getElementById("artist-location-input");
    const profileImageInput = document.getElementById("artist-profile-image-input");

    return {
        artist_name: artistNameInput?.value.trim() || "",
        tagline: taglineInput?.value.trim() || "",
        bio: bioInput?.value.trim() || "",
        primary_genre: tag1Input?.value.trim() || "",
        primary_instrument: tag2Input?.value.trim() || "",
        primary_vibe: tag3Input?.value.trim() || "",
        spotify_url: spotifyInput?.value.trim() || "",
        youtube_url: youtubeInput?.value.trim() || "",
        instagram_url: instagramInput?.value.trim() || "",
        soundcloud_url: soundcloudInput?.value.trim() || "",
        apple_music_url: appleMusicInput?.value.trim() || "",
        location: locationInput?.value.trim() || "",
        profile_image_url: profileImageInput?.value.trim() || ""
    };
}

function populateArtistDashboard(profile) {
    if (!profile) return;

    setText("artist-display-name", profile.artist_name || "Artist", "Artist");
    setHeroImage(profile.profile_image_url || "");

    const avatar = document.getElementById("artist-profile-avatar");
    if (avatar && profile.profile_image_url) {
        avatar.src = profile.profile_image_url;
    }

    const artistNameInput = document.getElementById("artist-name-input");
    const taglineInput = document.getElementById("artist-tagline-input");
    const bioInput = document.getElementById("artist-bio-input");

    const tag1Input = document.getElementById("artist-tag-1-input");
    const tag2Input = document.getElementById("artist-tag-2-input");
    const tag3Input = document.getElementById("artist-tag-3-input");

    const spotifyInput = document.getElementById("artist-spotify-input");
    const youtubeInput = document.getElementById("artist-youtube-input");
    const instagramInput = document.getElementById("artist-instagram-input");
    const soundcloudInput = document.getElementById("artist-soundcloud-input");
    const appleMusicInput = document.getElementById("artist-apple-music-input");
    const locationInput = document.getElementById("artist-location-input");
    const profileImageInput = document.getElementById("artist-profile-image-input");

    if (artistNameInput) artistNameInput.value = profile.artist_name || "";
    if (taglineInput) taglineInput.value = profile.tagline || "";
    if (bioInput) bioInput.value = profile.bio || "";

    if (tag1Input) tag1Input.value = profile.primary_genre || "";
    if (tag2Input) tag2Input.value = profile.primary_instrument || "";
    if (tag3Input) tag3Input.value = profile.primary_vibe || "";

    if (spotifyInput) spotifyInput.value = profile.spotify_url || "";
    if (youtubeInput) youtubeInput.value = profile.youtube_url || "";
    if (instagramInput) instagramInput.value = profile.instagram_url || "";
    if (soundcloudInput) soundcloudInput.value = profile.soundcloud_url || "";
    if (appleMusicInput) appleMusicInput.value = profile.apple_music_url || "";

    if (locationInput) locationInput.value = profile.location || "";
    if (profileImageInput) profileImageInput.value = profile.profile_image_url || "";

    updateArtistPageStatus(profile);
}

function updateArtistPageStatus(profile) {
    const rows = document.querySelectorAll(".page-status-row");
    if (!rows.length || !profile) return;

    const values = [
        profile.bio ? "Added" : "Missing",
        profile.profile_image_url ? "Added" : "Missing",
        profile.location ? "Added" : "Missing",
        [
            profile.primary_genre,
            profile.primary_instrument,
            profile.primary_vibe
        ].filter(Boolean).length + " Added",
        profile.spotify_url ? "Linked" : "Not Linked",
        profile.youtube_url ? "Linked" : "Not Linked"
    ];

    rows.forEach((row, index) => {
        const spans = row.querySelectorAll("span");
        if (spans.length >= 2 && values[index] !== undefined) {
            spans[1].textContent = values[index];
        }
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    const artistForm = document.getElementById("artist-profile-form");
    const saveButton = document.getElementById("artist-profile-save");
    const saveStatus = document.getElementById("artist-profile-save-status");

    if (!artistForm) return;

    try {
        const user = await getCurrentUser();
        if (!requireRole(user, ["artist"])) return;

        const profile = await getMyArtistProfile();
        populateArtistDashboard(profile || {});
    } catch (error) {
        console.error("Failed to load artist dashboard profile:", error);
        if (saveStatus) {
            saveStatus.textContent = "Could not load your artist profile.";
        }
    }

    artistForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (saveStatus) saveStatus.textContent = "";
        if (saveButton) saveButton.disabled = true;

        try {
            const payload = collectArtistProfilePayload();
            const updatedProfile = await saveMyArtistProfile(payload);
            populateArtistDashboard(updatedProfile || payload);

            if (saveStatus) {
                saveStatus.textContent = "Profile saved successfully.";
            }
        } catch (error) {
            console.error("Failed to save artist profile:", error);
            if (saveStatus) {
                saveStatus.textContent = error.message || "Could not save profile.";
            }
        } finally {
            if (saveButton) saveButton.disabled = false;
        }
    });
});