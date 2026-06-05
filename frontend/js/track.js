let currentComplaintId = null;
let currentMongoId = null;
let selectedRating = 0;

const STATUS_DESCRIPTIONS = {
    'Open': 'Complaint received and registered',
    'Under Review': 'Under review by officials',
    'Assigned': 'Assigned to responsible department',
    'In Progress': 'Work in progress by assigned team',
    'Resolved': 'Issue has been addressed',
    'Closed': 'Case closed',
    'open': 'Complaint received and registered',
    'in-progress': 'Work in progress',
    'resolved': 'Issue has been addressed',
};

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const complaintId = urlParams.get('id');
    if (complaintId) {
        document.getElementById('searchId').value = complaintId;
        searchComplaint();
    }

    document.getElementById('searchId').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchComplaint();
    });

    document.querySelectorAll('.star-btn').forEach(star => {
        star.addEventListener('click', () => {
            selectedRating = parseInt(star.dataset.rating);
            updateStarDisplay();
        });
    });
});

function updateStarDisplay() {
    document.querySelectorAll('.star-btn').forEach(star => {
        star.classList.toggle('active', parseInt(star.dataset.rating) <= selectedRating);
    });
}

async function searchComplaint() {
    const searchValue = document.getElementById('searchId').value.trim();
    if (!searchValue) { showError('Please enter a complaint ID'); return; }

    showLoading(true);
    hideError();

    try {
        const complaint = await apiClient.getComplaint(searchValue);
        currentMongoId = complaint._id;
        currentComplaintId = complaint.complaint_id || complaint._id;

        const history = await apiClient.getStatusHistory(currentMongoId).catch(() => []);
        displayComplaintDetails(complaint, history);
    } catch (error) {
        showError('Complaint not found. Use the Tracking ID shown after submission (e.g. CL-20240604-ABC123).');
        hideComplaintDetails();
    } finally {
        showLoading(false);
    }
}

function isResolved(status) {
    return ['Resolved', 'Closed', 'resolved', 'closed'].includes(status);
}

function buildTimeline(history, complaint) {
    let entries = Array.isArray(history) && history.length ? [...history] : [];

    if (!entries.length) {
        entries = [{
            status: complaint.status || 'Open',
            timestamp: complaint.created_at,
            updated_by: 'citizen',
        }];
    } else {
        const hasSubmitted = entries.some(e =>
            ['Open', 'open'].includes(e.status) ||
            formatDate(e.timestamp) === formatDate(complaint.created_at)
        );
        if (!hasSubmitted) {
            entries.unshift({
                status: 'Open',
                timestamp: complaint.created_at,
                updated_by: 'citizen',
            });
        }
    }

    entries.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    const currentStatus = formatStatus(complaint.status);
    const lastEntry = entries[entries.length - 1];
    if (lastEntry && formatStatus(lastEntry.status) !== currentStatus) {
        entries.push({
            status: complaint.status,
            timestamp: complaint.updated_at || complaint.created_at,
            updated_by: 'system',
        });
    }

    return entries.map((entry, index) => {
        const statusLabel = formatStatus(entry.status);
        const isLast = index === entries.length - 1;
        const isComplete = !isLast || isResolved(entry.status);
        const description = STATUS_DESCRIPTIONS[entry.status] || STATUS_DESCRIPTIONS[statusLabel] || 'Status updated';
        const updatedBy = entry.updated_by || 'system';

        return `
            <div class="timeline-item">
                <div class="timeline-marker ${isComplete ? 'completed' : ''}">
                    <i class="fas fa-${isComplete ? 'check' : 'hourglass-half'}"></i>
                </div>
                <div class="timeline-content">
                    <h6>${statusLabel}</h6>
                    <p>${formatDate(entry.timestamp)}</p>
                    <small class="text-muted">${description}</small>
                    <small class="d-block text-muted">Updated by: ${updatedBy}</small>
                </div>
            </div>
        `;
    }).join('');
}

