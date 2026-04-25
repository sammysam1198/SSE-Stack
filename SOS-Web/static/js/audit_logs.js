function formatAuditDate(value) {
    if (!value) return "—";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "—";
    return date.toLocaleString();
}

async function fetchAuditLogs() {
    const data = await apiFetch("/api/admin/audit-logs");
    return data.audit_logs || [];
}

function renderAuditLogs(logs) {
    const body = document.getElementById("audit-logs-body");
    if (!body) return;

    if (!logs.length) {
        body.innerHTML = `<tr><td colspan="5">No audit logs found.</td></tr>`;
        return;
    }

    body.innerHTML = logs.map(log => `
        <tr>
            <td>${formatAuditDate(log.created_at)}</td>
            <td>${log.event_type || "—"}</td>
            <td>${log.actor_role || "system"}</td>
            <td>${log.entity_type || "—"}${log.entity_id ? ` #${log.entity_id}` : ""}</td>
            <td>${log.message || "—"}</td>
        </tr>
    `).join("");
}

document.addEventListener("DOMContentLoaded", async () => {
    const body = document.getElementById("audit-logs-body");
    if (!body) return;

    try {
        const logs = await fetchAuditLogs();
        renderAuditLogs(logs);
    } catch (error) {
        console.error("Failed to load audit logs:", error);
        body.innerHTML = `<tr><td colspan="5">Could not load audit logs.</td></tr>`;
    }
});
