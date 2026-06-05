/**
 * Single source of truth for navigation — equal spacing, Admin same as others.
 */
(function () {
    const path = window.location.pathname;

    function isActive(href) {
        if (href === '/') return path === '/' || path.endsWith('/index.html') || path === '';
        const page = href.replace(/^\//, '');
        return path.endsWith(page) || path === href;
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
                <a class="nav-link${isActive(l.href) ? ' active' : ''}" href="${l.href}">${l.label}</a>
            </li>
        `).join('');

        return `
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
            <div class="container-fluid navbar-inner">
                <a class="navbar-brand" href="/">
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