function displayComplaintDetails(complaint, history) {
    document.getElementById('emptyState').classList.add('d-none');
    document.getElementById('complaintDetails').classList.remove('d-none');

    document.getElementById('trackingIdDisplay').textContent = complaint.complaint_id || complaint._id;
    document.getElementById('statusTimeline').innerHTML = buildTimeline(history, complaint);

    document.getElementById('detailText').textContent = complaint.text || 'N/A';
    document.getElementById('detailLocation').textContent = complaint.location || 'N/A';
    document.querySelector('#detailCategory .badge').textContent = complaint.category || 'Unclassified';
    document.getElementById('detailSeverity').innerHTML =
        `<span class="badge bg-${getSeverityColor(complaint.severity)}">${complaint.severity || 'N/A'}</span>`;

    const priority = complaint.priority_score || complaint.priority || 0;
    const priorityBar = document.getElementById('detailPriority');
    priorityBar.style.width = `${priority}%`;
    priorityBar.textContent = `${priority}/100`;
    priorityBar.className = `progress-bar bg-${priority >= 70 ? 'danger' : priority >= 50 ? 'warning' : 'success'}`;

    document.getElementById('detailDepartment').textContent = complaint.assigned_department || complaint.department || 'N/A';
    document.getElementById('detailLanguage').textContent = complaint.language || 'N/A';
    document.getElementById('detailConfidence').textContent =
        complaint.ai_confidence !== undefined ? `${Math.round(complaint.ai_confidence * 100)}%` : 'N/A';

    const resolutionCard = document.getElementById('resolutionNotesCard');
    const resolutionNotes = complaint.resolution_notes;
    if (resolutionNotes && resolutionNotes.trim()) {
        resolutionCard.classList.remove('d-none');
        document.getElementById('detailResolutionNotes').textContent = resolutionNotes;
        document.getElementById('resolutionUpdatedAt').textContent =
            complaint.updated_at ? `Last updated: ${formatDate(complaint.updated_at)}` : '';
    } else {
        resolutionCard.classList.add('d-none');
    }

    document.getElementById('duplicateInfo').classList.toggle('d-none', !complaint.duplicate_group_id);

    const status = complaint.status;
    const feedback = complaint.feedback || {};
    const feedbackSection = document.getElementById('feedbackSection');
    const feedbackDisplay = document.getElementById('feedbackDisplay');

    if (isResolved(status) && !feedback.rating) {
        feedbackSection.classList.remove('d-none');
        feedbackDisplay.classList.add('d-none');
    } else if (feedback.rating) {
        feedbackSection.classList.add('d-none');
        feedbackDisplay.classList.remove('d-none');
        document.getElementById('feedbackStars').textContent = '★'.repeat(feedback.rating) + '☆'.repeat(5 - feedback.rating);
        document.getElementById('feedbackCommentDisplay').textContent = feedback.comment || 'No comment provided';
    } else {
        feedbackSection.classList.add('d-none');
        feedbackDisplay.classList.add('d-none');
    }

    document.getElementById('complaintDetails').scrollIntoView({ behavior: 'smooth' });
}

async function submitFeedback() {
    const id = currentMongoId || currentComplaintId;
    if (!id || !selectedRating) {
        showError('Please select a star rating');
        return;
    }
    try {
        await apiClient.submitFeedback(id, {
            rating: selectedRating,
            comment: document.getElementById('feedbackComment').value.trim(),
        });
        alert('Thank you for your feedback!');
        document.getElementById('searchId').value = currentComplaintId;
        searchComplaint();
    } catch (err) {
        showError(err.message || 'Failed to submit feedback');
    }
}

function hideComplaintDetails() {
    document.getElementById('complaintDetails').classList.add('d-none');
    document.getElementById('emptyState').classList.remove('d-none');
}

function showLoading(show) {
    document.getElementById('loadingSpinner').classList.toggle('d-none', !show);
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorAlert').classList.remove('d-none');
}

function hideError() {
    document.getElementById('errorAlert').classList.add('d-none');
}
