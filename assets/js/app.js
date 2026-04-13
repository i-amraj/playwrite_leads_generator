/**
 * LeadGen Pro Main Application Logic
 * Terminal-style live scraping with real-time updates
 */

document.addEventListener('DOMContentLoaded', () => {
    // State Management
    const state = {
        currentSessionId: null,
        extractedCount: 0,
        totalAvailable: 0,
        isScraping: false,
        countryData: null,
        lastQuery: null,
        settings: { batch_size: 10, delay: 5 },
        startTime: null,
        timerInterval: null,
        leads: [] // Store leads for export
    };

    // DOM Elements
    const elements = {
        searchForm: document.getElementById('searchForm'),
        countrySelect: document.getElementById('country'),
        stateSelect: document.getElementById('state'),
        citySelect: document.getElementById('district'),
        areaSelect: document.getElementById('city'),
        keywordInput: document.getElementById('keyword'),
        searchBtn: document.getElementById('searchBtn'),

        // Scraping Panel Elements
        loadingOverlay: document.getElementById('loadingOverlay'),
        terminalLog: document.getElementById('terminalLog'),
        statusText: document.getElementById('statusText'),
        scrapingQuery: document.getElementById('scrapingQuery'),
        scrapingTime: document.getElementById('scrapingTime'),
        liveExtracted: document.getElementById('liveExtracted'),
        liveTotal: document.getElementById('liveTotal'),
        liveDelay: document.getElementById('liveDelay'),
        scrapingProgressBar: document.getElementById('scrapingProgressBar'),

        // Results Section
        emptyState: document.getElementById('emptyState'),
        resultsSection: document.getElementById('resultsSection'),
        resultsBody: document.getElementById('resultsBody'),
        extractedCount: document.getElementById('extractedCount'),
        totalAvailable: document.getElementById('totalAvailable'),
        progressBar: document.getElementById('progressBar'),
        currentLocation: document.getElementById('currentLocation'),

        getMoreBtn: document.getElementById('getMoreBtn'),
        exportBtn: document.getElementById('exportBtn'),
        paginationStatus: document.getElementById('paginationStatus'),
        countdown: document.getElementById('countdown')
    };

    // ===============================
    // TERMINAL LOGGING
    // ===============================
    function log(message, type = '') {
        if (!elements.terminalLog) return;

        const line = document.createElement('div');
        line.className = `log-line ${type}`;
        line.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        elements.terminalLog.appendChild(line);
        elements.terminalLog.scrollTop = elements.terminalLog.scrollHeight;
    }

    function clearLog() {
        if (elements.terminalLog) {
            elements.terminalLog.innerHTML = '';
        }
    }

    function updateStatus(text) {
        if (elements.statusText) {
            elements.statusText.textContent = text;
        }
    }

    function updateLiveStats(extracted, total, delay = '--') {
        if (elements.liveExtracted) elements.liveExtracted.textContent = extracted;
        if (elements.liveTotal) elements.liveTotal.textContent = total;
        if (elements.liveDelay) elements.liveDelay.textContent = delay;

        if (elements.scrapingProgressBar && total > 0) {
            const pct = Math.min((extracted / total) * 100, 100);
            elements.scrapingProgressBar.style.width = `${pct}%`;
        }
    }

    // Timer
    function startTimer() {
        state.startTime = Date.now();
        state.timerInterval = setInterval(() => {
            if (elements.scrapingTime) {
                const elapsed = Math.floor((Date.now() - state.startTime) / 1000);
                const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
                const secs = (elapsed % 60).toString().padStart(2, '0');
                elements.scrapingTime.textContent = `${mins}:${secs}`;
            }
        }, 1000);
    }

    function stopTimer() {
        if (state.timerInterval) {
            clearInterval(state.timerInterval);
            state.timerInterval = null;
        }
    }

    // ===============================
    // INITIALIZE
    // ===============================
    async function init() {
        console.log('[APP] Initializing...');

        try {
            const settingsResponse = await fetch('/api/health'); // Just check health for now
            // Settings logic can be expanded here if needed
            state.settings = { batch_size: 20, delay: 3 }; 
        } catch (e) {
            console.warn('[APP] Failed to load settings, using defaults');
        }

        elements.countrySelect.addEventListener('change', async (e) => {
            await loadCountryData(e.target.value);
            updateStateDropdown();
        });

        elements.stateSelect.addEventListener('change', () => updateCityDropdown());
        elements.citySelect.addEventListener('change', () => updateAreaDropdown());

        await loadCountryData(elements.countrySelect.value || 'India');
        updateStateDropdown();

        setupSearchFormHandler();
        console.log('[APP] Initialization complete');
    }

    // ===============================
    // LOCATION DATA FUNCTIONS
    // ===============================
    async function loadCountryData(countryName) {
        try {
            const fileName = countryName.toLowerCase() === 'india'
                ? 'india-locations.json'
                : 'nepal-locations.json';

            const response = await fetch(`public/${fileName}`);
            if (!response.ok) throw new Error('Failed to load location data');

            state.countryData = await response.json();
        } catch (error) {
            console.error('[APP] Error loading country data:', error);
            showToast('Failed to load location data', 'error');
            state.countryData = null;
        }
    }

    function updateStateDropdown() {
        elements.stateSelect.innerHTML = '<option value="">Select State</option>';
        elements.citySelect.innerHTML = '<option value="">Select City</option>';
        elements.areaSelect.innerHTML = '<option value="">Select Area (Optional)</option>';

        elements.stateSelect.disabled = true;
        elements.citySelect.disabled = true;
        elements.areaSelect.disabled = true;

        if (!state.countryData?.states) return;

        state.countryData.states.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.code;
            opt.textContent = s.name;
            opt.dataset.name = s.name;
            elements.stateSelect.appendChild(opt);
        });

        elements.stateSelect.disabled = false;
    }

    function updateCityDropdown() {
        elements.citySelect.innerHTML = '<option value="">Select City</option>';
        elements.areaSelect.innerHTML = '<option value="">Select Area (Optional)</option>';

        elements.citySelect.disabled = true;
        elements.areaSelect.disabled = true;

        const stateCode = elements.stateSelect.value;
        if (!stateCode || !state.countryData?.districts) return;

        const cities = state.countryData.districts[stateCode] || [];

        cities.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.name.replace(/\s+/g, '_');
            opt.textContent = c.name;
            opt.dataset.name = c.name;
            elements.citySelect.appendChild(opt);
        });

        elements.citySelect.disabled = cities.length === 0;
    }

    function updateAreaDropdown() {
        elements.areaSelect.innerHTML = '<option value="">Select Area (Optional)</option>';
        elements.areaSelect.disabled = true;

        const stateCode = elements.stateSelect.value;
        const cityValue = elements.citySelect.value;

        if (!stateCode || !cityValue || !state.countryData?.areas) return;

        const areaKey = `${stateCode}__${cityValue}`;
        const areas = state.countryData.areas[areaKey] || [];

        areas.forEach(a => {
            const opt = document.createElement('option');
            opt.value = a.name;
            opt.textContent = a.name;
            elements.areaSelect.appendChild(opt);
        });

        elements.areaSelect.disabled = areas.length === 0;
    }

    // ===============================
    // SEARCH FORM HANDLER
    // ===============================
    function setupSearchFormHandler() {
        elements.searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const keyword = elements.keywordInput.value.trim();
            if (!keyword) {
                showToast('Please enter a business type', 'error');
                return;
            }

            const stateOpt = elements.stateSelect.selectedOptions[0];
            if (!stateOpt?.value) {
                showToast('Please select a State', 'error');
                return;
            }

            const cityOpt = elements.citySelect.selectedOptions[0];
            if (!cityOpt?.value) {
                showToast('Please select a City', 'error');
                return;
            }

            const areaOpt = elements.areaSelect.selectedOptions[0];

            const stateName = stateOpt.dataset.name || stateOpt.text;
            const cityName = cityOpt.dataset.name || cityOpt.text;

            let location = '';
            if (areaOpt && areaOpt.value) {
                // Specific Area: "Indira Nagar, Kanpur Nagar, Uttar Pradesh"
                location = `${areaOpt.value}, ${cityName}, ${stateName}`;
            } else {
                // City Level: "Kanpur Nagar, Uttar Pradesh"
                location = `${cityName}, ${stateName}`;
            }

            const country = elements.countrySelect.value || 'India';
            const limit = parseInt(state.settings?.batch_size) || 20;

            // Get Sales Info - Added Inputs
            const salesPerson = document.getElementById('salesPerson')?.value.trim();
            const salesTeam = document.getElementById('salesTeam')?.value.trim();

            if (!salesPerson || !salesTeam) {
                showToast('Please fill in Sales Person and Sales Team', 'error');
                return;
            }

            await performSearch({
                keyword,
                location,
                country,
                limit,
                salesPerson,
                salesTeam
            });
        });
    }

    async function performSearch(params) {
        // Show scraping panel
        showScrapingPanel(params);
        state.isScraping = true;
        state.lastQuery = params;

        // Reset
        state.extractedCount = 0,
        state.totalAvailable = 0,
        state.leads = [];
        elements.resultsBody.innerHTML = '';

        try {
            // Simulate terminal-style progress
            log('🚀 Starting Google Maps Lead Generator', 'info');
            await sleep(300);

            log(`📍 Query: ${params.keyword} in ${params.location}`, 'info');
            await sleep(200);

            log(`📊 Limit: ${params.limit} businesses`, 'info');
            await sleep(200);

            updateStatus('Launching browser...');
            log('[STEP 1/5] Launching browser...', 'info');
            await sleep(500);

            updateStatus('Searching Google Maps...');
            log(`[STEP 2/5] Searching for: ${params.keyword} in ${params.location}`, 'info');
            await sleep(400);

            updateStatus('Loading results...');
            log('[STEP 3/5] Scrolling for more results...', 'info');

            // Actual API call
            const result = await ApiClient.search(params);

            if (result.success) {
                state.currentSessionId = result.session_id;
                state.totalAvailable = result.total_found || result.total_available || result.data?.length || 0;

                // --- CASE 1: RESTORED FROM HISTORY ---
                if (result.restored) {
                    log(`[INFO] Restored session from history`, 'success');
                    updateStatus('Restoring data...');
                    await sleep(500);

                    // Render all at once (no slow streaming)
                    if (result.data) {
                        state.leads = result.data;
                        result.data.forEach((item, i) => {
                            const row = createResultRow(item, i + 1);
                            elements.resultsBody.appendChild(row);
                        });
                        state.extractedCount = result.data.length;
                    }

                    hideScrapingPanel();
                    showResults(params);
                    showToast(`Loaded ${state.extractedCount} results from history. Use "Get More" for new.`, 'info');

                }
                // --- CASE 2: LIVE EXTRACTION ---
                else {
                    log(`[INFO] Found ${state.totalAvailable} businesses`, 'success');
                    updateLiveStats(0, state.totalAvailable);

                    updateStatus('Extracting data...');
                    log('[STEP 4/5] Getting business cards...', 'info');
                    await sleep(300);

                    log(`[STEP 5/5] Extracting data (limit: ${params.limit})...`, 'info');

                    // Stream results with terminal logging
                    if (result.data && result.data.length > 0) {
                        await streamResultsLive(result.data);
                    }

                    log('═'.repeat(40), 'success');
                    log('✅ EXTRACTION COMPLETE', 'success');
                    log('═'.repeat(40), 'success');
                    log(`📊 Total Businesses: ${state.extractedCount}`, 'success');

                    // Small delay before hiding panel
                    await sleep(1000);

                    // Hide panel and show results
                    hideScrapingPanel();
                    showResults(params);

                    showToast(`Extracted ${state.extractedCount} of ${state.totalAvailable} results!`, 'success');
                }
            } else {
                log(`❌ Error: ${result.error || 'Search failed'}`, 'error');
                hideScrapingPanel();
                showToast(result.error || 'Search failed', 'error');
            }
        } catch (error) {
            console.error('[APP] Search error:', error);
            log(`❌ Error: ${error.message}`, 'error');
            hideScrapingPanel();
            showToast('Search failed. Please try again.', 'error');
        } finally {
            state.isScraping = false;
        }
    }

    // ===============================
    // STREAMING RESULTS WITH LOG
    // ===============================
    async function streamResultsLive(data) {
        for (let i = 0; i < data.length; i++) {
            const item = data[i];

            // Add to table
            const row = createResultRow(item, i + 1);
            row.classList.add('streaming-row');
            elements.resultsBody.appendChild(row);

            // Store in state
            state.leads.push(item);

            // Log business name
            log(`📍 ${item.name || 'Unknown Business'}`, 'data');

            // Update live stats
            state.extractedCount = i + 1;
            updateLiveStats(state.extractedCount, state.totalAvailable);

            // Delay for streaming effect
            await sleep(100);
        }
    }

    function createResultRow(item, index) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td data-label="#">${index}</td>
            <td data-label="Business"><strong>${item.name || 'N/A'}</strong></td>
            <td data-label="Category"><span class="badge">${item.category || 'N/A'}</span></td>
            <td data-label="Rating"><i class="fas fa-star" style="color:#f59e0b"></i> ${item.rating || 'N/A'}</td>
            <td data-label="Phone"><a href="tel:${item.phone}" class="tel-link">${item.phone || 'N/A'}</a></td>
            <td data-label="Website">${item.website ? `<a href="${item.website}" target="_blank" class="web-link"><i class="fas fa-external-link-alt"></i></a>` : 'N/A'}</td>
            <td data-label="Address" class="address-cell">${item.address || 'N/A'}</td>
        `;
        return row;
    }

    // ===============================
    // PANEL HELPERS
    // ===============================
    function showScrapingPanel(params) {
        clearLog();
        startTimer();

        if (elements.scrapingQuery) {
            elements.scrapingQuery.textContent = `${params.keyword} in ${params.location}`;
        }
        updateLiveStats(0, '--', '--');
        updateStatus('Initializing...');

        elements.loadingOverlay.classList.remove('hidden');
        elements.searchBtn.disabled = true;
        elements.searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scraping...';
    }

    function hideScrapingPanel() {
        stopTimer();
        elements.loadingOverlay.classList.add('hidden');
        elements.searchBtn.disabled = false;
        elements.searchBtn.innerHTML = '<i class="fas fa-magnifying-glass"></i> Start Searching';
    }

    function showResults(params) {
        elements.emptyState.classList.add('hidden');
        elements.resultsSection.classList.remove('hidden');

        if (elements.currentLocation) {
            elements.currentLocation.textContent = `${params.location}, ${params.country}`;
        }
        if (elements.extractedCount) {
            elements.extractedCount.textContent = state.extractedCount;
        }
        if (elements.totalAvailable) {
            elements.totalAvailable.textContent = state.totalAvailable;
        }
        if (elements.progressBar) {
            const pct = state.totalAvailable > 0 ? (state.extractedCount / state.totalAvailable) * 100 : 0;
            elements.progressBar.style.width = `${pct}%`;
        }

        elements.getMoreBtn.disabled = state.extractedCount >= state.totalAvailable;
        elements.exportBtn.disabled = false;
    }

    // ===============================
    // GET MORE HANDLER
    // ===============================
    if (elements.getMoreBtn) {
        elements.getMoreBtn.addEventListener('click', async () => {
            if (!state.currentSessionId || state.isScraping) return;

            try {
                // Show scraping panel with Resume context
                showScrapingPanel({
                    keyword: state.lastQuery?.keyword || 'Resuming',
                    location: state.lastQuery?.location || 'Session'
                });

                state.isScraping = true;

                // Restore current stats in panel
                updateLiveStats(state.extractedCount, state.totalAvailable);
                updateStatus('Resuming session...');

                log('🔄 Resuming search session...', 'info');
                await sleep(500);

                const batchSize = parseInt(state.settings?.batch_size) || 20; // Default to larger batch for get more
                log(`📊 Fetching next batch of ${batchSize} results...`, 'info');

                // Countdown simulated in log/status instead of simple text
                const delayTime = parseInt(state.settings?.delay) || 5;

                if (delayTime > 0) {
                    log(`⏳ Waiting ${delayTime}s delay (human-like behavior)...`, 'warning');
                    for (let i = delayTime; i > 0; i--) {
                        updateStatus(`Waiting ${i}s...`);
                        if (elements.liveDelay) elements.liveDelay.textContent = `${i}s`;
                        await sleep(1000);
                    }
                    if (elements.liveDelay) elements.liveDelay.textContent = '0s';
                }

                updateStatus('Extracting more data...');
                log('[STEP 1/2] Scroll & Extract...', 'info');

                // Add animated progress messages while waiting for API
                let dotCount = 0;
                const progressMessages = [
                    'Scrolling Google Maps results',
                    'Loading more businesses',
                    'Extracting business details',
                    'Processing data'
                ];
                let msgIndex = 0;

                // Show animated progress while API is running
                const progressInterval = setInterval(() => {
                    dotCount = (dotCount + 1) % 4;
                    const dots = '.'.repeat(dotCount);
                    const msg = progressMessages[msgIndex % progressMessages.length];
                    updateStatus(`${msg}${dots}`);

                    // Cycle through messages every 3 iterations
                    if (dotCount === 0) {
                        msgIndex++;
                        if (msgIndex % progressMessages.length === 0) {
                            log(`🔍 ${msg}...`, 'info');
                        }
                    }
                }, 500);

                const result = await ApiClient.getMore(state.currentSessionId, batchSize);

                // Stop animation
                clearInterval(progressInterval);

                if (result.success) {
                    // Update total if backend provides new info - DISABLED PER USER REQUEST
                    // We want to keep the initial "Total Available" count fixed so user sees "20 of 120", then "40 of 120".
                    /*
                    if (result.total_available || result.total_count) {
                        state.totalAvailable = result.total_available || result.total_count;
                        log(`[INFO] Total available updated: ${state.totalAvailable}`, 'success');
                    }
                    */

                    log(`[INFO] Extracted ${result.data?.length || 0} new records`, 'success');

                    if (result.data && result.data.length > 0) {
                        const startIdx = state.extractedCount; // Keep track of continuous index

                        log(`[STEP 2/2] Processing data...`, 'info');

                        // Stream results using the same visual logic
                        // streamResultsLive uses 'state.extractedCount' internally to update global count
                        // We need to ensure logic flow is correct.
                        // streamResultsLive appends to table. Table is hidden but DOM operation works.

                        for (let i = 0; i < result.data.length; i++) {
                            const item = result.data[i];

                            // Add to table
                            const row = createResultRow(item, state.extractedCount + 1);
                            row.classList.add('streaming-row');
                            elements.resultsBody.appendChild(row);

                            // Store in state
                            state.leads.push(item);

                            // Log business name
                            log(`📍 ${item.name || 'Unknown Business'}`, 'data');

                            // Update live stats
                            state.extractedCount++;
                            updateLiveStats(state.extractedCount, state.totalAvailable);

                            // Delay for streaming effect
                            await sleep(100);
                        }
                    }

                    log('═'.repeat(40), 'success');
                    log('✅ BATCH COMPLETE', 'success');
                    log('═'.repeat(40), 'success');

                    await sleep(1000);

                    // Update Main UI Stats
                    if (elements.totalAvailable) elements.totalAvailable.textContent = state.totalAvailable;
                    if (elements.extractedCount) elements.extractedCount.textContent = state.extractedCount;
                    if (elements.progressBar) {
                        const pct = state.totalAvailable > 0 ? (state.extractedCount / state.totalAvailable) * 100 : 0;
                        elements.progressBar.style.width = `${pct}%`;
                    }

                    elements.getMoreBtn.disabled = !result.has_more;

                    hideScrapingPanel();
                    showResults(state.lastQuery); // Ensure results view is active/updated
                    showToast(`Added ${result.new_count || result.data.length} new results!`, 'success');

                } else {
                    log(`❌ Error: ${result.message || 'Failed to get more'}`, 'error');
                    await sleep(2000);
                    hideScrapingPanel();
                    showToast(result.message || 'Failed to get more results', 'error');
                    elements.getMoreBtn.disabled = false;
                }
            } catch (error) {
                console.error('[APP] Get more error:', error);
                log(`❌ Critical Error: ${error.message}`, 'error');
                await sleep(2000);
                hideScrapingPanel();
                showToast('Error loading more results.', 'error');
                elements.getMoreBtn.disabled = false;
            } finally {
                state.isScraping = false;
            }
        });
    }

    // ===============================
    // EXPORT HANDLER
    // ===============================
    if (elements.exportBtn) {
        elements.exportBtn.addEventListener('click', async () => {
            if (!state.currentSessionId) {
                showToast('No data to export', 'error');
                return;
            }

            try {
                elements.exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Preparing...';
                elements.exportBtn.disabled = true;

                await ApiClient.exportExcel(state.leads);
                showToast('Export started successfully', 'success');
            } catch (error) {
                console.error('[APP] Export error:', error);
                showToast('Export failed.', 'error');
            } finally {
                elements.exportBtn.innerHTML = '<i class="fas fa-file-excel"></i> Export Excel';
                elements.exportBtn.disabled = false;
            }
        });
    }

    // ===============================
    // HELPERS
    // ===============================
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // ===============================
    // RUN INIT
    // ===============================
    init();
});
