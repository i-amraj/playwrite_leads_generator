/**
 * Raj Leads Generator - Theme & Layout Logic
 * Handles Sidebar toggle and Dark/Light theme switching.
 * Shared across all pages.
 */

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initTheme();
});

// --- Sidebar Logic ---
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');

    // Create overlay if not exists
    let overlay = document.querySelector('.sidebar-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);
    }

    if (!sidebar || !sidebarToggle) return;

    // Load desktop saved state
    if (window.innerWidth > 768) {
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed) sidebar.classList.add('collapsed');
    }

    // Toggle event
    sidebarToggle.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
            // Mobile: Toggle off-canvas
            sidebar.classList.toggle('mobile-open');
            overlay.classList.toggle('active');
        } else {
            // Desktop: Toggle collapse
            sidebar.classList.toggle('collapsed');
            const nowCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', nowCollapsed);
        }
    });

    // Close on overlay click (Mobile)
    overlay.addEventListener('click', () => {
        sidebar.classList.remove('mobile-open');
        overlay.classList.remove('active');
    });

    // Handle Resize
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('mobile-open');
            overlay.classList.remove('active');

            // Restore collapsed state
            const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
            sidebar.classList.toggle('collapsed', isCollapsed);
        }
    });
}

// --- Theme Logic ---
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');

    // Load saved state or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(themeToggle, savedTheme);

    if (!themeToggle) return;

    // Toggle event
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(themeToggle, newTheme);
    });
}

function updateThemeIcon(btn, theme) {
    if (!btn) return;
    const icon = btn.querySelector('i');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
    }
}
