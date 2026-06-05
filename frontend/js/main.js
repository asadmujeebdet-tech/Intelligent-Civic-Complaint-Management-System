// Main JavaScript Utilities

/**
 * Load home page statistics
 */
async function loadHomeStats() {
    try {
        const stats = await apiClient.getDashboardStats();
        
        const totalElement = document.getElementById('total-complaints');
        const resolvedElement = document.getElementById('resolved-complaints');
        const activeElement = document.getElementById('active-complaints');
        
        if (totalElement) {
            totalElement.textContent = stats.total_complaints || 0;
        }
        if (resolvedElement) {
            resolvedElement.textContent = stats.resolved_complaints || 0;
        }
        if (activeElement) {
            activeElement.textContent = (stats.total_complaints - stats.resolved_complaints) || 0;
        }

        // Calculate percentages
        const total = stats.total_complaints || 1;
        const resolved = stats.resolved_complaints || 0;
        const percent = Math.round((resolved / total) * 100);
        
        const totalPercentElement = document.getElementById('total-percent');
        const resolvedPercentElement = document.getElementById('resolved-percent');
        
        if (totalPercentElement) {
            totalPercentElement.textContent = '+0% this month';
        }
        if (resolvedPercentElement) {
            resolvedPercentElement.textContent = `${percent}% rate`;
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

/**
 * Format a date string to readable format
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Get CSS class for severity level
 */
function getSeverityColor(severity) {
    const colorMap = {
        'Low': 'success',
        'Medium': 'warning',
        'High': 'danger',
        'Critical': 'danger'
    };
    return colorMap[severity] || 'secondary';
}

/**
 * Get CSS class for status
 */
function getStatusColor(status) {
    const colorMap = {
        'open': 'danger',
        'in-progress': 'warning',
        'resolved': 'success'
    };
    return colorMap[status] || 'secondary';
}

/**
 * Format status display text
 */
function formatStatus(status) {
    const statusMap = {
        'open': 'Open',
        'in-progress': 'In Progress',
        'resolved': 'Resolved'
    };
    return statusMap[status] || status;
}

/**
 * Show error message to user
 */
function showError(message) {
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    
    if (errorAlert && errorMessage) {
        errorMessage.textContent = message;
        errorAlert.classList.remove('d-none');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorAlert.classList.add('d-none');
        }, 5000);
    }
}

/**
 * Hide error message
 */
function hideError() {
    const errorAlert = document.getElementById('errorAlert');
    if (errorAlert) {
        errorAlert.classList.add('d-none');
    }
}

/**
 * Show loading spinner
 */
function showLoadingSpinner(show = true) {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.classList.toggle('d-none', !show);
    }
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text, buttonElement) {
    navigator.clipboard.writeText(text).then(() => {
        if (buttonElement) {
            const originalHTML = buttonElement.innerHTML;
            buttonElement.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => {
                buttonElement.innerHTML = originalHTML;
            }, 2000);
        }
    }).catch(err => {
        console.error('Failed to copy:', err);
        showError('Failed to copy to clipboard');
    });
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Validate phone number
 */
function isValidPhone(phone) {
    const regex = /^[\d\s\-\+\(\)]+$/;
    return regex.test(phone);
}

/**
 * Debounce function for input handlers
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function for scroll/resize handlers
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Check if element is in viewport
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Scroll to element smoothly
 */
function scrollToElement(element) {
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Get URL parameters
 */
function getURLParam(paramName) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(paramName);
}

/**
 * Set URL parameters without reload
 */
function setURLParam(paramName, paramValue) {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set(paramName, paramValue);
    window.history.replaceState({}, '', `${window.location.pathname}?${urlParams}`);
}

/**
 * Initialize tooltip (Bootstrap)
 */
function initTooltip(element) {
    if (typeof bootstrap !== 'undefined') {
        return new bootstrap.Tooltip(element);
    }
}

/**
 * Initialize popover (Bootstrap)
 */
function initPopover(element) {
    if (typeof bootstrap !== 'undefined') {
        return new bootstrap.Popover(element);
    }
}

/**
 * Show modal (Bootstrap)
 */
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal && typeof bootstrap !== 'undefined') {
        new bootstrap.Modal(modal).show();
    }
}

/**
 * Hide modal (Bootstrap)
 */
function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal && typeof bootstrap !== 'undefined') {
        bootstrap.Modal.getInstance(modal)?.hide();
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
        initTooltip(el);
    });
    
    // Initialize all popovers
    document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
        initPopover(el);
    });
});
