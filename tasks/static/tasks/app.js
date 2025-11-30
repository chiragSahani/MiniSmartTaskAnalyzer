document.addEventListener('DOMContentLoaded', () => {
    let tasks = [];

    // Elements
    const singleForm = document.getElementById('single-task-form');
    const bulkJsonInput = document.getElementById('bulk-json');
    const loadBulkBtn = document.getElementById('load-bulk-btn');
    const taskStagingArea = document.getElementById('task-staging-area');
    const clearTasksBtn = document.getElementById('clear-tasks-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const strategySelect = document.getElementById('strategy');
    const resultsArea = document.getElementById('results-area');
    const analyzedList = document.getElementById('analyzed-list');
    const suggestionsList = document.getElementById('suggestions-list');

    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(`${btn.dataset.tab}-tab`).classList.add('active');
        });
    });

    // Add Single Task
    singleForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(singleForm);

        const depsStr = formData.get('dependencies');
        const deps = depsStr ? depsStr.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n)) : [];

        const task = {
            id: formData.get('id') ? parseInt(formData.get('id')) : Date.now(),
            title: formData.get('title'),
            due_date: formData.get('due_date') || null,
            estimated_hours: parseFloat(formData.get('estimated_hours')),
            importance: parseInt(formData.get('importance')),
            dependencies: deps
        };

        tasks.push(task);
        renderStaging();
        singleForm.reset();
        document.getElementById('importance').nextElementSibling.value = 5;

        // Micro-interaction: Scroll to bottom of list
        taskStagingArea.scrollTop = taskStagingArea.scrollHeight;
    });

    // Load Bulk JSON
    loadBulkBtn.addEventListener('click', () => {
        try {
            const json = JSON.parse(bulkJsonInput.value);
            if (Array.isArray(json)) {
                tasks = [...tasks, ...json];
                renderStaging();
                bulkJsonInput.value = '';
            } else {
                alert('Input must be a JSON array of task objects.');
            }
        } catch (e) {
            alert('Invalid JSON format. Please check your syntax.');
        }
    });

    // Clear Tasks
    clearTasksBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all tasks?')) {
            tasks = [];
            renderStaging();
            resultsArea.classList.add('hidden');
        }
    });

    // Analyze
    analyzeBtn.addEventListener('click', async () => {
        if (tasks.length === 0) {
            alert('Please add some tasks first.');
            return;
        }

        const strategy = strategySelect.value;
        const originalText = analyzeBtn.innerHTML;
        analyzeBtn.innerHTML = '<span class="spinner"></span> Analyzing...';
        analyzeBtn.disabled = true;

        try {
            // 1. Analyze
            const analyzeRes = await fetch(`/api/tasks/analyze/?strategy=${strategy}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(tasks)
            });

            if (!analyzeRes.ok) throw new Error(await analyzeRes.text());
            const analyzedTasks = await analyzeRes.json();

            // 2. Get Suggestions (using same tasks)
            const suggestRes = await fetch('/api/tasks/suggest/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(tasks)
            });

            if (!suggestRes.ok) throw new Error(await suggestRes.text());
            const suggestions = await suggestRes.json();

            renderResults(analyzedTasks, suggestions);
        } catch (err) {
            console.error(err);
            alert('Analysis failed: ' + err.message);
        } finally {
            analyzeBtn.innerHTML = originalText;
            analyzeBtn.disabled = false;
        }
    });

    function renderStaging() {
        if (tasks.length === 0) {
            taskStagingArea.innerHTML = `
                <div class="empty-state">
                    <svg width="48" height="48" fill="none" stroke="var(--text-muted)" stroke-width="1.5" style="margin-bottom: 1rem;"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
                    <p>Your task list is empty.</p>
                    <small>Add tasks from the left panel to get started.</small>
                </div>`;
            return;
        }
        taskStagingArea.innerHTML = tasks.map(t => `
            <div class="task-card" style="animation: fadeIn 0.3s ease;">
                <div class="task-content">
                    <div class="task-title">${t.title}</div>
                    <div class="task-meta">
                        <span class="meta-item">ID: ${t.id || '-'}</span>
                        <span class="meta-item">Due: ${t.due_date || 'None'}</span>
                        <span class="meta-item">Imp: ${t.importance}</span>
                        <span class="meta-item">Est: ${t.estimated_hours}h</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    function renderResults(analyzed, suggestions) {
        resultsArea.classList.remove('hidden');

        analyzedList.innerHTML = analyzed.map((t, index) => createTaskCard(t, false, index)).join('');
        suggestionsList.innerHTML = suggestions.map((t, index) => createTaskCard(t, true, index)).join('');

        // Scroll to results
        resultsArea.scrollIntoView({ behavior: 'smooth' });
    }

    function createTaskCard(task, isMini = false, index = 0) {
        const badgeClass = `badge-${task.priority_level.toLowerCase()}`;
        const cycleWarning = task.has_cycle ?
            '<span style="color:var(--danger); font-weight:bold; margin-left:0.5rem; display:inline-flex; align-items:center; gap:0.25rem;"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg> Cycle</span>'
            : '';
        const delay = index * 0.05; // Staggered animation

        if (isMini) {
            return `
                <div class="mini-task" style="animation: fadeIn 0.5s ease ${delay}s backwards;">
                    <strong>${task.title}</strong>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span>Score: ${task.score}</span>
                        <span class="badge ${badgeClass}" style="font-size:0.6rem;">${task.priority_level}</span>
                    </div>
                </div>
            `;
        }

        return `
            <div class="task-card" style="animation: fadeIn 0.5s ease ${delay}s backwards;">
                <div class="task-content">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div class="task-title">
                            ${task.title}
                            ${cycleWarning}
                        </div>
                        <span class="badge ${badgeClass}">${task.priority_level}</span>
                    </div>
                    
                    <div class="task-meta">
                        <span class="meta-item">
                            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                            ${task.due_date || 'No Date'}
                        </span>
                        <span class="meta-item">
                            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                            ${task.estimated_hours}h
                        </span>
                        <span class="meta-item">
                            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                            Imp: ${task.importance}
                        </span>
                    </div>
                    
                    <div style="margin-top: 0.75rem; font-size: 0.9rem; color: var(--text-main); background: var(--bg-body); padding: 0.5rem; border-radius: var(--radius-sm);">
                        ${task.explanation}
                    </div>
                </div>
                
                <div class="score-indicator">
                    <div class="score-circle">
                        ${task.score}
                    </div>
                    <span style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem;">SCORE</span>
                </div>
            </div>
        `;
    }
});
