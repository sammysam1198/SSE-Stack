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
    if (el) {
        el.textContent = value || fallback;
    }
}

function resolveAssetUrl(value) {
    const raw = (value || "").trim();
    if (!raw) return "";

    if (/^https?:\/\//i.test(raw) || raw.startsWith("/")) {
        return raw;
    }

    const base = (window.SSE_ASSET_BASE_URL || "").trim();
    if (!base) return "";

    return `${base.replace(/\/+$/, "")}/${raw.replace(/^\/+/, "")}`;
}

function setHeroImageFromProfile(profile) {
    const hero = document.getElementById("dashboard-hero");
    if (!hero) return;

    const bannerUrl = resolveAssetUrl(profile.dashboard_banner_key);
    if (bannerUrl) {
        hero.style.setProperty("--hero-image", `url("${bannerUrl}")`);
        return;
    }

    hero.style.setProperty(
        "--hero-image",
        "radial-gradient(circle at top left, rgba(255,0,170,0.18), transparent 30%), radial-gradient(circle at bottom right, rgba(0,200,255,0.14), transparent 35%), linear-gradient(135deg, #08101d, #0c0f18)"
    );
}

function setAvatarFromProfile(profile) {
    const avatar = document.getElementById("artist-profile-avatar");
    if (!avatar) return;

    const portraitUrl = resolveAssetUrl(profile.profile_portrait_key);
    const logoUrl = resolveAssetUrl(profile.artist_logo_key);

    avatar.src = portraitUrl || logoUrl || "/static/logos/sse.png";
}

