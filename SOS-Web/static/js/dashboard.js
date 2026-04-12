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

function populateArtistDashboard(profile) {
    setText("artist-display-name", profile.artist_name || "Artist", "Artist");
    setHeroImage(profile.hero_image_url || "");

    const avatar = document.getElementById("artist-profile-avatar");
    if (avatar && profile.portrait_image_url) {
        avatar.src = profile.portrait_image_url;
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

    if (taglineInput) taglineInput.value = profile.tagline || "";
    if (tag1Input) tag1Input.value = profile.primary_genre || "";
    if (tag2Input) tag2Input.value = profile.primary_instrument || "";
    if (tag3Input) tag3Input.value = profile.primary_vibe || "";
    if (publisherInput) publisherInput.value = profile.publisher || "";
    if (locationInput) locationInput.value = profile.location || "";
    if (soundcloudInput) soundcloudInput.value = profile.soundcloud_url || "";

    updateArtistPageStatus(profile);
}

function updateArtistPageStatus(profile) {
    const rows = document.querySelectorAll(".page-status-row");
    if (!rows.length) return;

    const values = [
        profile.bio ? "Added" : "Missing",
        profile.hero_image_url ? "Added" : "Missing",
        profile.portrait_image_url ? "Added" : "Missing",
        [profile.tag_1, profile.tag_2, profile.tag_3].filter(Boolean).length + " Added",
        profile.spotify_url ? "Linked" : "Not Linked",
        profile.youtube_url ? "Linked" : "Not Linked",
    ];

    rows.forEach((row, index) => {
        const spans = row.querySelectorAll("span");
        if (spans.length >= 2 && values[index] !== undefined) {
            spans[1].textContent = values[index];
        }
    });
}