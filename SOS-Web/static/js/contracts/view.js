document.addEventListener("DOMContentLoaded", async () => {
    const params = new URLSearchParams(window.location.search);
    const contractId = params.get("id");

    const titleEl = document.getElementById("contract-title");
    const metaEl = document.getElementById("contract-meta");
    const statusLineEl = document.getElementById("contract-status-line");
    const recipientsEl = document.getElementById("contract-recipients");
    const bodyEl = document.getElementById("contract-body");
    const errorEl = document.getElementById("contract-error");
    const successEl = document.getElementById("contract-success");

    const downloadDocx = document.getElementById("download-unsigned-docx");
    const downloadPdf = document.getElementById("download-unsigned-pdf");
    const downloadSigned = document.getElementById("download-signed-pdf");

    const signedFileInput = document.getElementById("signed-contract-file");
    const uploadSignedButton = document.getElementById("upload-signed-button");

    function clearMessages() {
        errorEl.textContent = "";
        successEl.textContent = "";
    }

    if (!contractId) {
        errorEl.textContent = "Missing contract id.";
        return;
    }

    const currentUser = await getCurrentUser();
    if (!currentUser) {
        const returnTo = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/signin.html?next=${returnTo}`;
        return;
    }

    async function loadContract() {
        const data = await apiFetch(`/api/contracts/${contractId}`);
        const contract = data.contract;
        const recipients = data.recipients || [];

        titleEl.textContent = contract.title || "Contract";
        metaEl.textContent = `${contract.artist_name || "Artist"} • ${contract.contract_type || "contract"}`;
        statusLineEl.textContent = `Status: ${contract.status || "draft"}`;

        recipientsEl.innerHTML = recipients.length
            ? recipients.map((recipient) => `<div>${recipient.email}</div>`).join("")
            : `<div>No recipients saved.</div>`;

        bodyEl.textContent = contract.body_text || "";

        downloadDocx.href = `${API_BASE}/api/contracts/${contractId}/download/unsigned-docx`;
        downloadPdf.href = `${API_BASE}/api/contracts/${contractId}/download/unsigned-pdf`;

        if (contract.signed_object_key) {
            downloadSigned.href = `${API_BASE}/api/contracts/${contractId}/download/signed`;
            downloadSigned.style.display = "inline-flex";
        } else {
            downloadSigned.style.display = "none";
        }
    }

    uploadSignedButton?.addEventListener("click", async () => {
        clearMessages();

        const file = signedFileInput.files?.[0];
        if (!file) {
            errorEl.textContent = "Please choose a signed PDF.";
            return;
        }

        const formData = new FormData();
        formData.append("signed_contract", file);

        try {
            const response = await fetch(`${API_BASE}/api/contracts/${contractId}/upload-signed`, {
                method: "POST",
                body: formData,
                credentials: "include",
            });

            let data = {};
            try {
                data = await response.json();
            } catch (error) {
                data = {};
            }

            if (!response.ok) {
                throw new Error(data.error || "Failed to upload signed contract.");
            }

            successEl.textContent = "Signed contract uploaded successfully.";
            await loadContract();
        } catch (error) {
            errorEl.textContent = error.message || "Failed to upload signed contract.";
        }
    });

    try {
        const currentUser = await getCurrentUser();
        if (!currentUser) {
            window.location.href = "/";
            return;
        }

        await loadContract();
    } catch (error) {
        errorEl.textContent = error.message || "Failed to load contract.";
    }
});