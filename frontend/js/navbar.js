/**
 * Single source of truth for navigation — equal spacing, Admin same as others.
 * BASE_PATH supports same-origin mount under Streamlit (/backend) without UI changes.
 */
(function () {
    function getBase() {
        const cfg = window.CIVICLENS_CONFIG || {};
        return String(cfg.BASE_PATH || '').replace(/\/$/, '');
    }

    function hrefFor(page) {
        const BASE = getBase();
        if (page === '/') {
            return BASE ? `${BASE}/` : '/';
        }
        const name = page.replace(/^\//, '');
        return BASE ? `${BASE}/${name}` : `/${name}`;
    }

    function isActive(href) {
        const path = window.location.pathname;
        const BASE = getBase();
        const target = hrefFor(href);
        if (href === '/') {
            return (
                path === target ||
                path === `${BASE}/` ||
                path === BASE ||
                path.endsWith('/index.html') ||
                path === '/' ||
                path === ''
            );
        }
        const page = href.replace(/^\//, '');
        return path.endsWith(page) || path === target;
    }

    const links = [
        { href: '/', label: 'Home' },
        { href: '/submit.html', label: 'Report Issue' },
        { href: '/track.html', label: 'Track Status' },
        { href: '/dashboard.html', label: 'Analytics' },
        { href: '/admin.html', label: 'Admin' },
    ];

    function buildNavbar() {
        const items = links.map(l => `
            <li class="nav-item">
                <a class="nav-link${isActive(l.href) ? ' active' : ''}" href="${hrefFor(l.href)}">${l.label}</a>
            </li>
        `).join('');

        return `
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
            <div class="container-fluid navbar-inner">
                <a class="navbar-brand" href="${hrefFor('/')}">
                    <i class="fas fa-landmark"></i> CivicLens AI
                </a>
                <div class="collapse navbar-collapse navbar-links-wrap" id="navbarNav">
                    <ul class="navbar-nav navbar-nav-equal">${items}</ul>
                </div>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                    data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false"
                    aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
            </div>
        </nav>`;
    }

    function injectNavbar() {
        const existing = document.querySelector('nav.navbar');
        if (existing) {
            existing.outerHTML = buildNavbar();
        } else {
            document.body.insertAdjacentHTML('afterbegin', buildNavbar());
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectNavbar);
    } else {
        injectNavbar();
    }
})();
