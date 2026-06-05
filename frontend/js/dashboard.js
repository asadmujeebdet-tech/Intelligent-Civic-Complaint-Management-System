let charts = {};

async function loadDashboard(options = {}) {
    const { initial = false } = options;
    const loadingSpinner = document.getElementById('loadingSpinner');
    const dashboardContent = document.getElementById('dashboardContent');
    const refreshBtn = document.getElementById('refreshDashboardBtn');
    const refreshIcon = document.getElementById('refreshIcon');

    if (initial) {
        loadingSpinner.classList.remove('d-none');
        dashboardContent.classList.add('d-none');
    } else {
        if (refreshBtn) refreshBtn.disabled = true;
        if (refreshIcon) refreshIcon.classList.add('fa-spin');
    }

    try {
        const stats = await apiClient.getDashboardStats();
        renderDashboard(stats);
        dashboardContent.classList.remove('d-none');
        loadingSpinner.classList.add('d-none');
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        if (initial) {
            loadingSpinner.innerHTML = `
                <div class="alert alert-danger d-inline-block">
                    <i class="fas fa-exclamation-circle"></i> Failed to load dashboard. Please try again.
                </div>
            `;
        }
    } finally {
        if (refreshBtn) refreshBtn.disabled = false;
        if (refreshIcon) refreshIcon.classList.remove('fa-spin');
    }
}

function refreshDashboard() {
    loadDashboard({ initial: false });
}

function renderDashboard(stats) {
    const openCount = stats.open_complaints ?? stats.open_count ?? 0;
    const inProgressCount = stats.in_progress_complaints ?? stats.in_progress_count ?? 0;
    const resolvedCount = stats.resolved_complaints ?? stats.resolved_count ?? 0;

    document.getElementById('kpiTotal').textContent = stats.total_complaints || 0;
    document.getElementById('kpiOpen').textContent = openCount;
    document.getElementById('kpiProgress').textContent = inProgressCount;
    document.getElementById('kpiResolved').textContent = resolvedCount;
    document.getElementById('kpiCritical').textContent = stats.critical_count || 0;
    document.getElementById('kpiHighPriority').textContent = stats.high_priority_count || 0;

    document.getElementById('insightDuplicates').textContent = stats.duplicate_clusters || stats.duplicate_complaints || 0;

    const total = stats.total_complaints || 1;
    const resolutionRate = stats.resolved_percentage != null
        ? Math.round(stats.resolved_percentage)
        : Math.round((resolvedCount / total) * 100);
    document.getElementById('insightResolution').textContent = `${resolutionRate}%`;
    document.getElementById('insightSatisfaction').textContent = `${Math.round(stats.satisfaction_score || 0)}%`;
    document.getElementById('insightFeedback').textContent = stats.feedback_count || 0;

    renderCategoryChart(stats.category_breakdown || {});
    renderSeverityChart(stats.severity_breakdown || {});
    renderLocationsChart(stats.top_locations || []);
    renderStatusChart(stats.status_breakdown || {
        Open: openCount,
        'In Progress': inProgressCount,
        Resolved: resolvedCount,
    });
    renderTrendChart(stats.complaint_trend || []);
}

function destroyChart(key) {
    if (charts[key]) {
        charts[key].destroy();
        charts[key] = null;
    }
}

function renderCategoryChart(data) {
    destroyChart('category');
    const labels = Object.keys(data);
    charts.category = new Chart(document.getElementById('categoryChart'), {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Complaints',
                data: Object.values(data),
                backgroundColor: ['#2563EB', '#22C55E', '#F59E0B', '#EF4444', '#06B6D4', '#8B5CF6', '#EC4899'],
                borderRadius: 8,
            }],
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
        },
    });
}

function renderSeverityChart(data) {
    destroyChart('severity');
    const order = ['Low', 'Medium', 'High', 'Critical'];
    charts.severity = new Chart(document.getElementById('severityChart'), {
        type: 'doughnut',
        data: {
            labels: order,
            datasets: [{
                data: order.map(s => data[s] || 0),
                backgroundColor: ['#22C55E', '#F59E0B', '#EF4444', '#991B1B'],
            }],
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
    });
}

function renderLocationsChart(locations) {
    destroyChart('locations');
    const top = locations.slice(0, 8);
    const labels = top.map(l => l.location || l.name || 'Unknown');
    charts.locations = new Chart(document.getElementById('locationsChart'), {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Complaints',
                data: top.map(l => l.count || 0),
                backgroundColor: '#06B6D4',
                borderRadius: 8,
            }],
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
        },
    });
}

function renderStatusChart(data) {
    destroyChart('status');
    const labels = Object.keys(data).map(k => k.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()));
    const values = Object.values(data);
    charts.status = new Chart(document.getElementById('statusChart'), {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: ['#EF4444', '#F59E0B', '#22C55E', '#2563EB', '#64748B', '#8B5CF6'],
            }],
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
    });
}

function renderTrendChart(trend) {
    destroyChart('trend');
    charts.trend = new Chart(document.getElementById('trendChart'), {
        type: 'line',
        data: {
            labels: trend.map(t => t.date),
            datasets: [{
                label: 'Complaints',
                data: trend.map(t => t.count),
                borderColor: '#2563EB',
                backgroundColor: 'rgba(37, 99, 235, 0.12)',
                fill: true,
                tension: 0.35,
                pointRadius: 4,
                pointBackgroundColor: '#2563EB',
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
        },
    });
}
