document.addEventListener("DOMContentLoaded", async () => {
    const listEl = document.getElementById("contracts-list");
    const errorEl = document.getElementById("contracts-error");

    try {
        const currentUser = await getCurrentUser();
        if (!currentUser) {
            window.location.href = "/";
            return;
        }

        const data = await apiFetch("/api/contracts");
        const contracts = data.contracts || [];

        if (!contracts.length) {
            listEl.innerHTML = `<div class="glass-card" style="padding:1rem;">No contracts found.</div>`;
            return;
        }

        listEl.innerHTML = contracts.map((contract) => {
            return `
                <article class="glass-card" style="padding:1rem; display:grid; gap:.6rem;">
                    <div style="display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap;">
                        <div>
                            <h3 style="margin:0;">${contract.title || "Contract"}</h3>
                            <p style="margin:.25rem 0 0 0; opacity:.8;">${contract.artist_name || "Artist"} • ${contract.contract_type || ""}</p>
                        </div>
                        <div style="opacity:.85;">${contract.status || "draft"}</div>
                    </div>

                    <div style="display:flex; gap:.75rem; flex-wrap:wrap;">
                        <a class="release-btn secondary" href="/contracts/view?id=${contract.id}">Open</a>
                    </div>
                </article>
            `;
        }).join("");
    } catch (error) {
        errorEl.textContent = error.message || "Failed to load contracts.";
    }
});