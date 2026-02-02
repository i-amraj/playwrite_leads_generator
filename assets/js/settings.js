/**
 * Settings Page Logic
 * Manages user configuration
 */

document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('settingsForm');

    // Load Settings
    try {
        const response = await fetch('backend/php/api/get_settings.php');
        const result = await response.json();

        if (result.success) {
            populateForm(result.data);
        }
    } catch (error) {
        console.error('Failed to load settings:', error);
        showToast('Failed to load settings', 'error');
    }

    // Save Settings
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(form);
            const settings = Object.fromEntries(formData.entries());

            // Handle checkboxes (unchecked ones don't appear in FormData)
            settings.notifications = form.querySelector('[name="notifications"]').checked;
            settings.auto_scroll = form.querySelector('[name="auto_scroll"]').checked;

            try {
                const btn = form.querySelector('button[type="submit"]');
                const originalText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
                btn.disabled = true;

                const response = await fetch('backend/php/api/save_settings.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(settings)
                });

                const result = await response.json();

                if (result.success) {
                    showToast('Settings saved successfully', 'success');
                    // Apply theme immediately if changed
                    if (settings.theme) {
                        // Theme logic is handled by theme.js but we can trigger a reload or event if needed
                        // For now, simple toast is enough
                    }
                } else {
                    showToast('Failed to save settings', 'error');
                }
            } catch (error) {
                console.error('Save settings error:', error);
                showToast('An error occurred', 'error');
            } finally {
                const btn = form.querySelector('button[type="submit"]');
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
    }
});

function populateForm(settings) {
    const form = document.getElementById('settingsForm');
    if (!form) return;

    if (settings.theme) {
        const themeSelect = form.querySelector('[name="theme"]');
        if (themeSelect) themeSelect.value = settings.theme;
    }

    if (settings.export_format) {
        const formatSelect = form.querySelector('[name="export_format"]');
        if (formatSelect) formatSelect.value = settings.export_format;
    }

    if (settings.notifications !== undefined) {
        const notifCheck = form.querySelector('[name="notifications"]');
        if (notifCheck) notifCheck.checked = settings.notifications;
    }

    if (settings.auto_scroll !== undefined) {
        const scrollCheck = form.querySelector('[name="auto_scroll"]');
        if (scrollCheck) scrollCheck.checked = settings.auto_scroll;
    }
}
