let autocompleteTimer = null;

document.addEventListener('DOMContentLoaded', function() {
    const complaintForm = document.getElementById('complaintForm');
    const complaintText = document.getElementById('complaintText');
    const charCount = document.getElementById('charCount');
    const locationInput = document.getElementById('location');

    complaintText.addEventListener('input', () => {
        charCount.textContent = complaintText.value.length;
    });

    complaintForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await submitComplaint();
    });

    locationInput.addEventListener('input', () => {
        clearTimeout(autocompleteTimer);
        const query = locationInput.value.trim();
        if (query.length < 2) {
            hideSuggestions();
            return;
        }
        autocompleteTimer = setTimeout(() => fetchSuggestions(query), 300);
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.location-autocomplete-wrapper')) hideSuggestions();
    });

    document.getElementById('copyIdBtn')?.addEventListener('click', copyComplaintId);
});

async function fetchSuggestions(query) {
    const dropdown = document.getElementById('locationSuggestions');
    try {
        const result = await apiClient.getPlacesAutocomplete(query);
        const suggestions = result.data || result || [];
        if (!suggestions.length) {
            hideSuggestions();
            if (result.error) {
                console.warn('Maps autocomplete:', result.error);
            }
            return;
        }
        dropdown.innerHTML = suggestions.map(s => `
            <div class="autocomplete-item" data-place-id="${s.place_id}" data-description="${escapeHtml(s.description)}">
                <i class="fas fa-map-marker-alt"></i> ${escapeHtml(s.description)}
            </div>
        `).join('');
        dropdown.classList.remove('d-none');
        dropdown.querySelectorAll('.autocomplete-item').forEach(item => {
            item.addEventListener('click', () => selectLocation(item));
        });
    } catch (err) {
        hideSuggestions();
        console.warn('Autocomplete unavailable:', err.message);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function selectLocation(item) {
    const description = item.dataset.description;
    const placeId = item.dataset.placeId;
    document.getElementById('location').value = description;
    document.getElementById('placeId').value = placeId;
    hideSuggestions();

    try {
        const geo = await apiClient.geocodePlace(placeId, description);
        if (geo.latitude) document.getElementById('latitude').value = geo.latitude;
        if (geo.longitude) document.getElementById('longitude').value = geo.longitude;
        if (geo.formatted_address) document.getElementById('location').value = geo.formatted_address;
    } catch (err) {
        console.warn('Geocoding failed:', err);
    }
}

function hideSuggestions() {
    const dropdown = document.getElementById('locationSuggestions');
    dropdown.classList.add('d-none');
    dropdown.innerHTML = '';
}

async function submitComplaint() {
    const text = document.getElementById('complaintText').value.trim();
    const location = document.getElementById('location').value.trim();
    const language = document.getElementById('language').value || null;
    const category = document.getElementById('category').value || null;
    const lat = document.getElementById('latitude').value;
    const lng = document.getElementById('longitude').value;

    if (text.length < 10) { showError('Complaint description must be at least 10 characters'); return; }
    if (!location) { showError('Please enter a location'); return; }

    showLoading(true);
    hideError();

    try {
        const complaintData = { text, location, language, category };
        if (lat) complaintData.latitude = parseFloat(lat);
        if (lng) complaintData.longitude = parseFloat(lng);

        const response = await apiClient.submitComplaint(complaintData);
        if (response && response._id) {
            displaySuccessState(response);
        } else {
            showError('Failed to submit complaint');
        }
    } catch (error) {
        showError(error.message || 'Failed to submit complaint.');
    } finally {
        showLoading(false);
    }
}

function displaySuccessState(complaint) {
    document.getElementById('formSection').classList.add('d-none');
    document.getElementById('successSection').classList.remove('d-none');

    const trackingId = complaint.complaint_id || complaint._id;
    document.getElementById('complaintId').value = trackingId;
    document.getElementById('mongoId').value = complaint._id;

    if (complaint.category) document.getElementById('aiCategory').textContent = complaint.category;
    if (complaint.severity) {
        document.getElementById('aiSeverity').innerHTML =
            `<span class="badge bg-${getSeverityColor(complaint.severity)}">${complaint.severity}</span>`;
    }
    if (complaint.priority !== undefined) {
        const bar = document.getElementById('aiPriority');
        bar.style.width = `${complaint.priority}%`;
        bar.textContent = `${complaint.priority}/100`;
    }
    if (complaint.department) document.getElementById('aiDepartment').textContent = complaint.department;
    if (complaint.ai_confidence !== undefined) {
        document.getElementById('aiConfidence').textContent = `${Math.round(complaint.ai_confidence * 100)}%`;
    }
    if (complaint.ai_recommendation) document.getElementById('aiRecommendation').textContent = complaint.ai_recommendation;
}

function resetForm() {
    document.getElementById('complaintForm').reset();
    document.getElementById('charCount').textContent = '0';
    document.getElementById('latitude').value = '';
    document.getElementById('longitude').value = '';
    document.getElementById('placeId').value = '';
    document.getElementById('mongoId').value = '';
    document.getElementById('successSection').classList.add('d-none');
    document.getElementById('formSection').classList.remove('d-none');
}

async function copyComplaintId() {
    const input = document.getElementById('complaintId');
    const btn = document.getElementById('copyIdBtn');
    const id = input.value;

    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(id);
        } else {
            input.removeAttribute('readonly');
            input.select();
            input.setSelectionRange(0, id.length);
            document.execCommand('copy');
            input.setAttribute('readonly', 'readonly');
        }
        const original = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        btn.classList.replace('btn-outline-primary', 'btn-success');
        setTimeout(() => {
            btn.innerHTML = original;
            btn.classList.replace('btn-success', 'btn-outline-primary');
        }, 2000);
    } catch (err) {
        showError('Could not copy. Please select and copy the ID manually.');
    }
}

function trackComplaint() {
    const id = document.getElementById('complaintId').value;
    window.location.href = `track.html?id=${encodeURIComponent(id)}`;
}

function showLoading(show) {
    document.getElementById('formSection').style.opacity = show ? '0.5' : '1';
    document.getElementById('loadingSpinner').classList.toggle('d-none', !show);
}

function hideError() {
    document.getElementById('errorAlert')?.classList.add('d-none');
}
