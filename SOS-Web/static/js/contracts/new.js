document.addEventListener("DOMContentLoaded", async () => {
    const artistSelect = document.getElementById("contract-artist");
    const contractType = document.getElementById("contract-type");
    const contractEmails = document.getElementById("contract-emails");
    const contractNotes = document.getElementById("contract-notes");
    const contractBody = document.getElementById("contract-body");
    const form = document.getElementById("contract-form");
    const saveSendButton = document.getElementById("save-send-button");
    const errorBox = document.getElementById("contract-error");
    const successBox = document.getElementById("contract-success");

    let artists = [];

    function clearMessages() {
        errorBox.textContent = "";
        successBox.textContent = "";
    }

    function getSelectedArtist() {
        const selectedId = artistSelect.value;
        return artists.find((artist) => String(artist.id) === String(selectedId)) || null;
    }

    async function loadArtists() {
        const data = await apiFetch("/api/contracts/artists");
        artists = data.artists || [];

        artistSelect.innerHTML = artists.map((artist) => {
            return `<option value="${artist.id}">${artist.artist_name}</option>`;
        }).join("");

        const selected = getSelectedArtist();
        if (selected) {
            contractEmails.value = (selected.emails || []).join(", ");
        }
    }

    function fillDefaultTemplate() {
        const selectedArtist = getSelectedArtist();
        const type = contractType.value;

        const artistName = selectedArtist?.artist_name || "[Artist Name]";
        const typeTitle = type === "publishing" ? "Publishing" : "Distribution";

        contractBody.value = `${typeTitle} Contract

This agreement is entered into between SpacedOut Studios and ${artistName}.

1. Parties
SpacedOut Studios and ${artistName} agree to the terms set forth in this contract.

2. Scope
This contract governs the ${typeTitle.toLowerCase()} relationship between the label and the artist.

3. Terms
Edit this language as needed before sending.

4. Signatures
The artist will sign and return the executed document.`;
    }

    artistSelect?.addEventListener("change", () => {
        const selected = getSelectedArtist();
        contractEmails.value = (selected?.emails || []).join(", ");
    });

    contractType?.addEventListener("change", () => {
        fillDefaultTemplate();
    });

    form?.addEventListener("submit", async (event) => {
        event.preventDefault();
        await submitContract(false);
    });

    saveSendButton?.addEventListener("click", async () => {
        await submitContract(true);
    });

    async function submitContract(sendNow) {
        clearMessages();

        const selectedArtist = getSelectedArtist();
        if (!selectedArtist) {
            errorBox.textContent = "Please choose an artist.";
            return;
        }

        const payload = {
            artist_profile_id: selectedArtist.id,
            artist_name: selectedArtist.artist_name,
            contract_type: contractType.value,
            body_text: contractBody.value.trim(),
            notes: contractNotes.value.trim(),
            send_now: sendNow,
            recipient_emails: contractEmails.value
                .split(",")
                .map((value) => value.trim())
                .filter(Boolean),
        };

        try {
            const data = await apiFetch("/api/contracts", {
                method: "POST",
                body: payload,
            });

            successBox.textContent = sendNow
                ? "Contract created and sent."
                : "Contract draft saved.";

            if (data.contract?.id) {
                window.location.href = `/contracts/view?id=${data.contract.id}`;
            }
        } catch (error) {
            errorBox.textContent = error.message || "Failed to save contract.";
        }
    }

    try {
        const currentUser = await getCurrentUser();
        if (!currentUser || !["admin", "developer"].includes(currentUser.role)) {
            window.location.href = "/";
            return;
        }

        await loadArtists();
        fillDefaultTemplate();
    } catch (error) {
        errorBox.textContent = error.message || "Failed to load contract editor.";
    }
});