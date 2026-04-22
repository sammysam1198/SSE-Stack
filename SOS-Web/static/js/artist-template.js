
window.SSE_ASSET_BASE_URL = "https://pub-4d4f2d565e844d6fb3e84f51d1093198.r2.dev";

function getArtistSlugFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const slugFromQuery = params.get("slug");
    if (slugFromQuery) return slugFromQuery.trim().toLowerCase();

    const parts = window.location.pathname.split("/").filter(Boolean);
    const last = parts[parts.length - 1] || "";
    if (!last || last === "artist" || last === "artist.html") return "";
    return last.replace(/\.html$/i, "").trim().toLowerCase();
}

function resolveAssetUrl(value) {
    const raw = (value || "").trim();
    if (!raw) return "";

    // already full URL
    if (raw.startsWith("http")) return raw;

    // local fallback
    if (raw.startsWith("/static")) return raw;

    // R2 object key
    return `${window.SSE_ASSET_BASE_URL}/${raw}`;
}

function setText(id, value, fallback = "—") {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = (value || "").trim() || fallback;
}

function setHtml(id, html, fallbackHtml = '<p class="section-copy">Nothing here yet.</p>') {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = (html || "").trim() || fallbackHtml;
}

function setImage(id, src, fallback, altText) {
    const el = document.getElementById(id);
    if (!el) return;
    el.src = src || fallback;
    el.alt = altText || "Artist image";
}

function setLinkTile(id, url) {
    const el = document.getElementById(id);
    if (!el) return;

    if ((url || "").trim()) {
        el.href = url.trim();
        el.hidden = false;
    } else {
        el.hidden = true;
    }
}

function setOfficialWebsite(profile) {
    const button = document.getElementById("officialWebsiteButton");
    if (!button) return;

    const url = (profile.website_url || "").trim();
    if (url) {
        button.href = url;
        button.hidden = false;
    } else {
        button.hidden = true;
    }
}

function buildGenreLine(profile) {
    return [
        profile.primary_genre,
        profile.genre2,
        profile.genre3
    ].filter(Boolean).join(", ") || "—";
}

function buildRoleLine(profile) {
    return [
        profile.primary_instrument,
        profile.role2,
        profile.role3
    ].filter(Boolean).join(", ") || "—";
}

function buildTagline(profile) {
    const pieces = [
        profile.primary_genre,
        profile.genre2,
        profile.genre3
    ].filter(Boolean);

    if (pieces.length) {
        return pieces.join(" / ");
    }

    return profile.tagline || "Artist";
}

function setBioParagraphs(profile) {
    const wrap = document.getElementById("artistBioWrap");
    if (!wrap) return;

    const rawBio = (profile.bio || "").trim();
    if (!rawBio) {
        wrap.innerHTML = '<p class="section-copy">No bio yet.</p>';
        return;
    }

    const parts = rawBio
        .split(/\n{2,}/)
        .map((part) => part.trim())
        .filter(Boolean);

    if (!parts.length) {
        wrap.innerHTML = `<p class="section-copy">${rawBio}</p>`;
        return;
    }

    wrap.innerHTML = parts
        .map((part) => `<p class="section-copy">${part}</p>`)
        .join("");
}

function applyArtistProfile(profile) {
    const artistName = (profile.artist_name || "Artist").trim();
    const portraitUrl = resolveAssetUrl(profile.profile_portrait_key);
    const logoUrl = resolveAssetUrl(profile.artist_logo_key);
    const displayImage = portraitUrl || logoUrl || "/static/logos/sse.png";

    document.title = `${artistName} | SpacedOut Studios`;

    const pageDescription = document.getElementById("pageDescription");
    if (pageDescription) {
        pageDescription.content = `${artistName} on SpacedOut Studios. ${buildGenreLine(profile)}.`.trim();
    }

    const aboutVisual = logoUrl || portraitUrl || "/static/logos/sse.png";

    setImage(
        "artistLogoImage",
        aboutVisual,
        "/static/logos/sse.png",
        `${artistName} logo`
    );

    setText("artistName", artistName, "Artist");
    setText("artistTagline", buildTagline(profile), "Artist");
    setText("artistShortCopy", profile.tagline, "No tagline yet.");
    setText("artistLocation", profile.location, "—");
    setText("artistGenres", buildGenreLine(profile), "—");
    setText("artistRoles", buildRoleLine(profile), "—");

    setText("aboutEyebrow", `About ${artistName}`, "About");
    setText("aboutHeading", artistName, artistName);
    setText("platformCopy", `Direct access to ${artistName} across platforms.`, "Direct access across platforms.");

    setImage("artistBaseArt", displayImage, "/static/logos/sse.png", artistName);

    setBioParagraphs(profile);

    setHtml(
        "featuredMediaWrap",
        profile.featured_video_embed,
        '<p class="section-copy">No featured media yet.</p>'
    );

    setHtml(
        "spotifyEmbedWrap",
        profile.spotify_embed,
        '<p class="section-copy">No Spotify embed yet.</p>'
    );

    setHtml(
        "video2EmbedWrap",
        profile.video2_embed,
        '<p class="section-copy">No second video yet.</p>'
    );

    setHtml(
        "video3EmbedWrap",
        profile.video3_embed,
        '<p class="section-copy">No third video yet.</p>'
    );

    setText("featuredHeading", profile.featured_video_name || "Featured Listen", "Featured Listen");
    setText("video2Title", profile.video2_name, "Visual Feature");
    setText("video3Title", profile.video3_name, "Second Feature");

    setOfficialWebsite(profile);

    setLinkTile("spotifyTile", profile.spotify_url);
    setLinkTile("youtubeTile", profile.youtube_channel_url);
    setLinkTile("instagramTile", profile.instagram_url);
    setLinkTile("soundcloudTile", profile.soundcloud_url);
    setLinkTile("bandcampTile", profile.bandcamp_url);
    setLinkTile("ytmusicTile", profile.youtube_music_url);
    setLinkTile("threadsTile", profile.threads_url);
    setLinkTile("tidalTile", profile.tidal_url);
    setLinkTile("appleTile", profile.apple_music_url);


}



function showArtistError(message) {
    const section = document.getElementById("artistErrorSection");
    const text = document.getElementById("artistErrorText");

    if (section) section.hidden = false;
    if (text) text.textContent = message || "We could not load this artist page.";
}

document.addEventListener("DOMContentLoaded", async () => {
    const slug = getArtistSlugFromUrl();

    if (!slug) {
        showArtistError("No artist slug was found in the URL.");
        return;
    }

    try {
        const data = await apiFetch(`/api/artists/slug/${encodeURIComponent(slug)}`);
        const profile = data.artist_profile;

        if (!profile) {
            showArtistError("Artist profile not found.");
            return;
        }

        applyArtistProfile(profile);
    } catch (error) {
        console.error("Failed to load artist profile:", error);
        showArtistError(error.message || "Failed to load artist page.");
    }
});