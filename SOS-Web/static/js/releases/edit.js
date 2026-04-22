document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("release-form");
    const errorBox = document.getElementById("release-error");
    const successBox = document.getElementById("release-success");
    const pageTitle = document.getElementById("release-page-title");
    const reviewNote = document.getElementById("release-review-note");

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

        if (String(release.status || "").toLowerCase() !== "draft") {
            errorBox.textContent = "Only draft releases can be edited.";
            form.style.display = "none";
            return;
        }

        if (pageTitle) {
            pageTitle.textContent = `Edit Release: ${release.release_title || "Untitled"}`;
        }

        if (reviewNote) {
            reviewNote.textContent = release.artist_notes || "No label notes attached.";
        }

        form.elements["release_title"].value = release.release_title || "";
        form.elements["release_type"].value = release.release_type || "";
        form.elements["preferred_release_date"].value = release.preferred_release_date || "";
        form.elements["primary_genre"].value = release.primary_genre || "";
        form.elements["other_genres"].value = release.other_genres || "";
        form.elements["release_pitch"].value = release.release_pitch || "";

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            errorBox.textContent = "";
            successBox.textContent = "";

            const formData = new FormData(form);

            const payload = {
                release_title: formData.get("release_title")?.trim() || "",
                release_type: formData.get("release_type")?.trim() || "",
                preferred_release_date: formData.get("preferred_release_date")?.trim() || "",
                primary_genre: formData.get("primary_genre")?.trim() || "",
                other_genres: formData.get("other_genres")?.trim() || "",
                release_pitch: formData.get("release_pitch")?.trim() || "",
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