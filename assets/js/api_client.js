/**
 * API Client for LeadGen Pro (Python Version)
 */

const API_BASE_URL = 'http://localhost:8000/api';

const ApiClient = {
    /**
     * Start a new search
     */
    async search(params) {
        try {
            const response = await fetch(`${API_BASE_URL}/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    keyword: params.keyword,
                    location: params.location,
                    country: params.country || 'India'
                })
            });
            if (!response.ok) throw new Error('Search failed');
            return await response.json();
        } catch (error) {
            console.error('Search error:', error);
            throw error;
        }
    },

    /**
     * Get Search History
     */
    async getHistory() {
        try {
            const response = await fetch(`${API_BASE_URL}/history`);
            if (!response.ok) throw new Error('History fetch failed');
            return await response.json();
        } catch (error) {
            console.error('History error:', error);
            throw error;
        }
    },

    /**
     * Export Leads to Excel
     */
    async exportLeads(leads) {
        try {
            const response = await fetch(`${API_BASE_URL}/export`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(leads)
            });

            if (!response.ok) throw new Error('Export failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `leads_${new Date().getTime()}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            return { success: true };
        } catch (error) {
            console.error('Export error:', error);
            throw error;
        }
    }
};
