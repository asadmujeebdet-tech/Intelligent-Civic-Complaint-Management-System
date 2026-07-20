const API_BASE_URL = (window.CIVICLENS_CONFIG && window.CIVICLENS_CONFIG.API_BASE_URL) || '/api/v1';

function isLocalhostApi() {
    return /^https?:\/\/(localhost|127\.0\.0\.1)/i.test(API_BASE_URL);
}

if (isLocalhostApi() && typeof window !== 'undefined' && window.location.hostname.includes('streamlit.app')) {
    console.error(
        '[CivicLens] API points to localhost inside Streamlit Cloud — use the /backend mount or set BACKEND_API_URL.'
    );
}

class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL.replace(/\/$/, '');
    }

    async request(endpoint, options = {}) {
        const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        const url = `${this.baseURL}${path}`;
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Error:', url, error);
            throw error;
        }
    }

    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async patch(endpoint, data) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    async submitComplaint(complaintData) {
        return this.post('/complaints/', complaintData);
    }

    async getComplaint(complaintId) {
        const response = await this.get(`/complaints/${complaintId}`);
        return response.data || response;
    }

    async getAllComplaints(params = {}) {
        const queryString = new URLSearchParams(
            Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ''))
        ).toString();
        const endpoint = `/complaints/${queryString ? '?' + queryString : ''}`;
        return this.get(endpoint);
    }

    async updateComplaint(complaintId, updateData) {
        return this.patch(`/complaints/${complaintId}`, updateData);
    }

    async submitFeedback(complaintId, feedback) {
        return this.post(`/complaints/${complaintId}/feedback`, feedback);
    }

    async getStatusHistory(complaintId) {
        const response = await this.get(`/complaints/${complaintId}/history`);
        return response.data || [];
    }

    async getDashboardStats() {
        return this.get('/complaints/analytics/dashboard');
    }

    async getAIInsights() {
        return this.get('/complaints/analytics/insights');
    }

    async getPlacesAutocomplete(query) {
        return this.get(`/maps/autocomplete?q=${encodeURIComponent(query)}`);
    }

    async geocodePlace(placeId, address) {
        const params = new URLSearchParams();
        if (placeId) params.set('place_id', placeId);
        if (address) params.set('address', address);
        const response = await this.get(`/maps/geocode?${params}`);
        return response.data || {};
    }

    async chatWithAI(question) {
        const response = await this.post('/chatbot/chat', { question });
        return response.answer;
    }
}

const apiClient = new APIClient();

function showError(message) {
    const msg = message || 'Service temporarily unavailable.';
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    if (errorAlert && errorMessage) {
        errorMessage.textContent = msg;
        errorAlert.classList.remove('d-none');
        setTimeout(() => errorAlert.classList.add('d-none'), 5000);
    } else {
        console.error(msg);
    }
}

function getSeverityColor(severity) {
    const map = { Low: 'success', Medium: 'warning', High: 'danger', Critical: 'danger' };
    return map[severity] || 'secondary';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'N/A';
    return date.toLocaleString(undefined, {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: true,
    });
}

function formatStatus(status) {
    const map = {
        open: 'Open', 'in-progress': 'In Progress', resolved: 'Resolved',
        Open: 'Open', 'Under Review': 'Under Review', Assigned: 'Assigned',
        'In Progress': 'In Progress', Resolved: 'Resolved', Closed: 'Closed',
    };
    return map[status] || status;
}

function getStatusColor(status) {
    const normalized = formatStatus(status);
    const map = {
        Open: 'danger', 'Under Review': 'info', Assigned: 'primary',
        'In Progress': 'warning', Resolved: 'success', Closed: 'secondary',
    };
    return map[normalized] || 'secondary';
}
