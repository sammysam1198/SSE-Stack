let contactRequestsState = [];

function formatContactDate(value) {
    if (!value) return "—";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "—";
    return date.toLocaleDateString();
}

function contactStatusLabel(status) {
    if (status === "in_progress") return "In Progress";
    if (status === "closed") return "Closed";
    return "Open";
}

async function fetchContactRequests() {
    const data = await apiFetch("/api/admin/contact-requests");
    return data.contact_requests || [];
}

async function updateContactRequestStatus(requestId, status) {
    const result = await apiFetch(`/api/requests/contact/${requestId}`, {
        method: "PATCH",
        body: { status }
    });

    const updated = result.contact_request;
    contactRequestsState = contactRequestsState.map(item => (
        item.id === requestId ? updated : item
    ));

    renderContactRequestsTable();
}

function renderContactRequestsTable() {
    const body = document.getElementById("contact-requests-body");
    if (!body) return;

    if (!contactRequestsState.length) {
        body.innerHTML = `<tr><td colspan="7">No contact requests found.</td></tr>`;
        return;
    }

    body.innerHTML = contactRequestsState.map(item => `
        <tr>
            <td>${item.requester_name || "—"}</td>
            <td>${item.issue_type || "—"}</td>
            <td>${item.department_tag || "—"}</td>
            <td>${item.subject || "—"}</td>
            <td>${formatContactDate(item.created_at)}</td>
            <td>${contactStatusLabel(item.status)}</td>
            <td>
                <div class="applications-table__actions">
                    <button type="button" class="artist-action-button" data-view-contact="${item.id}">
                        View
                    </button>
                    <select data-contact-status="${item.id}">
                        <option value="open" ${item.status === "open" ? "selected" : ""}>Open</option>
                        <option value="in_progress" ${item.status === "in_progress" ? "selected" : ""}>In Progress</option>
                        <option value="closed" ${item.status === "closed" ? "selected" : ""}>Closed</option>
                    </select>
                </div>
            </td>
        </tr>
    `).join("");

    body.querySelectorAll("[data-view-contact]").forEach(button => {
        button.addEventListener("click", () => {
            const id = Number(button.getAttribute("data-view-contact"));
            const item = contactRequestsState.find(row => row.id === id);
            if (!item) return;

            alert([
                `${item.subject || "Contact Request"}`,
                "",
                `From: ${item.requester_name || "—"} <${item.requester_email || "—"}>`,
                `Department: ${item.department_tag || "—"}`,
                `Issue: ${item.issue_type || "—"}`,
                "",
                item.message || "—"
            ].join("\n"));
        });
    });

    body.querySelectorAll("[data-contact-status]").forEach(select => {
        select.addEventListener("change", async () => {
            const id = Number(select.getAttribute("data-contact-status"));
            try {
                await updateContactRequestStatus(id, select.value);
            } catch (error) {
                console.error("Failed to update contact request:", error);
                alert(error.message || "Could not update contact request.");
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    const body = document.getElementById("contact-requests-body");
    if (!body) return;

    try {
        contactRequestsState = await fetchContactRequests();
        renderContactRequestsTable();
    } catch (error) {
        console.error("Failed to load contact requests:", error);
        body.innerHTML = `<tr><td colspan="7">Could not load contact requests.</td></tr>`;
    }
});
