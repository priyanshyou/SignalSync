let globalLeads = [];

async function loadData() {
    const tbody = document.getElementById('table-body');
    const loadingHtml = '<tr><td colspan="6" class="loading">Loading live data... <i class="fas fa-circle-notch fa-spin"></i></td></tr>';
    tbody.innerHTML = loadingHtml;

    try {
        const response = await fetch('/api/leads?limit=500');
        const data = await response.json();

        globalLeads = data.data;
        updateUI(globalLeads);

    } catch (error) {
        console.error("Error loading data:", error);
        tbody.innerHTML = `<tr><td colspan="6" style="color: #ef4444; text-align:center; padding: 3rem;">Failed to connect to API. Server is offline.</td></tr>`;
    }
}

async function triggerAISearch() {
    const searchTerm = prompt("Enter a semantic query (e.g., 'Looking for senior database engineer roles focused on scalability'):");
    if (!searchTerm) {
        return loadData(); // reset if cancelled
    }

    // Switch button state
    const btn = document.getElementById('ai-search-btn');
    btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Searching Vector Space...';

    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(searchTerm)}`);
        const data = await response.json();
        const results = data.data;

        // Show AI results 
        document.getElementById('search').value = '';
        document.getElementById('stack-filter').value = '';
        renderTable(results);

        // Alert user
        if (results.length > 0) {
            btn.innerHTML = `<i class="fas fa-check"></i> Found ${results.length} Matches`;
        } else {
            btn.innerHTML = `<i class="fas fa-times"></i> No matches`;
        }
    } catch (e) {
        console.error(e);
        btn.innerHTML = `<i class="fas fa-brain"></i> AI Semantic Search`;
    }

    setTimeout(() => {
        btn.innerHTML = `<i class="fas fa-brain"></i> AI Semantic Search`;
    }, 5000);
}

function updateUI(leads) {
    // Update metrics
    document.getElementById('total-leads').innerText = leads.length;

    const stackCounts = {};

    leads.forEach(lead => {
        if (lead.tech_stack) {
            lead.tech_stack.split(',').forEach(s => {
                const tech = s.trim();
                stackCounts[tech] = (stackCounts[tech] || 0) + 1;
            });
        }
    });

    document.getElementById('tech-stacks').innerText = Object.keys(stackCounts).length;

    renderTable(leads);
}

function renderTable(leads) {
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '';

    if (leads.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="loading">No jobs found in database yet. Pipeline might still be scraping. Let the automation run.</td></tr>`;
        return;
    }

    leads.forEach(lead => {
        const tr = document.createElement('tr');

        let techHtml = '<span class="text-secondary">-</span>';
        if (lead.tech_stack) {
            techHtml = lead.tech_stack.split(',')
                .filter(t => t.trim() !== '')
                .map(t => `<span class="tech-tag">${t.trim()}</span>`)
                .join('');
        }

        tr.innerHTML = `
            <td style="font-weight: 600;">${lead.company}</td>
            <td>${lead.title}</td>
            <td>${techHtml}</td>
            <td style="color: var(--text-secondary); font-size: 0.9rem;"><i class="fas fa-map-marker-alt"></i> ${lead.location}</td>
            <td style="font-size: 0.9rem;">${lead.date_posted}</td>
            <td><a href="${lead.url}" target="_blank" class="action-link">View Lead <i class="fas fa-external-link-alt" style="font-size:0.7rem;"></i></a></td>
        `;
        tbody.appendChild(tr);
    });
}

function filterTable() {
    const searchTerm = document.getElementById('search').value.toLowerCase();
    const stackFilter = document.getElementById('stack-filter').value.toLowerCase();

    const filtered = globalLeads.filter(lead => {
        const cMatch = lead.company && lead.company.toLowerCase().includes(searchTerm);
        const tMatch = lead.title && lead.title.toLowerCase().includes(searchTerm);
        const sMatch = lead.tech_stack && lead.tech_stack.toLowerCase().includes(searchTerm);

        const stackMatch = stackFilter === "" || (lead.tech_stack && lead.tech_stack.toLowerCase().includes(stackFilter));

        return (cMatch || tMatch || sMatch) && stackMatch;
    });

    renderTable(filtered);
}

window.onload = loadData;
// Auto refresh every 60 seconds
setInterval(loadData, 60000);
