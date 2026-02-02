/**
 * History Page Logic
 * Fetches and displays past search sessions
 */

document.addEventListener('DOMContentLoaded', async () => {
    const historyContainer = document.querySelector('.history-section .glassy');

    // Initial State
    historyContainer.innerHTML = `
        <div style="text-align: center; padding: 4rem 2rem;">
            <i class="fas fa-spinner fa-spin" style="font-size: 3rem; color: var(--primary); margin-bottom: 1rem;"></i>
            <h3>Loading History...</h3>
        </div>
    `;

    try {
        const response = await fetch('backend/php/api/get_history.php');
        const result = await response.json();

        if (result.success && result.data.length > 0) {
            renderHistoryTable(result.data, historyContainer);
        } else {
            renderEmptyState(historyContainer);
        }
    } catch (error) {
        console.error('Failed to load history:', error);
        historyContainer.innerHTML = `
            <div style="text-align: center; padding: 4rem 2rem;">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: var(--danger); margin-bottom: 1rem;"></i>
                <h3>Failed to load history</h3>
                <p>Please try again later.</p>
            </div>
        `;
    }
});

function renderHistoryTable(data, container) {
    let html = `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Keyword</th>
                        <th>Location</th>
                        <th>Total Leads</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;

    data.forEach(item => {
        html += `
            <tr>
                <td>${formatDate(item.date)}</td>
                <td><strong>${item.keyword}</strong></td>
                <td>${item.location}, ${item.country}</td>
                <td>${item.total_leads}</td>
                <td><span class="badge success">${item.status}</span></td>
                <td>
                    <button class="btn-icon" onclick="downloadSession('${item.session_id}')" title="Download Excel">
                        <i class="fas fa-download"></i>
                    </button>
                    <!-- Future: Add 'Resume' button -->
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

function renderEmptyState(container) {
    container.innerHTML = `
        <div style="text-align: center; padding: 4rem 2rem;">
            <i class="fas fa-folder-open" style="font-size: 3rem; color: var(--text-muted); margin-bottom: 1rem;"></i>
            <h3>No Search History</h3>
            <p style="color: var(--text-muted);">Your past sessions will appear here.</p>
            <br>
            <a href="index.html" class="btn btn-primary">Start New Search</a>
        </div>
    `;
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Global function for download action
window.downloadSession = async (sessionId) => {
    try {
        showToast('Preparing download...', 'info');
        // Re-use logic from api_client if possible, or simple fetch
        // For now, simple redirect/fetch for download
        const response = await fetch('backend/php/api/export.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });

        if (!response.ok) throw new Error('Export failed');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `leads_${sessionId}.csv`; // Ideally get filename from header
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showToast('Download started', 'success');
    } catch (error) {
        showToast('Failed to download session', 'error');
        console.error(error);
    }
};
