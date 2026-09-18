/**
 * AI-Based Software Requirement Analyzer — Frontend Application Controller
 * High-performance vanilla JavaScript with state management, view routing,
 * real-time API integrations, Chart.js analytics, and interactive inspectors.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Determine API Base URL (auto-connect to http://127.0.0.1:8000 when opened via file:// or non-8000 ports)
    const API_BASE = (window.location.protocol === 'file:' || !window.location.port || window.location.port !== '8000') 
        ? 'http://127.0.0.1:8000' 
        : '';

    // ==========================================
    // 1. APPLICATION STATE & VARIABLES
    // ==========================================
    const state = {
        currentView: 'landing',
        activeAnalysis: null,
        historicalAnalyses: [],
        historyStats: null,
        selectedFile: null,
        // Requirements Table State
        reqSearchQuery: '',
        reqFilterClass: 'ALL',
        reqFilterAmbiguity: 'ALL',
        reqFilterQuality: 'ALL',
        reqSortColumn: 'id',
        reqSortOrder: 'asc',
        reqCurrentPage: 1,
        reqPageSize: 10,
        // Chart Instances
        charts: {
            globalDist: null,
            resultsDist: null,
            resultsRadar: null
        }
    };

    // ==========================================
    // 2. DOM ELEMENT REFERENCES
    // ==========================================
    const sidebar = document.getElementById('sidebar');
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenuClose = document.getElementById('mobile-menu-close');
    const navItems = document.querySelectorAll('.sidebar-nav .nav-item, .nav-brand');
    const pageViews = document.querySelectorAll('.page-view');
    const currentPageTitle = document.getElementById('current-page-title');
    const analysisNavHeader = document.getElementById('analysis-nav-header');
    const activeAnalysisItems = document.querySelectorAll('.active-analysis-item');
    const topDocBadge = document.getElementById('top-doc-badge');
    const topDocName = document.getElementById('top-doc-name');
    const toastContainer = document.getElementById('toast-container');

    // Progress Modal Elements
    const progressModal = document.getElementById('progress-modal');
    const pipelineProgressBar = document.getElementById('pipeline-progress-bar');
    const pipelineSteps = document.querySelectorAll('.pipeline-step');

    // Requirement Detail Modal
    const reqDetailModal = document.getElementById('requirement-detail-modal');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalFooterCloseBtn = document.getElementById('modal-footer-close-btn');

    // Workspace Input Elements
    const tabBtnUpload = document.getElementById('tab-btn-upload');
    const tabBtnText = document.getElementById('tab-btn-text');
    const uploadPanel = document.getElementById('upload-panel');
    const textPanel = document.getElementById('text-panel');
    const fileDropZone = document.getElementById('file-drop-zone');
    const realFileInput = document.getElementById('real-file-input');
    const browseFilesBtn = document.getElementById('browse-files-btn');
    const selectedFileBar = document.getElementById('selected-file-bar');
    const selectedFileName = document.getElementById('selected-file-name');
    const selectedFileSize = document.getElementById('selected-file-size');
    const clearSelectedFileBtn = document.getElementById('clear-selected-file');
    const srsTitleInput = document.getElementById('srs-title-input');
    const srsRawTextarea = document.getElementById('srs-raw-textarea');
    const editorLineCount = document.getElementById('editor-line-count');
    const editorWordCount = document.getElementById('editor-word-count');
    const editorCharCount = document.getElementById('editor-char-count');
    const editorLoadSampleBtn = document.getElementById('editor-load-sample-btn');
    const editorClearBtn = document.getElementById('editor-clear-btn');
    const startAnalysisBtn = document.getElementById('start-analysis-btn');

    // Top Action Buttons
    const topSampleBtn = document.getElementById('top-sample-btn');
    const topAnalyzeCta = document.getElementById('top-analyze-cta');
    const landingGetStartedBtn = document.getElementById('landing-get-started-btn');
    const landingLoadSampleBtn = document.getElementById('landing-load-sample-btn');
    const quickDemoBtn = document.getElementById('quick-demo-btn');

    // Table Filters
    const reqSearchInput = document.getElementById('req-search-input');
    const filterClassification = document.getElementById('filter-classification');
    const filterAmbiguity = document.getElementById('filter-ambiguity');
    const filterQuality = document.getElementById('filter-quality');
    const reqTableThSortable = document.querySelectorAll('#main-req-table th.sortable');
    const mainReqTbody = document.getElementById('main-req-tbody');
    const reqPaginationInfo = document.getElementById('req-pagination-info');
    const reqPrevPageBtn = document.getElementById('req-prev-page-btn');
    const reqNextPageBtn = document.getElementById('req-next-page-btn');
    const reqCurrentPage = document.getElementById('req-current-page');

    // Report Actions
    const reportDownloadMdBtn = document.getElementById('report-download-md-btn');
    const reportDownloadTxtBtn = document.getElementById('report-download-txt-btn');
    const reportPrintBtn = document.getElementById('report-print-btn');
    const reportToggleFormatted = document.getElementById('report-toggle-formatted');
    const reportToggleRaw = document.getElementById('report-toggle-raw');
    const reportFormattedContent = document.getElementById('report-formatted-content');
    const reportRawContent = document.getElementById('report-raw-content');

    // ==========================================
    // 3. VIEW ROUTER & NAVIGATION
    // ==========================================
    function switchView(viewName) {
        if (!viewName) return;

        // If target requires an active analysis and none exists, redirect to analyze
        const requiresAnalysis = ['results', 'requirements', 'ambiguity', 'duplicates', 'missing', 'complexity', 'quality', 'report'];
        if (requiresAnalysis.includes(viewName) && !state.activeAnalysis) {
            showToast("Please run or load an analysis first.", "info");
            switchView('analyze');
            return;
        }

        state.currentView = viewName;

        // Update nav items
        navItems.forEach(item => {
            if (item.dataset.nav === viewName) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Update view containers
        pageViews.forEach(view => {
            if (view.id === `view-${viewName}`) {
                view.classList.add('active');
            } else {
                view.classList.remove('active');
            }
        });

        // Update breadcrumb title
        const titles = {
            landing: 'Overview & Home',
            dashboard: 'Global Dashboard',
            analyze: 'Analyze SRS Workspace',
            results: 'Results Hub',
            requirements: 'Requirements Explorer',
            ambiguity: 'Ambiguity Inspector',
            duplicates: 'Duplicate Overlaps',
            missing: 'Missing Requirements',
            complexity: 'Complexity Analysis',
            quality: 'Quality Scoring',
            report: 'Report & Export',
            history: 'Analysis History'
        };
        currentPageTitle.textContent = titles[viewName] || 'Workspace';

        // Close mobile sidebar if open
        sidebar.classList.remove('open');
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Trigger view-specific renderers if needed
        if (viewName === 'dashboard') {
            loadGlobalDashboardData();
        } else if (viewName === 'history') {
            loadHistoryTable();
        } else if (viewName === 'requirements') {
            renderRequirementsTable();
        } else if (viewName === 'report' && state.activeAnalysis) {
            renderReportView();
        }
    }

    // Attach click listeners to all navigation triggers
    document.querySelectorAll('[data-nav]').forEach(el => {
        el.addEventListener('click', (e) => {
            e.preventDefault();
            const targetNav = el.getAttribute('data-nav');
            switchView(targetNav);
        });
    });

    // Mobile menu toggle
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', () => sidebar.classList.add('open'));
    }
    if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', () => sidebar.classList.remove('open'));
    }

    // ==========================================
    // 4. TOAST NOTIFICATIONS
    // ==========================================
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = 'ℹ️';
        if (type === 'success') icon = '✅';
        if (type === 'error') icon = '⚠️';

        toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(30px)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // ==========================================
    // 5. WORKSPACE INPUT & FILE UPLOAD
    // ==========================================
    // Switch between Upload and Text Editor tabs
    tabBtnUpload.addEventListener('click', () => {
        tabBtnUpload.classList.add('active');
        tabBtnText.classList.remove('active');
        uploadPanel.classList.add('active');
        textPanel.classList.remove('active');
    });

    tabBtnText.addEventListener('click', () => {
        tabBtnText.classList.add('active');
        tabBtnUpload.classList.remove('active');
        textPanel.classList.add('active');
        uploadPanel.classList.remove('active');
    });

    // File Drag & Drop Handlers
    ['dragenter', 'dragover'].forEach(name => {
        fileDropZone.addEventListener(name, (e) => {
            e.preventDefault();
            e.stopPropagation();
            fileDropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(name => {
        fileDropZone.addEventListener(name, (e) => {
            e.preventDefault();
            e.stopPropagation();
            fileDropZone.classList.remove('dragover');
        });
    });

    fileDropZone.addEventListener('drop', (e) => {
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleSelectedFile(e.dataTransfer.files[0]);
        }
    });

    browseFilesBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        realFileInput.click();
    });

    fileDropZone.addEventListener('click', () => realFileInput.click());

    realFileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleSelectedFile(e.target.files[0]);
        }
    });

    function handleSelectedFile(file) {
        const validExtensions = ['.txt', '.pdf', '.docx', '.csv', '.xlsx', '.xls', '.json', '.jsonl', '.md', '.markdown'];
        const name = file.name.toLowerCase();
        const isValid = validExtensions.some(ext => name.endsWith(ext));

        if (!isValid) {
            showToast("Invalid file format. Supported: .txt, .pdf, .docx, .csv, .xlsx, .json, .jsonl, .md", "error");
            return;
        }

        let icon = '📄';
        if (name.endsWith('.csv')) icon = '📊';
        else if (name.endsWith('.xlsx') || name.endsWith('.xls')) icon = '📗';
        else if (name.endsWith('.json') || name.endsWith('.jsonl')) icon = '📦';
        else if (name.endsWith('.pdf')) icon = '📕';
        else if (name.endsWith('.docx')) icon = '📘';

        const fileBadge = document.querySelector('.file-icon-badge');
        if (fileBadge) fileBadge.textContent = icon;

        state.selectedFile = file;
        selectedFileName.textContent = file.name;
        selectedFileSize.textContent = formatBytes(file.size);
        fileDropZone.classList.add('hidden');
        selectedFileBar.classList.remove('hidden');
        showToast(`Selected file: ${file.name}`, "info");
    }

    clearSelectedFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        state.selectedFile = null;
        realFileInput.value = '';
        selectedFileBar.classList.add('hidden');
        fileDropZone.classList.remove('hidden');
    });

    function formatBytes(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / 1048576).toFixed(1) + ' MB';
    }

    // Text Editor Live Counter
    srsRawTextarea.addEventListener('input', updateTextareaCounters);
    function updateTextareaCounters() {
        const text = srsRawTextarea.value;
        const lines = text ? text.split('\n').filter(l => l.trim().length > 0).length : 0;
        const words = text ? text.trim().split(/\s+/).filter(w => w.length > 0).length : 0;
        const chars = text.length;

        editorLineCount.textContent = `${lines} lines`;
        editorWordCount.textContent = `${words} words`;
        editorCharCount.textContent = `${chars} characters`;
    }

    editorClearBtn.addEventListener('click', () => {
        srsRawTextarea.value = '';
        updateTextareaCounters();
    });

    // ==========================================
    // 6. SAMPLE SRS LOADER
    // ==========================================
    async function loadSampleSRS(autoAnalyze = false) {
        try {
            const res = await fetch(`${API_BASE}/api/sample`);
            const result = await res.json();

            if (res.ok && result.content) {
                srsRawTextarea.value = result.content;
                srsTitleInput.value = result.title || "Hospital Management System (Sample SRS)";
                updateTextareaCounters();

                // Switch to text editor tab
                tabBtnText.click();
                showToast("Sample SRS loaded successfully.", "success");

                if (autoAnalyze) {
                    runAnalysis();
                }
            } else {
                showToast("Could not load sample SRS.", "error");
            }
        } catch (err) {
            showToast(`Server connection error: ${err.message}. Please ensure the backend is running at ${API_BASE || 'http://127.0.0.1:8000'}.`, "error");
        }
    }

    if (editorLoadSampleBtn) editorLoadSampleBtn.addEventListener('click', () => loadSampleSRS(false));
    if (topSampleBtn) topSampleBtn.addEventListener('click', () => { switchView('analyze'); loadSampleSRS(false); });
    if (landingLoadSampleBtn) landingLoadSampleBtn.addEventListener('click', () => { switchView('analyze'); loadSampleSRS(true); });
    if (quickDemoBtn) quickDemoBtn.addEventListener('click', () => loadSampleSRS(true));
    if (landingGetStartedBtn) landingGetStartedBtn.addEventListener('click', () => switchView('analyze'));
    if (topAnalyzeCta) topAnalyzeCta.addEventListener('click', () => switchView('analyze'));

    // ==========================================
    // 7. MULTI-STAGE ANALYSIS PIPELINE
    // ==========================================
    startAnalysisBtn.addEventListener('click', runAnalysis);

    async function runAnalysis() {
        const isUploadTab = uploadPanel.classList.contains('active');

        // Validation
        if (isUploadTab && !state.selectedFile) {
            showToast("Please drag & drop or select an SRS file first.", "error");
            return;
        }
        if (!isUploadTab && (!srsRawTextarea.value || srsRawTextarea.value.trim().length < 20)) {
            showToast("Please paste at least one requirement statement.", "error");
            return;
        }

        // Show Progress Modal & Start Animation
        progressModal.classList.remove('hidden');
        startProgressAnimation();

        try {
            let response, jsonResult;

            if (isUploadTab && state.selectedFile) {
                const formData = new FormData();
                formData.append('file', state.selectedFile);

                response = await fetch(`${API_BASE}/api/analyze`, {
                    method: 'POST',
                    body: formData
                });
            } else {
                const payload = {
                    text: srsRawTextarea.value.trim(),
                    title: srsTitleInput.value.trim() || "Custom Software Specification"
                };

                response = await fetch(`${API_BASE}/api/analyze/text`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            }

            jsonResult = await response.json();

            if (!response.ok) {
                throw new Error(jsonResult.detail || "Analysis request failed.");
            }

            // Complete progress bar
            completeProgressAnimation();

            setTimeout(() => {
                progressModal.classList.add('hidden');
                onAnalysisComplete(jsonResult.data);
            }, 600);

        } catch (error) {
            progressModal.classList.add('hidden');
            showToast(`Analysis Error: ${error.message}`, "error");
        }
    }

    let progressInterval = null;
    function startProgressAnimation() {
        pipelineProgressBar.style.width = '10%';
        pipelineSteps.forEach((step, index) => {
            step.className = 'pipeline-step';
            step.querySelector('.step-status').textContent = 'Waiting...';
        });

        let currentStep = 0;
        const totalSteps = pipelineSteps.length;

        if (progressInterval) clearInterval(progressInterval);

        progressInterval = setInterval(() => {
            if (currentStep < totalSteps - 1) {
                const prev = pipelineSteps[currentStep];
                if (prev) {
                    prev.className = 'pipeline-step done';
                    prev.querySelector('.step-status').textContent = 'Completed ✓';
                }

                currentStep++;
                const curr = pipelineSteps[currentStep];
                if (curr) {
                    curr.className = 'pipeline-step active';
                    curr.querySelector('.step-status').textContent = 'Processing...';
                }

                const pct = Math.min(90, Math.round(((currentStep + 1) / totalSteps) * 100));
                pipelineProgressBar.style.width = `${pct}%`;
            }
        }, 400);
    }

    function completeProgressAnimation() {
        if (progressInterval) clearInterval(progressInterval);
        pipelineProgressBar.style.width = '100%';
        pipelineSteps.forEach(step => {
            step.className = 'pipeline-step done';
            step.querySelector('.step-status').textContent = 'Completed ✓';
        });
    }

    // ==========================================
    // 8. POPULATE ANALYSIS RESULTS & VIEWS
    // ==========================================
    function onAnalysisComplete(data) {
        state.activeAnalysis = data;

        // Reveal Active Analysis Nav Items
        if (analysisNavHeader) analysisNavHeader.classList.remove('hidden');
        activeAnalysisItems.forEach(item => item.classList.remove('hidden'));

        // Update Top Navbar Badge
        topDocBadge.classList.remove('hidden');
        topDocName.textContent = data.title || data.filename || "Active SRS";

        // Sidebar Badges
        const sidebarAmb = document.getElementById('sidebar-ambiguity-count');
        const sidebarDup = document.getElementById('sidebar-duplicate-count');
        if (sidebarAmb) sidebarAmb.textContent = data.ambiguity.ambiguous_count;
        if (sidebarDup) sidebarDup.textContent = data.duplicates.pairs_count || data.duplicates.pairs.length;

        // Render all data views
        renderResultsHub(data);
        renderAmbiguityPage(data);
        renderDuplicatesPage(data);
        renderMissingPage(data);
        renderComplexityPage(data);
        renderQualityPage(data);
        renderRequirementsTable();
        renderReportView();

        showToast("AI Requirement Analysis completed successfully!", "success");
        switchView('results');
    }

    // Render 4. Results Hub
    function renderResultsHub(data) {
        const { summary, complexity, quality, ambiguity, duplicates, missing_categories } = data;

        document.getElementById('results-doc-title').textContent = data.title || "SRS Analysis Results";
        document.getElementById('results-doc-subtitle').textContent = `Source: ${data.filename} • Extracted on ${new Date().toLocaleTimeString()}`;

        // Top Badges
        const compBadge = document.getElementById('results-complexity-badge');
        compBadge.textContent = `Complexity: ${complexity.complexity_level}`;
        compBadge.className = `badge ${complexity.complexity_level === 'Low' ? 'success-badge' : (complexity.complexity_level === 'High' ? 'danger-badge' : 'warning-badge')}`;

        const qualBadge = document.getElementById('results-quality-badge');
        qualBadge.textContent = `Quality: ${quality.quality_tier}`;
        qualBadge.className = `badge ${quality.overall_score >= 80 ? 'success-badge' : 'warning-badge'}`;

        // KPI Numbers
        document.getElementById('res-total-reqs').textContent = summary.total_requirements;
        document.getElementById('res-func-reqs').textContent = summary.functional_count;
        document.getElementById('res-nfr-reqs').textContent = summary.non_functional_count;

        const total = summary.total_requirements || 1;
        document.getElementById('res-func-pct').textContent = `${Math.round((summary.functional_count / total) * 100)}% of total`;
        document.getElementById('res-nfr-pct').textContent = `${Math.round((summary.non_functional_count / total) * 100)}% of total`;

        document.getElementById('res-amb-reqs').textContent = ambiguity.ambiguous_count;
        document.getElementById('res-amb-pct').textContent = `${ambiguity.ambiguity_percentage}% flagged`;

        const dupCount = duplicates.pairs_count !== undefined ? duplicates.pairs_count : duplicates.pairs.length;
        document.getElementById('res-dup-pairs').textContent = dupCount;
        document.getElementById('res-dup-pct').textContent = `${Math.round((duplicates.ratio || 0) * 100)}% overlap`;

        document.getElementById('res-missing-count').textContent = missing_categories.length;
        document.getElementById('res-quality-score').textContent = quality.overall_score;
        document.getElementById('res-quality-tier').textContent = quality.quality_tier;
        document.getElementById('res-completeness-score').textContent = `${summary.completeness_score}%`;
        document.getElementById('res-complexity-level').textContent = complexity.complexity_level;
        document.getElementById('res-complexity-score').textContent = `Score: ${complexity.complexity_score}/100`;
        document.getElementById('res-avg-confidence').textContent = `${summary.overall_confidence}%`;

        // Render Results Charts
        renderResultsCharts(data);
    }

    function renderResultsCharts(data) {
        const { summary, ambiguity, quality } = data;

        // Chart 1: Distribution Doughnut
        const ctxDist = document.getElementById('results-dist-chart');
        if (ctxDist) {
            if (state.charts.resultsDist) state.charts.resultsDist.destroy();
            state.charts.resultsDist = new Chart(ctxDist, {
                type: 'doughnut',
                data: {
                    labels: ['Functional (FR)', 'Non-Functional (NFR)', 'Ambiguous Terms'],
                    datasets: [{
                        data: [summary.functional_count, summary.non_functional_count, ambiguity.ambiguous_count],
                        backgroundColor: ['#10b981', '#f59e0b', '#f43f5e'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } } }
                    }
                }
            });
        }

        // Chart 2: Quality Radar
        const ctxRadar = document.getElementById('results-quality-radar');
        if (ctxRadar) {
            if (state.charts.resultsRadar) state.charts.resultsRadar.destroy();
            state.charts.resultsRadar = new Chart(ctxRadar, {
                type: 'radar',
                data: {
                    labels: ['Clarity', 'Completeness', 'Consistency', 'Specificity', 'Testability'],
                    datasets: [{
                        label: 'Quality Score',
                        data: [quality.clarity, quality.completeness, quality.consistency, quality.specificity, quality.testability],
                        backgroundColor: 'rgba(99, 102, 241, 0.25)',
                        borderColor: '#6366f1',
                        pointBackgroundColor: '#8b5cf6',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            min: 0,
                            max: 100,
                            ticks: { display: false },
                            grid: { color: 'rgba(255, 255, 255, 0.08)' },
                            angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
                            pointLabels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
    }

    // ==========================================
    // 9. REQUIREMENTS EXPLORER TABLE & MODAL
    // ==========================================
    function renderRequirementsTable() {
        if (!state.activeAnalysis) return;

        const allReqs = state.activeAnalysis.classifications;
        const query = state.reqSearchQuery.toLowerCase();

        // 1. Filter
        let filtered = allReqs.filter(item => {
            const matchesQuery = item.id.toLowerCase().includes(query) || item.requirement.toLowerCase().includes(query);
            const matchesClass = state.reqFilterClass === 'ALL' || item.label === state.reqFilterClass;
            const matchesAmb = state.reqFilterAmbiguity === 'ALL' ||
                (state.reqFilterAmbiguity === 'AMBIGUOUS' && item.ambiguity.is_ambiguous) ||
                (state.reqFilterAmbiguity === 'CLEAR' && !item.ambiguity.is_ambiguous);
            const matchesQuality = state.reqFilterQuality === 'ALL' ||
                (item.quality && item.quality.status === state.reqFilterQuality);

            return matchesQuery && matchesClass && matchesAmb && matchesQuality;
        });

        // 2. Sort
        filtered.sort((a, b) => {
            let valA, valB;
            if (state.reqSortColumn === 'id') {
                valA = a.index; valB = b.index;
            } else if (state.reqSortColumn === 'label') {
                valA = a.label; valB = b.label;
            } else if (state.reqSortColumn === 'confidence') {
                valA = a.confidence; valB = b.confidence;
            } else if (state.reqSortColumn === 'ambiguity') {
                valA = a.ambiguity.ambiguity_score; valB = b.ambiguity.ambiguity_score;
            } else if (state.reqSortColumn === 'quality') {
                valA = a.quality ? a.quality.overall_score : 0;
                valB = b.quality ? b.quality.overall_score : 0;
            } else {
                valA = a.index; valB = b.index;
            }

            if (valA < valB) return state.reqSortOrder === 'asc' ? -1 : 1;
            if (valA > valB) return state.reqSortOrder === 'asc' ? 1 : -1;
            return 0;
        });

        // 3. Pagination
        const totalItems = filtered.length;
        const totalPages = Math.max(1, Math.ceil(totalItems / state.reqPageSize));
        state.reqCurrentPage = Math.min(state.reqCurrentPage, totalPages);

        const startIndex = (state.reqCurrentPage - 1) * state.reqPageSize;
        const pageItems = filtered.slice(startIndex, startIndex + state.reqPageSize);

        // Update pagination UI
        reqPaginationInfo.textContent = `Showing ${Math.min(startIndex + 1, totalItems)} to ${Math.min(startIndex + state.reqPageSize, totalItems)} of ${totalItems} requirements`;
        reqCurrentPage.textContent = state.reqCurrentPage;
        reqPrevPageBtn.disabled = state.reqCurrentPage <= 1;
        reqNextPageBtn.disabled = state.reqCurrentPage >= totalPages;

        // Render Rows
        mainReqTbody.innerHTML = '';
        if (pageItems.length === 0) {
            mainReqTbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted" style="padding:2rem;">No requirements match your current filter settings.</td></tr>`;
            return;
        }

        pageItems.forEach(item => {
            const tr = document.createElement('tr');
            
            const isFR = item.label === 'Functional';
            const classBadge = isFR ? `<span class="badge functional-badge">Functional</span>` : `<span class="badge nfr-badge">Non-Functional</span>`;
            
            const isAmb = item.ambiguity && item.ambiguity.is_ambiguous;
            const ambBadge = isAmb ? `<span class="badge danger-badge">⚠️ Ambiguous</span>` : `<span class="badge success-badge">✅ Clear</span>`;
            
            const qScore = item.quality ? item.quality.overall_score : '-';
            const qClass = qScore >= 80 ? 'text-emerald' : (qScore >= 60 ? 'text-amber' : 'text-rose');

            tr.innerHTML = `
                <td><strong class="font-mono text-indigo">${item.id}</strong></td>
                <td><span style="font-size:0.92rem;">${escapeHtml(item.requirement)}</span></td>
                <td>${classBadge}</td>
                <td><strong>${item.confidence_percentage}%</strong></td>
                <td>${ambBadge}</td>
                <td><strong class="${qClass}">${qScore}</strong></td>
                <td class="text-center">
                    <button class="btn btn-secondary btn-xs btn-inspect-req" data-req-index="${item.index}">Inspect</button>
                </td>
            `;
            mainReqTbody.appendChild(tr);
        });

        // Attach Inspect Click Listeners
        document.querySelectorAll('.btn-inspect-req').forEach(btn => {
            btn.addEventListener('click', () => {
                const idx = parseInt(btn.getAttribute('data-req-index'), 10);
                openRequirementInspector(idx);
            });
        });
    }

    // Filter Listeners
    reqSearchInput.addEventListener('input', (e) => {
        state.reqSearchQuery = e.target.value;
        state.reqCurrentPage = 1;
        renderRequirementsTable();
    });

    filterClassification.addEventListener('change', (e) => {
        state.reqFilterClass = e.target.value;
        state.reqCurrentPage = 1;
        renderRequirementsTable();
    });

    filterAmbiguity.addEventListener('change', (e) => {
        state.reqFilterAmbiguity = e.target.value;
        state.reqCurrentPage = 1;
        renderRequirementsTable();
    });

    filterQuality.addEventListener('change', (e) => {
        state.reqFilterQuality = e.target.value;
        state.reqCurrentPage = 1;
        renderRequirementsTable();
    });

    reqPrevPageBtn.addEventListener('click', () => {
        if (state.reqCurrentPage > 1) {
            state.reqCurrentPage--;
            renderRequirementsTable();
        }
    });

    reqNextPageBtn.addEventListener('click', () => {
        state.reqCurrentPage++;
        renderRequirementsTable();
    });

    // Sort Click Listeners
    reqTableThSortable.forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-sort');
            if (state.reqSortColumn === col) {
                state.reqSortOrder = state.reqSortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                state.reqSortColumn = col;
                state.reqSortOrder = 'asc';
            }
            renderRequirementsTable();
        });
    });

    // Requirement Inspector Modal
    function openRequirementInspector(index) {
        if (!state.activeAnalysis) return;
        const item = state.activeAnalysis.classifications[index];
        if (!item) return;

        document.getElementById('modal-req-id').textContent = item.id;
        
        const typeBadge = document.getElementById('modal-req-type');
        typeBadge.textContent = item.label;
        typeBadge.className = `badge ${item.label === 'Functional' ? 'functional-badge' : 'nfr-badge'}`;

        document.getElementById('modal-req-conf').textContent = `Confidence: ${item.confidence_percentage}%`;
        document.getElementById('modal-req-text').textContent = item.requirement;

        // Cleaned Tokens
        const tokensWrap = document.getElementById('modal-req-tokens');
        tokensWrap.innerHTML = '';
        const tokens = (item.cleaned_text || '').split(' ').filter(t => t.length > 0);
        if (tokens.length === 0) {
            tokensWrap.innerHTML = `<span class="text-muted text-xs">No tokens</span>`;
        } else {
            tokens.forEach(tok => {
                const chip = document.createElement('span');
                chip.className = 'token-chip';
                chip.textContent = tok;
                tokensWrap.appendChild(chip);
            });
        }

        // Ambiguity Details
        const amb = item.ambiguity;
        const ambBadge = document.getElementById('modal-amb-badge');
        const ambScore = document.getElementById('modal-amb-score');
        const ambExplanation = document.getElementById('modal-amb-explanation');
        const ambRewriteWrap = document.getElementById('modal-amb-rewrite-wrap');
        const ambRewrite = document.getElementById('modal-amb-rewrite');

        if (amb && amb.is_ambiguous) {
            ambBadge.textContent = `Ambiguous (${amb.severity} Severity)`;
            ambBadge.className = 'badge danger-badge';
            ambScore.textContent = `Score: ${amb.ambiguity_score} / 1.0`;
            ambExplanation.textContent = amb.explanation;
            ambRewrite.textContent = amb.suggested_rewrite;
            ambRewriteWrap.classList.remove('hidden');
        } else {
            ambBadge.textContent = 'Clear Statement';
            ambBadge.className = 'badge success-badge';
            ambScore.textContent = 'Score: 0.0';
            ambExplanation.textContent = 'Meets precision criteria with no ambiguous qualitative modifiers.';
            ambRewriteWrap.classList.add('hidden');
        }

        // Quality Mini Meters
        const qMeters = document.getElementById('modal-quality-meters');
        qMeters.innerHTML = '';
        if (item.quality) {
            const q = item.quality;
            const metrics = [
                { name: 'Clarity', val: q.clarity_score },
                { name: 'Completeness', val: q.completeness_score },
                { name: 'Consistency', val: q.consistency_score },
                { name: 'Specificity', val: q.specificity_score },
                { name: 'Testability', val: q.testability_score }
            ];

            metrics.forEach(m => {
                const row = document.createElement('div');
                row.className = 'q-meter-item';
                row.innerHTML = `
                    <span>${m.name}</span>
                    <strong class="${m.val >= 75 ? 'text-emerald' : 'text-amber'}">${m.val}/100</strong>
                `;
                qMeters.appendChild(row);
            });
        }

        // Duplicate Links
        const dupSection = document.getElementById('modal-dup-section');
        const dupLinks = document.getElementById('modal-dup-links');
        dupLinks.innerHTML = '';
        const matchingPairs = (state.activeAnalysis.duplicates.pairs || []).filter(p => p.index_a === index || p.index_b === index);

        if (matchingPairs.length > 0) {
            dupSection.classList.remove('hidden');
            matchingPairs.forEach(pair => {
                const otherId = pair.index_a === index ? pair.req_id_b : pair.req_id_a;
                const otherText = pair.index_a === index ? pair.requirement_b : pair.requirement_a;
                const sim = pair.similarity_percentage || Math.round(pair.similarity_score * 100);

                const card = document.createElement('div');
                card.className = 'amb-rewrite-box mb-2';
                card.innerHTML = `<strong>${sim}% Semantic Overlap with ${otherId}:</strong> "${escapeHtml(otherText)}"`;
                dupLinks.appendChild(card);
            });
        } else {
            dupSection.classList.add('hidden');
        }

        reqDetailModal.classList.remove('hidden');
    }

    modalCloseBtn.addEventListener('click', () => reqDetailModal.classList.add('hidden'));
    modalFooterCloseBtn.addEventListener('click', () => reqDetailModal.classList.add('hidden'));

    // ==========================================
    // 10. AMBIGUITY PAGE RENDERER
    // ==========================================
    function renderAmbiguityPage(data) {
        const { ambiguity, classifications } = data;

        document.getElementById('amb-total-count').textContent = ambiguity.ambiguous_count;
        document.getElementById('amb-percentage-badge').textContent = `${ambiguity.ambiguity_percentage}% of document`;
        document.getElementById('amb-high-severity').textContent = ambiguity.high_severity_count || 0;
        document.getElementById('amb-med-severity').textContent = ambiguity.medium_severity_count || 0;
        document.getElementById('amb-clear-count').textContent = ambiguity.clear_count || 0;

        // Frequent Terms Chips
        const chipsContainer = document.getElementById('amb-term-chips');
        chipsContainer.innerHTML = '';
        const freq = ambiguity.frequent_ambiguous_terms || {};
        const entries = Object.entries(freq).sort((a, b) => b[1] - a[1]);

        if (entries.length === 0) {
            chipsContainer.innerHTML = `<span class="text-emerald text-sm">✓ No frequent ambiguous terms detected.</span>`;
        } else {
            entries.forEach(([term, count]) => {
                const chip = document.createElement('span');
                chip.className = 'term-chip';
                chip.innerHTML = `"${escapeHtml(term)}" <span class="badge info-badge">${count}</span>`;
                chipsContainer.appendChild(chip);
            });
        }

        // Ambiguity Cards List
        const cardsContainer = document.getElementById('ambiguity-cards-container');
        cardsContainer.innerHTML = '';
        const ambiguousItems = classifications.filter(c => c.ambiguity && c.ambiguity.is_ambiguous);

        if (ambiguousItems.length === 0) {
            cardsContainer.innerHTML = `
                <div class="text-center text-muted" style="padding: 2.5rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">✅</div>
                    <h4>Zero Ambiguity Detected</h4>
                    <p>All extracted requirement statements adhere to objective, measurable criteria.</p>
                </div>
            `;
            return;
        }

        ambiguousItems.forEach(item => {
            const amb = item.ambiguity;
            const card = document.createElement('div');
            card.className = `amb-item-card ${amb.severity === 'High' ? 'high-severity' : ''}`;

            const flaggedList = (amb.ambiguous_terms || []).map(t => `<span class="term-chip">"${escapeHtml(t)}"</span>`).join(' ');

            card.innerHTML = `
                <div class="amb-item-header">
                    <div>
                        <strong class="font-mono text-indigo">${item.id}</strong>
                        <span class="badge ${amb.severity === 'High' ? 'danger-badge' : 'warning-badge'} ml-2">${amb.severity} Severity</span>
                    </div>
                    <div>${flaggedList}</div>
                </div>
                <div class="amb-original-text">"${escapeHtml(item.requirement)}"</div>
                <p class="amb-explanation-p"><strong>Problem:</strong> ${escapeHtml(amb.explanation)}</p>
                <div class="amb-rewrite-box">
                    <strong>AI Suggested Rewrite:</strong> "${escapeHtml(amb.suggested_rewrite)}"
                </div>
            `;
            cardsContainer.appendChild(card);
        });
    }

    // ==========================================
    // 11. DUPLICATE DETECTOR PAGE RENDERER
    // ==========================================
    function renderDuplicatesPage(data) {
        const { duplicates } = data;
        const pairs = duplicates.pairs || [];

        document.getElementById('dup-pairs-count').textContent = pairs.length;
        document.getElementById('dup-ratio-val').textContent = `${Math.round((duplicates.ratio || 0) * 100)}%`;

        const container = document.getElementById('duplicate-pairs-container');
        container.innerHTML = '';

        if (pairs.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted" style="padding: 2.5rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">✅</div>
                    <h4>No Duplicate Statements Detected</h4>
                    <p>All extracted requirements satisfy the semantic uniqueness threshold.</p>
                </div>
            `;
            return;
        }

        pairs.forEach(pair => {
            const card = document.createElement('div');
            card.className = 'dup-pair-card';

            const sim = pair.similarity_percentage || Math.round(pair.similarity_score * 100);
            const statusClass = sim >= 90 ? 'danger-badge' : 'warning-badge';

            card.innerHTML = `
                <div class="dup-pair-header">
                    <div>
                        <span class="badge info-badge">${pair.req_id_a}</span>
                        <span class="text-dim">vs</span>
                        <span class="badge info-badge">${pair.req_id_b}</span>
                    </div>
                    <span class="badge ${statusClass}">${sim}% Semantic Overlap (${pair.status || 'Duplicate'})</span>
                </div>
                <div class="dup-comparison-grid">
                    <div class="dup-req-col">
                        <div class="dup-req-title">${pair.req_id_a} Original Statement:</div>
                        <div class="dup-req-text">"${escapeHtml(pair.requirement_a)}"</div>
                    </div>
                    <div class="dup-req-col">
                        <div class="dup-req-title">${pair.req_id_b} Original Statement:</div>
                        <div class="dup-req-text">"${escapeHtml(pair.requirement_b)}"</div>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
    }

    // ==========================================
    // 12. MISSING DOMAIN CATEGORIES RENDERER
    // ==========================================
    function renderMissingPage(data) {
        const { domain_coverage, missing_categories } = data;
        const coverage = domain_coverage || {};

        document.getElementById('missing-coverage-pct').textContent = `${coverage.coverage_percentage || 0}%`;
        document.getElementById('missing-coverage-sub').textContent = `${coverage.covered_count || 0} of ${coverage.total_categories || 22} domain categories covered`;
        document.getElementById('missing-recommendations-count').textContent = missing_categories.length;

        const highPrioCount = missing_categories.filter(m => m.priority === 'High').length;
        document.getElementById('missing-high-prio-count').textContent = highPrioCount;

        const container = document.getElementById('missing-categories-container');
        container.innerHTML = '';

        if (missing_categories.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted" style="padding: 2.5rem; grid-column: 1 / -1;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎉</div>
                    <h4>100% Comprehensive Domain Coverage</h4>
                    <p>Your specification includes requirements across all 22 standard software engineering categories.</p>
                </div>
            `;
            return;
        }

        missing_categories.forEach(item => {
            const card = document.createElement('div');
            card.className = 'category-card';

            const prioClass = item.priority === 'High' ? 'danger-badge' : (item.priority === 'Medium' ? 'warning-badge' : 'info-badge');
            const supportingHtml = (item.supporting_items || []).map(s => `<span class="support-tag">${escapeHtml(s)}</span>`).join('');

            card.innerHTML = `
                <div class="category-card-header">
                    <h4>${escapeHtml(item.category)}</h4>
                    <span class="badge ${prioClass}">Priority: ${item.priority}</span>
                </div>
                <p class="category-reason">${escapeHtml(item.reason)}</p>
                <div class="category-suggestion-box">
                    <strong class="text-cyan">AI Recommended Statement:</strong>
                    <p class="mt-1" style="font-style: italic;">"${escapeHtml(item.suggested_requirement)}"</p>
                    <div class="supporting-tags">${supportingHtml}</div>
                </div>
            `;
            container.appendChild(card);
        });
    }

    // ==========================================
    // 13. COMPLEXITY & QUALITY PAGES RENDERER
    // ==========================================
    function renderComplexityPage(data) {
        const { complexity } = data;

        const tierBadge = document.getElementById('comp-tier-badge');
        tierBadge.textContent = `${complexity.complexity_level} Complexity`;
        tierBadge.className = `complexity-tier-badge ${complexity.complexity_level === 'Low' ? 'text-emerald' : (complexity.complexity_level === 'High' ? 'text-rose' : 'text-amber')}`;

        document.getElementById('comp-score-number').textContent = complexity.complexity_score;
        document.getElementById('comp-explanation-text').textContent = complexity.explanation;

        const container = document.getElementById('complexity-factors-container');
        container.innerHTML = '';

        const breakdown = complexity.factor_breakdown || {};
        Object.entries(breakdown).forEach(([name, info]) => {
            const item = document.createElement('div');
            item.className = 'factor-item';

            item.innerHTML = `
                <div class="factor-meta">
                    <span>${escapeHtml(name)} <span class="text-dim text-xs">(${escapeHtml(info.description)})</span></span>
                    <span>${info.score} / 100</span>
                </div>
                <div class="factor-bar-bg">
                    <div class="factor-bar-fill" style="width: ${info.score}%;"></div>
                </div>
            `;
            container.appendChild(item);
        });
    }

    function renderQualityPage(data) {
        const { quality } = data;

        document.getElementById('quality-main-score').textContent = quality.overall_score;
        document.getElementById('quality-main-tier').textContent = quality.quality_tier;
        document.getElementById('quality-exec-summary').textContent = quality.executive_summary;

        // Circle stroke offset animation (Circumference: 314 for radius 50)
        const circleFg = document.getElementById('quality-circle-fg');
        const offset = 314 - (314 * quality.overall_score) / 100;
        circleFg.style.strokeDashoffset = offset;
        circleFg.style.stroke = quality.overall_score >= 80 ? '#10b981' : (quality.overall_score >= 60 ? '#f59e0b' : '#f43f5e');

        // Dimensions Bars
        const dimContainer = document.getElementById('quality-dimensions-container');
        dimContainer.innerHTML = '';

        const dims = [
            { name: 'Clarity (Readability & Precision)', val: quality.clarity },
            { name: 'Completeness (Domain Coverage & Modals)', val: quality.completeness },
            { name: 'Consistency (Lack of Redundancies)', val: quality.consistency },
            { name: 'Specificity (Metrics & Boundaries)', val: quality.specificity },
            { name: 'Testability (Verifiability Criteria)', val: quality.testability }
        ];

        dims.forEach(d => {
            const row = document.createElement('div');
            row.className = 'factor-item';
            row.innerHTML = `
                <div class="factor-meta">
                    <span>${d.name}</span>
                    <strong class="${d.val >= 75 ? 'text-emerald' : 'text-amber'}">${d.val} / 100</strong>
                </div>
                <div class="factor-bar-bg">
                    <div class="factor-bar-fill" style="width: ${d.val}%;"></div>
                </div>
            `;
            dimContainer.appendChild(row);
        });

        // Strengths & Recommendations Lists
        const strengthsList = document.getElementById('quality-strengths-list');
        strengthsList.innerHTML = '';
        (quality.key_strengths || []).forEach(s => {
            const li = document.createElement('li');
            li.textContent = s;
            strengthsList.appendChild(li);
        });

        const recsList = document.getElementById('quality-recommendations-list');
        recsList.innerHTML = '';
        (quality.improvement_recommendations || []).forEach(r => {
            const li = document.createElement('li');
            li.textContent = r;
            recsList.appendChild(li);
        });
    }

    // ==========================================
    // 14. REPORT PREVIEW & EXPORTS
    // ==========================================
    async function renderReportView() {
        if (!state.activeAnalysis) return;

        const id = state.activeAnalysis.id || state.activeAnalysis.history_id;
        document.getElementById('report-doc-title').textContent = `${state.activeAnalysis.title || 'SRS'} — Analysis Report`;

        try {
            const res = await fetch(`${API_BASE}/api/report/${id}?format=markdown`);
            const mdText = await res.text();

            reportRawContent.textContent = mdText;
            reportFormattedContent.innerHTML = renderMarkdownSimple(mdText);
        } catch (err) {
            showToast(`Failed to load report preview: ${err.message}`, "error");
        }
    }

    reportToggleFormatted.addEventListener('click', () => {
        reportToggleFormatted.classList.add('active');
        reportToggleRaw.classList.remove('active');
        reportFormattedContent.classList.remove('hidden');
        reportRawContent.classList.add('hidden');
    });

    reportToggleRaw.addEventListener('click', () => {
        reportToggleRaw.classList.add('active');
        reportToggleFormatted.classList.remove('active');
        reportRawContent.classList.remove('hidden');
        reportFormattedContent.classList.add('hidden');
    });

    reportDownloadMdBtn.addEventListener('click', () => {
        if (!state.activeAnalysis) return;
        const id = state.activeAnalysis.id || state.activeAnalysis.history_id;
        window.location.href = `${API_BASE}/api/report/${id}?format=markdown`;
    });

    reportDownloadTxtBtn.addEventListener('click', () => {
        if (!state.activeAnalysis) return;
        const id = state.activeAnalysis.id || state.activeAnalysis.history_id;
        window.location.href = `${API_BASE}/api/report/${id}?format=txt`;
    });

    reportPrintBtn.addEventListener('click', () => {
        window.print();
    });

    function renderMarkdownSimple(md) {
        if (!md) return '';
        let html = escapeHtml(md);

        // Convert markdown headers, bold, tables, lists
        html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
        html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
        html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
        html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');
        html = html.replace(/`([^`]+)`/gim, '<code class="token-chip">$1</code>');
        html = html.replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>');
        html = html.replace(/^- (.*$)/gim, '<li>$1</li>');
        html = html.replace(/\n\n/gim, '<br><br>');

        return html;
    }

    // ==========================================
    // 15. GLOBAL DASHBOARD & HISTORY MANAGEMENT
    // ==========================================
    async function loadGlobalDashboardData() {
        try {
            const res = await fetch(`${API_BASE}/api/analyses`);
            const result = await res.json();

            if (res.ok && result.data) {
                const { stats, history } = result.data;
                state.historicalAnalyses = history || [];
                state.historyStats = stats;

                document.getElementById('dash-total-docs').textContent = stats.total_analyses || 0;
                document.getElementById('dash-total-reqs').textContent = stats.total_requirements || 0;
                document.getElementById('dash-func-reqs').textContent = stats.functional_count || 0;
                document.getElementById('dash-nfr-reqs').textContent = stats.non_functional_count || 0;
                document.getElementById('dash-avg-quality').textContent = stats.avg_quality_score || '0.0';
                document.getElementById('dash-avg-conf').textContent = `${stats.avg_confidence || 0}%`;

                // Render Chart
                const ctx = document.getElementById('global-dist-chart');
                if (ctx) {
                    if (state.charts.globalDist) state.charts.globalDist.destroy();
                    state.charts.globalDist = new Chart(ctx, {
                        type: 'pie',
                        data: {
                            labels: ['Functional Requirements', 'Non-Functional Requirements', 'Ambiguous Flagged'],
                            datasets: [{
                                data: [stats.functional_count || 1, stats.non_functional_count || 1, stats.ambiguous_count || 0],
                                backgroundColor: ['#10b981', '#f59e0b', '#f43f5e'],
                                borderWidth: 0
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } } }
                            }
                        }
                    });
                }

                // Render Recent Table
                const tbody = document.getElementById('dashboard-recent-tbody');
                tbody.innerHTML = '';
                const recent = (history || []).slice(0, 5);

                if (recent.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted" style="padding:1.5rem;">No historical analyses found.</td></tr>`;
                } else {
                    recent.forEach(item => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td><strong>${escapeHtml(item.title)}</strong></td>
                            <td><span class="text-dim text-xs">${item.created_at}</span></td>
                            <td>${item.total_requirements}</td>
                            <td><strong class="text-emerald">${item.quality_score}</strong></td>
                            <td><span class="badge ${item.complexity_level === 'Low' ? 'success-badge' : 'warning-badge'}">${item.complexity_level}</span></td>
                            <td>
                                <button class="btn btn-ghost btn-xs btn-load-history" data-history-id="${item.id}">Open →</button>
                            </td>
                        `;
                        tbody.appendChild(tr);
                    });

                    attachHistoryOpenListeners();
                }
            }
        } catch (err) {
            console.warn("Dashboard initial fetch (server may be starting):", err.message);
        }
    }

    async function loadHistoryTable() {
        try {
            const res = await fetch(`${API_BASE}/api/analyses`);
            const result = await res.json();

            if (res.ok && result.data) {
                const history = result.data.history || [];
                const tbody = document.getElementById('history-full-tbody');
                tbody.innerHTML = '';

                if (history.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted" style="padding:2.5rem;">No saved analyses in SQLite database yet.</td></tr>`;
                    return;
                }

                history.forEach(item => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong class="font-mono text-indigo">#${item.id}</strong></td>
                        <td><strong>${escapeHtml(item.title)}</strong><br><span class="text-dim text-xs">${escapeHtml(item.filename)}</span></td>
                        <td><span class="text-dim text-xs">${item.created_at}</span></td>
                        <td><strong>${item.total_requirements}</strong></td>
                        <td><span class="text-emerald">${item.functional_count}</span> / <span class="text-amber">${item.non_functional_count}</span></td>
                        <td><strong class="text-emerald">${item.quality_score}</strong></td>
                        <td><strong>${item.completeness_score}%</strong></td>
                        <td><span class="badge ${item.complexity_level === 'Low' ? 'success-badge' : 'warning-badge'}">${item.complexity_level}</span></td>
                        <td class="text-center">
                            <div style="display:flex; gap:6px; justify-content:center;">
                                <button class="btn btn-secondary btn-xs btn-load-history" data-history-id="${item.id}">View</button>
                                <button class="btn btn-danger btn-xs btn-delete-history" data-history-id="${item.id}">Delete</button>
                            </div>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });

                attachHistoryOpenListeners();
                attachHistoryDeleteListeners();
            }
        } catch (err) {
            showToast(`Failed to load history: ${err.message}`, "error");
        }
    }

    function attachHistoryOpenListeners() {
        document.querySelectorAll('.btn-load-history').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.getAttribute('data-history-id');
                try {
                    const res = await fetch(`${API_BASE}/api/analysis/${id}`);
                    const result = await res.json();
                    if (res.ok && result.data) {
                        onAnalysisComplete(result.data);
                    } else {
                        showToast("Could not load analysis record.", "error");
                    }
                } catch (err) {
                    showToast(`Load failed: ${err.message}`, "error");
                }
            });
        });
    }

    function attachHistoryDeleteListeners() {
        document.querySelectorAll('.btn-delete-history').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.getAttribute('data-history-id');
                if (confirm(`Are you sure you want to delete analysis #${id}?`)) {
                    try {
                        const res = await fetch(`${API_BASE}/api/analysis/${id}`, { method: 'DELETE' });
                        if (res.ok) {
                            showToast(`Analysis #${id} deleted.`, "info");
                            loadHistoryTable();
                            loadGlobalDashboardData();
                        } else {
                            showToast("Failed to delete analysis.", "error");
                        }
                    } catch (err) {
                        showToast(`Delete failed: ${err.message}`, "error");
                    }
                }
            });
        });
    }

    function escapeHtml(text) {
        if (!text) return '';
        const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // ==========================================
    // 16. INITIAL STARTUP
    // ==========================================
    loadGlobalDashboardData();
    switchView('landing');
});
