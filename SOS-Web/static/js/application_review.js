let applicationsState = [];

function formatDate(value) {
    if (!value) return "—";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "—";
    return date.toLocaleDateString();
}

function derivedStatus(app) {
    if (app.status === "approved") return "Approved";
    if (app.status === "denied") return "Denied";
    if (app.status === "pending" && !app.opened_at) return "Unopened";
    return "Pending";
}

function sortApplications(items, sortValue) {
    const copy = [...items];

    if (sortValue === "az") {
        copy.sort((a, b) => (a.artist_name || "").localeCompare(b.artist_name || ""));
        return copy;
    }

    if (sortValue === "za") {
        copy.sort((a, b) => (b.artist_name || "").localeCompare(a.artist_name || ""));
        return copy;
    }

    if (sortValue === "oldest") {
        copy.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        return copy;
    }

    copy.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    return copy;
}

function filterApplications(items, filterValue) {
    if (filterValue === "all") return items;
    if (filterValue === "unopened") {
        return items.filter(app => app.status === "pending" && !app.opened_at);
    }
    if (filterValue === "pending") {
        return items.filter(app => app.status === "pending" && !!app.opened_at);
    }
    return items.filter(app => app.status === filterValue);
}

async function fetchApplications() {
    const data = await apiFetch("/api/applications");
    return data.applications || [];
}

async function openApplicationPdf(application) {
    if (application.status === "pending" && !application.opened_at) {
        try {
            const result = await apiFetch(`/api/applications/${application.id}/open`, {
                method: "POST"
            });
            application.opened_at = result.application?.opened_at || new Date().toISOString();
        } catch (error) {
            console.error("Failed to mark application opened:", error);
        }
    }

    const overlay = document.getElementById("application-pdf-overlay");
    const frame = document.getElementById("application-pdf-frame");
    const title = document.getElementById("application-pdf-title");
    const download = document.getElementById("application-pdf-download");

    if (!overlay || !frame || !title || !download) return;

    title.textContent = `${application.artist_name || "Artist"} Application`;
    frame.src = `${API_BASE}/api/applications/${application.id}/pdf?disposition=inline`;
    download.href = `${API_BASE}/api/applications/${application.id}/pdf?disposition=attachment`;

    overlay.hidden = false;
    renderApplicationsTable();
}

function closeApplicationPdfOverlay() {
    const overlay = document.getElementById("application-pdf-overlay");
    const frame = document.getElementById("application-pdf-frame");
    if (!overlay || !frame) return;
    frame.src = "";
    overlay.hidden = true;
}

async function updateApplicationStatus(applicationId, status) {
    const result = await apiFetch(`/api/applications/${applicationId}/status`, {
        method: "PATCH",
        body: { status }
    });

    const updated = result.application;
    applicationsState = applicationsState.map(app => (
        app.id === applicationId ? updated : app
    ));

    renderApplicationsTable();
}

function renderApplicationsTable() {
    const body = document.getElementById("applications-table-body");
    const sortSelect = document.getElementById("application-sort-select");
    const statusFilter = document.getElementById("application-status-filter");

    if (!body) return;

    const sortValue = sortSelect?.value || "newest";
    const filterValue = statusFilter?.value || "all";

    let rows = filterApplications(applicationsState, filterValue);
    rows = sortApplications(rows, sortValue);

    if (!rows.length) {
        body.innerHTML = `<tr><td colspan="4">No applications found.</td></tr>`;
        return;
    }

    body.innerHTML = rows.map(app => `
        <tr>
            <td>${app.artist_name || "—"}</td>
            <td>${formatDate(app.created_at)}</td>
            <td>${derivedStatus(app)}</td>
            <td>
                <div class="applications-table__actions">
                    <button type="button" class="artist-action-button" data-open-application="${app.id}">
                        View
                    </button>

                    <select data-status-application="${app.id}">
                        <option value="pending" ${app.status === "pending" ? "selected" : ""}>Pending</option>
                        <option value="approved" ${app.status === "approved" ? "selected" : ""}>Approved</option>
                        <option value="denied" ${app.status === "denied" ? "selected" : ""}>Denied</option>
                    </select>
                </div>
            </td>
        </tr>
    `).join("");

    body.querySelectorAll("[data-open-application]").forEach(button => {
        button.addEventListener("click", () => {
            const id = Number(button.getAttribute("data-open-application"));
            const app = applicationsState.find(item => item.id === id);
            if (app) openApplicationPdf(app);
        });
    });

    body.querySelectorAll("[data-status-application]").forEach(select => {
        select.addEventListener("change", async () => {
            const id = Number(select.getAttribute("data-status-application"));
            try {
                await updateApplicationStatus(id, select.value);
            } catch (error) {
                console.error("Failed to update application status:", error);
                alert(error.message || "Could not update application status.");
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    const body = document.getElementById("applications-table-body");
    if (!body) return;

    document.getElementById("application-sort-select")?.addEventListener("change", renderApplicationsTable);
    document.getElementById("application-status-filter")?.addEventListener("change", renderApplicationsTable);
    document.getElementById("application-pdf-close")?.addEventListener("click", closeApplicationPdfOverlay);
    document.getElementById("application-pdf-close-backdrop")?.addEventListener("click", closeApplicationPdfOverlay);

    try {
        applicationsState = await fetchApplications();
        renderApplicationsTable();
    } catch (error) {
        console.error("Failed to load applications:", error);
        body.innerHTML = `<tr><td colspan="4">Could not load applications.</td></tr>`;
    }
});