let selectedComplaintId = null;
let complaintModal = null;
let filterTimer = null;

document.addEventListener('DOMContentLoaded', () => {
    complaintModal = new bootstrap.Modal(document.getElementById('complaintModal'), { backdrop: 'static' });
    loadComplaints();

    ['filterSearch', 'filterLocation'].forEach(id => {
        document.getElementById(id).addEventListener('input', () => {
            clearTimeout(filterTimer);
            filterTimer = setTimeout(loadComplaints, 400);
        });
    });

    ['filterStatus', 'filterCategory', 'filterSeverity'].forEach(id => {
        document.getElementById(id).addEventListener('change', loadComplaints);
    });
});

async function loadComplaints() {
    const tbody = document.getElementById('complaintsTableBody');
    tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4">Loading...</td></tr>';

    try {
        const params = {
            limit: 100,
            search: document.getElementById('filterSearch').value.trim() || undefined,
            status: document.getElementById('filterStatus').value || undefined,
            category: document.getElementById('filterCategory').value || undefined,
            severity: document.getElementById('filterSeverity').value || undefined,
            location: document.getElementById('filterLocation').value.trim() || undefined,
        };

        const response = await apiClient.getAllComplaints(params);
        const complaints = response.data || [];

        if (!complaints.length) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">No complaints found</td></tr>';
            return;
        }

        tbody.innerHTML = complaints.map(c => `
            <tr class="complaint-row" onclick="openDrawer('${c._id}')">
                <td><code class="small">${c.complaint_id || c._id.slice(-8)}</code></td>
                <td>${c.category}</td>
                <td><span class="badge bg-${getSeverityColor(c.severity)}">${c.severity}</span></td>
                <td class="d-none d-md-table-cell text-truncate" style="max-width:150px">${c.location || 'N/A'}</td>
                <td><span class="badge bg-${getStatusColor(c.status)}">${formatStatus(c.status)}</span></td>
                <td class="d-none d-sm-table-cell">${c.priority_score || c.priority || 0}</td>
                <td class="small">${formatDate(c.created_at)}</td>
            </tr>
        `).join('');
    } catch (err) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger py-4">Failed to load complaints</td></tr>';
    }
}

function renderModalContent(complaint, history) {
    const content = document.getElementById('drawerContent');
    const feedback = complaint.feedback || {};
    const timeline = history.length ? history : [{ status: 'Open', timestamp: complaint.created_at, updated_by: 'citizen' }];

    document.getElementById('updateStatus').value = formatStatus(complaint.status);
    document.getElementById('updateDepartment').value = complaint.assigned_department || complaint.department || '';
    document.getElementById('updateNotes').value = complaint.resolution_notes || '';

    content.innerHTML = `
        <div id="saveSuccessAlert" class="alert alert-success d-none mb-3">
            <i class="fas fa-check-circle"></i> Changes saved successfully. Modal stays open for further edits.
        </div>
        <div class="drawer-section">
            <label>Tracking ID</label>
            <p><code>${complaint.complaint_id || complaint._id}</code></p>
        </div>
        <div class="drawer-section">
            <label>Complaint Text</label>
            <p>${complaint.text}</p>
        </div>
        <div class="row drawer-section g-2">
            <div class="col-6 col-md-4"><label>Category</label><p>${complaint.category}</p></div>
            <div class="col-6 col-md-4"><label>Severity</label><p><span class="badge bg-${getSeverityColor(complaint.severity)}">${complaint.severity}</span></p></div>
            <div class="col-6 col-md-4"><label>Priority</label><p>${complaint.priority_score || complaint.priority}/100</p></div>
            <div class="col-6 col-md-4"><label>Department</label><p>${complaint.assigned_department || complaint.department || 'N/A'}</p></div>
            <div class="col-12"><label>Location</label><p>${complaint.location}</p></div>
            ${complaint.duplicate_group_id ? '<div class="col-12"><span class="badge bg-info">Duplicate Cluster</span></div>' : ''}
        </div>
        <div class="drawer-section">
            <label>Status History</label>
            <div class="status-timeline">
                ${timeline.map(h => `
                    <div class="timeline-step">
                        <div class="timeline-dot"></div>
                        <div>
                            <strong>${formatStatus(h.status)}</strong>
                            <small class="d-block text-muted">${formatDate(h.timestamp)} · ${h.updated_by || 'system'}</small>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        ${complaint.resolution_notes ? `<div class="drawer-section"><label>Resolution Notes</label><p>${complaint.resolution_notes}</p></div>` : ''}
        ${feedback.rating ? `
            <div class="drawer-section">
                <label>Citizen Feedback</label>
                <p>${'★'.repeat(feedback.rating)}${'☆'.repeat(5 - feedback.rating)} (${feedback.rating}/5)</p>
                <p class="text-muted">${feedback.comment || ''}</p>
            </div>
        ` : ''}
    `;
}

async function openDrawer(complaintId) {
    selectedComplaintId = complaintId;
    document.getElementById('drawerContent').innerHTML =
        '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';
    complaintModal.show();

    try {
        const [complaint, history] = await Promise.all([
            apiClient.getComplaint(complaintId),
            apiClient.getStatusHistory(complaintId).catch(() => []),
        ]);
        renderModalContent(complaint, history);
    } catch (err) {
        document.getElementById('drawerContent').innerHTML =
            '<div class="alert alert-danger">Failed to load details</div>';
    }
}

function closeDrawer() {
    complaintModal?.hide();
    selectedComplaintId = null;
}

async function saveComplaintUpdate() {
    if (!selectedComplaintId) return;

    const saveBtn = document.querySelector('.modal-footer .btn-primary');
    const originalText = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Saving...';

    try {
        await apiClient.updateComplaint(selectedComplaintId, {
            status: document.getElementById('updateStatus').value,
            assigned_department: document.getElementById('updateDepartment').value,
            resolution_notes: document.getElementById('updateNotes').value,
            updated_by: 'admin',
        });

        const [complaint, history] = await Promise.all([
            apiClient.getComplaint(selectedComplaintId),
            apiClient.getStatusHistory(selectedComplaintId).catch(() => []),
        ]);

        renderModalContent(complaint, history);
        await loadComplaints();

        const alert = document.getElementById('saveSuccessAlert');
        if (alert) {
            alert.classList.remove('d-none');
            setTimeout(() => alert.classList.add('d-none'), 4000);
        }
    } catch (err) {
        alert(err.message || 'Failed to update complaint');
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;
    }
}