function setImagePreview(imgId, keyValue, fallbackSrc = "") {
    const img = document.getElementById(imgId);
    if (!img) return;

    const resolved = resolveAssetUrl(keyValue);
    img.src = resolved || fallbackSrc;
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

async function uploadArtistAsset(assetType, file) {
    const formData = new FormData();
    formData.append("asset_type", assetType);
    formData.append("file", file);

    const response = await fetch(`${API_BASE}/api/artists/me/upload-asset`, {
        method: "POST",
        body: formData,
        credentials: "include"
    });

    let data = {};
    try {
        data = await response.json();
    } catch (error) {
        data = {};
    }

    if (!response.ok) {
        throw new Error(data.error || `Failed to upload ${assetType}.`);
    }

    return data;
}

function collectArtistProfilePayload() {
    return {
        artist_name: document.getElementById("artist-name-input")?.value.trim() || "",
        tagline: document.getElementById("artist-tagline-input")?.value.trim() || "",
        bio: document.getElementById("artist-bio-input")?.value.trim() || "",
        first_name: document.getElementById("artist-first-name-input")?.value.trim() || "",
        last_name: document.getElementById("artist-last-name-input")?.value.trim() || "",
        publisher: document.getElementById("artist-publisher-input")?.value.trim() || "",
        location: document.getElementById("artist-location-input")?.value.trim() || "",

        primary_genre: document.getElementById("artist-primary-genre-input")?.value.trim() || "",
        genre2: document.getElementById("artist-genre-2-input")?.value.trim() || "",
        genre3: document.getElementById("artist-genre-3-input")?.value.trim() || "",

        primary_instrument: document.getElementById("artist-primary-role-input")?.value.trim() || "",
        role2: document.getElementById("artist-role-2-input")?.value.trim() || "",
        role3: document.getElementById("artist-role-3-input")?.value.trim() || "",

        primary_vibe: document.getElementById("artist-vibe-input")?.value.trim() || "",

        spotify_embed: document.getElementById("artist-spotify-embed-input")?.value.trim() || "",
        featured_video_embed: document.getElementById("artist-featured-video-embed-input")?.value.trim() || "",
        featured_video_name: document.getElementById("artist-featured-video-name-input")?.value.trim() || "",
        video2_embed: document.getElementById("artist-video-2-embed-input")?.value.trim() || "",
        video2_name: document.getElementById("artist-video-2-name-input")?.value.trim() || "",
        video3_embed: document.getElementById("artist-video-3-embed-input")?.value.trim() || "",
        video3_name: document.getElementById("artist-video-3-name-input")?.value.trim() || "",

        spotify_url: document.getElementById("artist-spotify-input")?.value.trim() || "",
        apple_music_url: document.getElementById("artist-apple-music-input")?.value.trim() || "",
        youtube_music_url: document.getElementById("artist-youtube-music-input")?.value.trim() || "",
        youtube_channel_url: document.getElementById("artist-youtube-channel-input")?.value.trim() || "",
        tidal_url: document.getElementById("artist-tidal-input")?.value.trim() || "",
        threads_url: document.getElementById("artist-threads-input")?.value.trim() || "",
        instagram_url: document.getElementById("artist-instagram-input")?.value.trim() || "",
        soundcloud_url: document.getElementById("artist-soundcloud-input")?.value.trim() || "",
        bandcamp_url: document.getElementById("artist-bandcamp-input")?.value.trim() || "",
        tiktok_url: document.getElementById("artist-tiktok-input")?.value.trim() || "",
        twitter_url: document.getElementById("artist-twitter-input")?.value.trim() || "",
        deezer_url: document.getElementById("artist-deezer-input")?.value.trim() || "",
        beatport_url: document.getElementById("artist-beatport-input")?.value.trim() || "",
        amazon_music_url: document.getElementById("artist-amazon-music-input")?.value.trim() || "",
        facebook_url: document.getElementById("artist-facebook-input")?.value.trim() || "",

        dashboard_banner_key: document.getElementById("artist-banner-key-input")?.value.trim() || "",
        artist_logo_key: document.getElementById("artist-logo-key-input")?.value.trim() || "",
        profile_portrait_key: document.getElementById("artist-portrait-key-input")?.value.trim() || ""
    };
}

function populateArtistDashboard(profile) {
    if (!profile) return;

    setText("artist-display-name", profile.artist_name || "Artist", "Artist");
    setHeroImageFromProfile(profile);
    setAvatarFromProfile(profile);

    const setValue = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.value = value || "";
    };

    setValue("artist-name-input", profile.artist_name);
    setValue("artist-tagline-input", profile.tagline);
    setValue("artist-bio-input", profile.bio);
    setValue("artist-first-name-input", profile.first_name);
    setValue("artist-last-name-input", profile.last_name);
    setValue("artist-publisher-input", profile.publisher);
    setValue("artist-location-input", profile.location);

    setValue("artist-primary-genre-input", profile.primary_genre);
    setValue("artist-genre-2-input", profile.genre2);
    setValue("artist-genre-3-input", profile.genre3);

    setValue("artist-primary-role-input", profile.primary_instrument);
    setValue("artist-role-2-input", profile.role2);
    setValue("artist-role-3-input", profile.role3);

    setValue("artist-vibe-input", profile.primary_vibe);

    setValue("artist-spotify-embed-input", profile.spotify_embed);
    setValue("artist-featured-video-embed-input", profile.featured_video_embed);
    setValue("artist-featured-video-name-input", profile.featured_video_name);
    setValue("artist-video-2-embed-input", profile.video2_embed);
    setValue("artist-video-2-name-input", profile.video2_name);
    setValue("artist-video-3-embed-input", profile.video3_embed);
    setValue("artist-video-3-name-input", profile.video3_name);

    setValue("artist-spotify-input", profile.spotify_url);
    setValue("artist-apple-music-input", profile.apple_music_url);
    setValue("artist-youtube-music-input", profile.youtube_music_url);
    setValue("artist-youtube-channel-input", profile.youtube_channel_url);
    setValue("artist-tidal-input", profile.tidal_url);
    setValue("artist-threads-input", profile.threads_url);
    setValue("artist-instagram-input", profile.instagram_url);
    setValue("artist-soundcloud-input", profile.soundcloud_url);
    setValue("artist-bandcamp-input", profile.bandcamp_url);
    setValue("artist-tiktok-input", profile.tiktok_url);
    setValue("artist-twitter-input", profile.twitter_url);
    setValue("artist-deezer-input", profile.deezer_url);
    setValue("artist-beatport-input", profile.beatport_url);
    setValue("artist-amazon-music-input", profile.amazon_music_url);
    setValue("artist-facebook-input", profile.facebook_url);

    setValue("artist-banner-key-input", profile.dashboard_banner_key);
    setValue("artist-logo-key-input", profile.artist_logo_key);
    setValue("artist-portrait-key-input", profile.profile_portrait_key);

    setImagePreview("artist-banner-preview", profile.dashboard_banner_key, "/static/logos/sse.png");
    setImagePreview("artist-logo-preview", profile.artist_logo_key, "/static/logos/sse.png");
    setImagePreview("artist-portrait-preview", profile.profile_portrait_key, "/static/logos/sse.png");

    updateArtistPageStatus(profile);
}

function updateArtistPageStatus(profile) {
    const rows = document.querySelectorAll(".page-status-row");
    if (!rows.length || !profile) return;

    const tagCount = [
        profile.primary_genre,
        profile.genre2,
        profile.genre3,
        profile.primary_instrument,
        profile.role2,
        profile.role3,
        profile.primary_vibe
    ].filter(Boolean).length;

    const linkCount = [
        profile.spotify_url,
        profile.apple_music_url,
        profile.youtube_music_url,
        profile.youtube_channel_url,
        profile.tidal_url,
        profile.threads_url,
        profile.instagram_url,
        profile.soundcloud_url,
        profile.bandcamp_url,
        profile.tiktok_url,
        profile.twitter_url,
        profile.deezer_url,
        profile.beatport_url,
        profile.amazon_music_url,
        profile.facebook_url
    ].filter(Boolean).length;

    const values = [
        profile.bio ? "Added" : "Missing",
        profile.profile_portrait_key ? "Added" : "Missing",
        profile.location ? "Added" : "Missing",
        `${tagCount} Added`,
        `${linkCount} Linked`
    ];

    rows.forEach((row, index) => {
        const spans = row.querySelectorAll("span");
        if (spans.length >= 2 && values[index] !== undefined) {
            spans[1].textContent = values[index];
        }
    });
}

