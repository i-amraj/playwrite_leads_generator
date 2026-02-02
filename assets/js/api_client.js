/**
 * API Client for LeadGen Pro
 * Encapsulates all backend communication
 */

const API_BASE_URL = 'backend/php/api';

const ApiClient = {
    /**
     * Start a new search
     * @param {Object} params {keyword, location, country, limit}
     */
    async search(params) {
        try {
            const response = await fetch(`${API_BASE_URL}/search.php`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    keyword: params.keyword,
                    location: params.location,
                    country: params.country || 'India',
                    limit: params.limit || 20,
                    sales_person: params.salesPerson,
                    sales_team: params.salesTeam
                })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Search API error:', error);
            throw error;
        }
    },

    /**
     * Get next batch of results
     * @param {string} sessionId 
     * @param {number} batchSize 
     */
    async getMore(sessionId, batchSize = 20) {
        try {
            const response = await fetch(`${API_BASE_URL}/getmore.php`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    batch_size: batchSize
                })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Get More API error:', error);
            throw error;
        }
    },

    /**
     * Export data to Excel
     * @param {string} sessionId 
     */
    async exportExcel(sessionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/export.php`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`Export error: ${response.status}`);
            }

            // Handle binary download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');

            // Get filename from header if possible
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'leadgen_export.csv';
            if (contentDisposition && contentDisposition.indexOf('filename=') !== -1) {
                filename = contentDisposition.split('filename=')[1].replace(/"/g, '');
            }

            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            return true;
        } catch (error) {
            console.error('Export API error:', error);
            throw error;
        }
    },

    /**
     * Check session status
     * @param {string} sessionId 
     */
    async getStatus(sessionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/status.php?session_id=${sessionId}`);
            if (!response.ok) {
                throw new Error(`Status error: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Status API error:', error);
            throw error;
        }
    }
};
