document.addEventListener("DOMContentLoaded", () => {
    const inviteUserForm = document.getElementById("invite-user-form");
    if (!inviteUserForm) return;

    const inviteEmailInput = document.getElementById("invite-email");
    const inviteRoleInput = document.getElementById("invite-role");
    const inviteArtistNameInput = document.getElementById("invite-artist-name");
    const inviteArtistPageInput = document.getElementById("invite-artist-page");
    const inviteUserError = document.getElementById("invite-user-error");
    const inviteUserSuccess = document.getElementById("invite-user-success");
    const inviteUserSubmit = document.getElementById("invite-user-submit");
    const inviteEmailSubjectInput = document.getElementById("invite-email-subject");
    const inviteEmailBodyInput = document.getElementById("invite-email-body");

    function normalizeArtistPage(value) {
        if (!value) return "";

        let cleaned = value.trim();

        try {
            if (cleaned.startsWith("http://") || cleaned.startsWith("https://")) {
                const url = new URL(cleaned);
                cleaned = url.pathname || "";
            }
        } catch (error) {
            console.warn("Could not parse associated page URL:", error);
        }

        cleaned = cleaned.replace(/^\/+|\/+$/g, "");
        cleaned = cleaned.replace(/^artists\//i, "");
        cleaned = cleaned.replace(/\.html$/i, "");
        cleaned = cleaned.trim();

        return cleaned;
    }

    function slugifyArtistName(value) {
        return value
            .toLowerCase()
            .trim()
            .replace(/[^a-z0-9\s-]/g, "")
            .replace(/\s+/g, "-")
            .replace(/-+/g, "-");
    }

    function updateRoleDependentFields() {
        const role = inviteRoleInput.value;
        const isArtist = role === "artist";

        inviteArtistNameInput.disabled = !isArtist;
        inviteArtistPageInput.disabled = !isArtist;

        inviteArtistNameInput.required = isArtist;
        inviteArtistPageInput.required = isArtist;

        if (!isArtist) {
            inviteArtistNameInput.value = "";
            inviteArtistPageInput.value = "";
            delete inviteArtistPageInput.dataset.editedManually;
        }
    }

    inviteRoleInput.addEventListener("change", updateRoleDependentFields);
    updateRoleDependentFields();

    inviteArtistNameInput.addEventListener("input", () => {
        if (inviteRoleInput.value !== "artist") return;

        if (!inviteArtistPageInput.dataset.editedManually) {
            inviteArtistPageInput.value = slugifyArtistName(inviteArtistNameInput.value);
        }
    });

    inviteArtistPageInput.addEventListener("input", () => {
        inviteArtistPageInput.dataset.editedManually = "true";
    });

    inviteArtistPageInput.addEventListener("blur", () => {
        inviteArtistPageInput.value = normalizeArtistPage(inviteArtistPageInput.value);
    });

    inviteUserForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        inviteUserError.textContent = "";
        inviteUserSuccess.textContent = "";

        const email = (inviteEmailInput.value || "").trim().toLowerCase();
        const role = inviteRoleInput.value;
        const artistName = (inviteArtistNameInput.value || "").trim();
        const artistPage = normalizeArtistPage(inviteArtistPageInput.value || "");
        const emailSubject = (inviteEmailSubjectInput?.value || "").trim();
        const emailBody = (inviteEmailBodyInput?.value || "").trim();

        if (!email) {
            inviteUserError.textContent = "Email is required.";
            return;
        }

        if (!role) {
            inviteUserError.textContent = "Role is required.";
            return;
        }

        if (role === "artist") {
            if (!artistName) {
                inviteUserError.textContent = "Artist name is required for artist accounts.";
                return;
            }

            if (!artistPage) {
                inviteUserError.textContent = "Associated page is required for artist accounts.";
                return;
            }
        }

        inviteUserSubmit.disabled = true;
        inviteUserForm.classList.add("is-loading");

        const payload = {
            email,
            role
        };

        if (role === "artist") {
            payload.artist_name = artistName;
            payload.artist_page = artistPage;
            if (emailSubject) {
                payload.email_subject = emailSubject;
            }

            if (emailBody) {
                payload.email_body = emailBody;
            }
        }

        try {
            const response = await apiFetch("/api/admin/users/create-artist", {
                method: "POST",
                body: payload
            });

            inviteUserSuccess.textContent =
                response.message || "Invite sent successfully.";

            inviteUserForm.reset();
            delete inviteArtistPageInput.dataset.editedManually;
            updateRoleDependentFields();
        } catch (error) {
            inviteUserError.textContent =
                error.message || "Could not send invite.";
        } finally {
            inviteUserSubmit.disabled = false;
            inviteUserForm.classList.remove("is-loading");
        }
    });
});