function bindProfileMenu() {
    const signoutButton = document.getElementById("artist-signout-button");
    const profileTrigger = document.getElementById("artist-profile-trigger");
    const profileDropdown = document.getElementById("artist-profile-dropdown");

    if (profileTrigger && profileDropdown) {
        profileTrigger.addEventListener("click", () => {
            const isOpen = profileDropdown.classList.toggle("is-open");
            profileTrigger.setAttribute("aria-expanded", String(isOpen));
        });

        document.addEventListener("click", (event) => {
            const menu = document.getElementById("artist-profile-menu");
            if (menu && !menu.contains(event.target)) {
                profileDropdown.classList.remove("is-open");
                profileTrigger.setAttribute("aria-expanded", "false");
            }
        });
    }

    if (signoutButton) {
        signoutButton.addEventListener("click", async () => {
            try {
                await signout();
            } catch (error) {
                console.error("Sign out failed:", error);
            }
            window.location.href = "/";
        });
    }
}

function bindPreviewButton() {
    const previewButton = document.getElementById("artist-preview-button");
    const statusEl = document.getElementById("artist-editor-status");

    if (!previewButton) return;

    previewButton.addEventListener("click", () => {
        const payload = collectArtistProfilePayload();

        setText("artist-display-name", payload.artist_name || "Artist", "Artist");
        setHeroImageFromProfile(payload);
        setAvatarFromProfile(payload);

        setImagePreview("artist-banner-preview", payload.dashboard_banner_key, "/static/logos/sse.png");
        setImagePreview("artist-logo-preview", payload.artist_logo_key, "/static/logos/sse.png");
        setImagePreview("artist-portrait-preview", payload.profile_portrait_key, "/static/logos/sse.png");

        updateArtistPageStatus(payload);

        if (statusEl) {
            statusEl.textContent = "Preview updated.";
        }
    });
}

function bindLocalFilePreviews() {
    const bindings = [
        { inputId: "artist-banner-file-input", previewId: "artist-banner-preview" },
        { inputId: "artist-logo-file-input", previewId: "artist-logo-preview" },
        { inputId: "artist-portrait-file-input", previewId: "artist-portrait-preview" }
    ];

    bindings.forEach(({ inputId, previewId }) => {
        const input = document.getElementById(inputId);
        const preview = document.getElementById(previewId);

        if (!input || !preview) return;

        input.addEventListener("change", () => {
            const file = input.files?.[0];
            if (!file) return;

            const objectUrl = URL.createObjectURL(file);
            preview.src = objectUrl;
        });
    });
}

async function handleAssetUploads(statusEl) {
    const uploads = [
        {
            assetType: "banner",
            inputId: "artist-banner-file-input",
            hiddenFieldId: "artist-banner-key-input"
        },
        {
            assetType: "logo",
            inputId: "artist-logo-file-input",
            hiddenFieldId: "artist-logo-key-input"
        },
        {
            assetType: "portrait",
            inputId: "artist-portrait-file-input",
            hiddenFieldId: "artist-portrait-key-input"
        }
    ];

    for (const item of uploads) {
        const input = document.getElementById(item.inputId);
        const hiddenField = document.getElementById(item.hiddenFieldId);
        const file = input?.files?.[0];

        if (!file) continue;

        if (statusEl) {
            statusEl.textContent = `Uploading ${item.assetType}...`;
        }

        const result = await uploadArtistAsset(item.assetType, file);

        if (hiddenField) {
            hiddenField.value = result.object_key || result.asset_key || result.key || "";
        }
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("artist-editor-form");
    const statusEl = document.getElementById("artist-editor-status");
    const saveButton = document.getElementById("artist-profile-save");

    if (!form) return;

    try {
        const user = await getCurrentUser();
        if (!requireRole(user, ["artist"])) return;

        bindProfileMenu();
        bindPreviewButton();
        bindLocalFilePreviews();

        const profile = await getMyArtistProfile();
        populateArtistDashboard(profile || {});
    } catch (error) {
        console.error("Failed to load artist dashboard profile:", error);
        if (statusEl) {
            statusEl.textContent = "Could not load your artist profile.";
        }
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (statusEl) statusEl.textContent = "";
        if (saveButton) saveButton.disabled = true;

        try {
            await handleAssetUploads(statusEl);

            if (statusEl) {
                statusEl.textContent = "Saving profile...";
            }

            const payload = collectArtistProfilePayload();
            const updatedProfile = await saveMyArtistProfile(payload);

            populateArtistDashboard(updatedProfile || payload);

            if (statusEl) {
                statusEl.textContent = "Profile saved successfully.";
            }
        } catch (error) {
            console.error("Failed to save artist profile:", error);
            if (statusEl) {
                statusEl.textContent = error.message || "Could not save profile.";
            }
        } finally {
            if (saveButton) saveButton.disabled = false;
        }
    });
});