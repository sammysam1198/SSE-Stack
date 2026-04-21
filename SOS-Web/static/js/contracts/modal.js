document.addEventListener("DOMContentLoaded", async () => {
    const modal = document.getElementById("contract-create-modal");
    const artistSelect = document.getElementById("contract-modal-artist");
    const typeSelect = document.getElementById("contract-modal-type");
    const errorBox = document.getElementById("contract-modal-error");

    const openButtons = [
        document.getElementById("open-contract-modal-admin"),
        document.getElementById("open-contract-modal-dev"),
    ].filter(Boolean);

    const closeButtons = [
        document.getElementById("close-contract-modal-admin"),
        document.getElementById("close-contract-modal-dev"),
    ].filter(Boolean);

    const continueButtons = [
        document.getElementById("continue-contract-modal-admin"),
        document.getElementById("continue-contract-modal-dev"),
    ].filter(Boolean);

    if (!modal || !artistSelect || !typeSelect) return;

    let artists = [];

    function openModal() {
        modal.classList.add("is-open");
    }

    function closeModal() {
        modal.classList.remove("is-open");
        if (errorBox) errorBox.textContent = "";
    }

    async function loadArtists() {
        const data = await apiFetch("/api/contracts/artists");
        artists = data.artists || [];

        artistSelect.innerHTML = artists.map((artist) => {
            return `<option value="${artist.id}" data-name="${String(artist.artist_name || "").replaceAll('"', "&quot;")}">${artist.artist_name}</option>`;
        }).join("");
    }

    openButtons.forEach((button) => {
        button.addEventListener("click", async () => {
            try {
                if (!artists.length) {
                    await loadArtists();
                }
                openModal();
            } catch (error) {
                if (errorBox) {
                    errorBox.textContent = error.message || "Failed to load artists.";
                }
            }
        });
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", closeModal);
    });

    modal.addEventListener("click", (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    continueButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const artistId = artistSelect.value;
            const contractType = typeSelect.value;

            if (!artistId) {
                if (errorBox) errorBox.textContent = "Please choose an artist.";
                return;
            }

            window.location.href = `/contracts/new?artist_profile_id=${encodeURIComponent(artistId)}&type=${encodeURIComponent(contractType)}`;
        });
    });
});