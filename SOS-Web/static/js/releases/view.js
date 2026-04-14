document.addEventListener("DOMContentLoaded", async () => {
    const list = document.getElementById("release-list");
    const errorBox = document.getElementById("release-error");
    const pageTitle = document.getElementById("release-page-title");

    if (!list) return;

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
            list.innerHTML = `<p>No releases found.</p>`;
            return;
        }

        list.innerHTML = releases.map((release) => `
            <article class="release-card">
                <h3>${escapeHtml(release.release_title || "Untitled Release")}</h3>
                <p>Status: ${escapeHtml(release.status || "draft")}</p>
                <p>Type: ${escapeHtml(release.release_type || "—")}</p>
                <a href="/releases/edit?submission=${release.id}">Edit</a>
            </article>
        `).join("");
    } catch (error) {
        errorBox.textContent = error.message || "Failed to load releases.";
    }
});