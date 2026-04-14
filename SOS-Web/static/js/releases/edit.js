document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("release-form");
    const pageTitle = document.getElementById("release-page-title");
    const artistContext = document.getElementById("artist-context");
    const errorBox = document.getElementById("release-error");
    const successBox = document.getElementById("release-success");

    if (!form) return;

    try {
        const user = await getCurrentUser();
        if (!user) {
            window.location.href = "/";
            return;
        }

        const { artist } = getReleasePageParams();

        let selectedArtist = null;

        if (isPrivilegedRole(user.role) && artist) {
            selectedArtist = artist;
        } else if (user.role === "artist") {
            selectedArtist = user.artist_page || user.artist_name || user.username || null;
        }

        if (artistContext) {
            artistContext.textContent = selectedArtist
                ? `Creating release for ${selectedArtist}`
                : "Creating new release";
        }

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            errorBox.textContent = "";
            successBox.textContent = "";

            const formData = new FormData(form);

            const payload = {
                artist: selectedArtist,
                release_title: formData.get("release_title")?.trim(),
                release_type: formData.get("release_type")?.trim(),
                language: formData.get("language")?.trim(),
                preferred_release_date: formData.get("preferred_release_date")?.trim(),
                pitch: formData.get("pitch")?.trim(),
                lyrics: formData.get("lyrics")?.trim(),
                genre_notes: formData.get("genre_notes")?.trim(),
            };

            try {
                const data = await apiFetch("/api/releases", {
                    method: "POST",
                    body: payload,
                });

                successBox.textContent = "Release draft created successfully.";

                if (data.release && data.release.id) {
                    window.location.href = `/releases-edit.html?submission=${data.release.id}`;
                }
            } catch (error) {
                errorBox.textContent = error.message || "Failed to create release draft.";
            }
        });
    } catch (error) {
        if (errorBox) {
            errorBox.textContent = "Failed to load release page.";
        }
    }
});