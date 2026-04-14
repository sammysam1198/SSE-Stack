document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("release-form");
    const errorBox = document.getElementById("release-error");
    const successBox = document.getElementById("release-success");
    const pageTitle = document.getElementById("release-page-title");

    if (!form) return;

    const { submission } = getReleasePageParams();

    if (!submission) {
        errorBox.textContent = "Missing submission id.";
        return;
    }

    try {
        const user = await getCurrentUser();
        if (!user) {
            window.location.href = "/";
            return;
        }

        const data = await apiFetch(`/api/releases/${submission}`);
        const release = data.release;

        if (pageTitle) {
            pageTitle.textContent = `Edit Release: ${release.release_title || "Untitled"}`;
        }

        form.elements["release_title"].value = release.release_title || "";
        form.elements["release_type"].value = release.release_type || "";
        form.elements["language"].value = release.language || "";
        form.elements["preferred_release_date"].value = release.preferred_release_date || "";
        form.elements["pitch"].value = release.pitch || "";
        form.elements["lyrics"].value = release.lyrics || "";
        form.elements["genre_notes"].value = release.genre_notes || "";

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            errorBox.textContent = "";
            successBox.textContent = "";

            const formData = new FormData(form);

            const payload = {
                release_title: formData.get("release_title")?.trim(),
                release_type: formData.get("release_type")?.trim(),
                language: formData.get("language")?.trim(),
                preferred_release_date: formData.get("preferred_release_date")?.trim(),
                pitch: formData.get("pitch")?.trim(),
                lyrics: formData.get("lyrics")?.trim(),
                genre_notes: formData.get("genre_notes")?.trim(),
            };

            try {
                await apiFetch(`/api/releases/${submission}`, {
                    method: "PATCH",
                    body: payload,
                });

                successBox.textContent = "Release draft updated successfully.";
            } catch (error) {
                errorBox.textContent = error.message || "Failed to update release.";
            }
        });
    } catch (error) {
        errorBox.textContent = error.message || "Failed to load release.";
    }
});