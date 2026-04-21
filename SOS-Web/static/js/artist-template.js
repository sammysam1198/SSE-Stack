const ARTIST_PAGE_DEFAULTS = {
    name: "Unknown Artist",
    tagline: "No tagline yet.",
    bio: "No bio yet.",
    location: "Not listed",
    vibe: "Not listed",
    primaryGenre: "Not listed",
    primaryRole: "Not listed",
    publisher: "Not listed"
};

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

function getArtistSlugFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const querySlug = params.get("slug");
    if (querySlug) return querySlug.trim().toLowerCase();

    const parts = window.location.pathname.split("/").filter(Boolean);
    const last = parts[parts.length - 1] || "";

    if (!last || last === "artist" || last === "artist.html") {
        return "";
    }

    return last.replace(/\.html$/i, "").trim().toLowerCase();
}

async function fetchArtistProfileBySlug(slug) {
    const data = await apiFetch(`/api/artists/slug/${encodeURIComponent(slug)}`);
    return data.artist_profile;
}

function setText(id, value, fallback = "—") {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = value || fallback;
    }
}

function setImage(id, src, fallback = "/static/logos/sse.png", alt = "") {
    const el = document.getElementById(id);
    if (!el) return;
    el.src = src || fallback;
    if (alt) el.alt = alt;
}

function buildTagPills(profile) {
    const row = document.getElementById("artistTagRow");
    if (!row) return;

    row.innerHTML = "";

    const values = [
        profile.primary_genre,
        profile.genre2,
        profile.genre3,
        profile.primary_instrument,
        profile.role2,
        profile.role3,
        profile.primary_vibe
    ].filter(Boolean);

    const unique = [...new Set(values.map((value) => value.trim()).filter(Boolean))].slice(0, 6);

    if (!unique.length) return;

    unique.forEach((value) => {
        const pill = document.createElement("span");
        pill.className = "artist-pill";
        pill.textContent = value;
        row.appendChild(pill);
    });
}

function setEmbed(containerId, rawEmbedHtml) {
    const wrap = document.getElementById(containerId);
    if (!wrap) return;

    const html = (rawEmbedHtml || "").trim();
    if (!html) {
        wrap.classList.add("embed-wrap--empty");
        wrap.innerHTML = `<p class="embed-empty">Nothing here yet.</p>`;
        return;
    }

    wrap.classList.remove("embed-wrap--empty");
    wrap.innerHTML = html;
}

function buildLinks(profile) {
    const linksRoot = document.getElementById("artistLinks");
    if (!linksRoot) return;

    linksRoot.innerHTML = "";

    const linkDefs = [
        ["Spotify", profile.spotify_url],
        ["Apple Music", profile.apple_music_url],
        ["YouTube Music", profile.youtube_music_url],
        ["YouTube Channel", profile.youtube_channel_url],
        ["Instagram", profile.instagram_url],
        ["Threads", profile.threads_url],
        ["SoundCloud", profile.soundcloud_url],
        ["Bandcamp", profile.bandcamp_url],
        ["Tidal", profile.tidal_url],
        ["TikTok", profile.tiktok_url],
        ["Twitter", profile.twitter_url],
        ["Deezer", profile.deezer_url],
        ["Beatport", profile.beatport_url],
        ["Amazon Music", profile.amazon_music_url],
        ["Facebook", profile.facebook_url]
    ].filter(([, url]) => !!(url || "").trim());

    if (!linkDefs.length) {
        linksRoot.innerHTML = `<p class="artist-copy">No links added yet.</p>`;
        return;
    }

    linkDefs.forEach(([label, url]) => {
        const tile = document.createElement("a");
        tile.className = "artist-link-tile";
        tile.href = url;
        tile.target = "_blank";
        tile.rel = "noopener noreferrer";

        tile.innerHTML = `
            <span class="artist-link-tile__label">${label}</span>
            <span class="artist-link-tile__value">${url}</span>
        `;

        linksRoot.appendChild(tile);
    });
}

function applyArtistProfile(profile) {
    const bannerUrl = resolveAssetUrl(profile.dashboard_banner_key);
    const portraitUrl = resolveAssetUrl(profile.profile_portrait_key);
    const logoUrl = resolveAssetUrl(profile.artist_logo_key);

    const hero = document.getElementById("artist-hero");
    if (hero && bannerUrl) {
        hero.style.setProperty("--artist-banner-image", `url("${bannerUrl}")`);
    }

    document.title = `${profile.artist_name || ARTIST_PAGE_DEFAULTS.name} | SpacedOut Studios`;

    setText("artistName", profile.artist_name, ARTIST_PAGE_DEFAULTS.name);
    setText("artistTagline", profile.tagline, ARTIST_PAGE_DEFAULTS.tagline);
    setText("artistBio", profile.bio, ARTIST_PAGE_DEFAULTS.bio);
    setText("artistLocation", profile.location, ARTIST_PAGE_DEFAULTS.location);
    setText("artistVibe", profile.primary_vibe, ARTIST_PAGE_DEFAULTS.vibe);
    setText("artistPrimaryGenre", profile.primary_genre, ARTIST_PAGE_DEFAULTS.primaryGenre);
    setText("artistPrimaryRole", profile.primary_instrument, ARTIST_PAGE_DEFAULTS.primaryRole);
    setText("artistPublisher", profile.publisher, ARTIST_PAGE_DEFAULTS.publisher);
    setText("artistSlug", profile.artist_page, "—");

    setImage(
        "artistPortrait",
        portraitUrl || logoUrl,
        "/static/logos/sse.png",
        `${profile.artist_name || "Artist"} portrait`
    );

    setImage(
        "artistLogo",
        logoUrl || portraitUrl,
        "/static/logos/sse.png",
        `${profile.artist_name || "Artist"} logo`
    );

    setEmbed("spotifyEmbedWrap", profile.spotify_embed);
    setEmbed("featuredVideoWrap", profile.featured_video_embed);
    setEmbed("video2Wrap", profile.video2_embed);
    setEmbed("video3Wrap", profile.video3_embed);

    setText("video2Title", profile.video2_name || "Video 2", "Video 2");
    setText("video3Title", profile.video3_name || "Video 3", "Video 3");

    buildTagPills(profile);
    buildLinks(profile);
}

function showArtistError(message) {
    const card = document.getElementById("artistErrorCard");
    const text = document.getElementById("artistErrorText");
    const name = document.getElementById("artistName");

    if (name) name.textContent = "Artist not found";
    if (card) card.hidden = false;
    if (text) text.textContent = message || "We could not load this artist page.";
}

document.addEventListener("DOMContentLoaded", async () => {
    const slug = getArtistSlugFromUrl();

    if (!slug) {
        showArtistError("No artist slug was found in the URL.");
        return;
    }

    try {
        const profile = await fetchArtistProfileBySlug(slug);
        applyArtistProfile(profile);
    } catch (error) {
        console.error("Failed to load artist profile:", error);
        showArtistError(error.message || "Failed to load artist.");
    }
});