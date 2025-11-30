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
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(`${btn.dataset.tab}-tab`).classList.add('active');
        });
    });

    // Add Single Task
    singleForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(singleForm);
        
        const deps = formData.get('dependencies')
            .split(',')
            .map(s => parseInt(s.trim()))
            .filter(n => !isNaN(n));

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
            alert('Invalid JSON format.');
        }
    });

    // Clear Tasks
    clearTasksBtn.addEventListener('click', () => {
        tasks = [];
        renderStaging();
        resultsArea.classList.add('hidden');
    });

    // Analyze
    analyzeBtn.addEventListener('click', async () => {
        if (tasks.length === 0) {
            alert('Please add some tasks first.');
            return;
        }

        const strategy = strategySelect.value;
        analyzeBtn.textContent = 'Analyzing...';
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
            analyzeBtn.textContent = 'Analyze & Prioritize';
            analyzeBtn.disabled = false;
        }
    });

    function renderStaging() {
        if (tasks.length === 0) {
            taskStagingArea.innerHTML = '<div class="empty-state">No tasks added yet.</div>';
            return;
        }
        taskStagingArea.innerHTML = tasks.map(t => `
            <div class="task-item">
                <div>
                    <strong>${t.title}</strong>
                    <div class="task-meta">
                        <span>ID: ${t.id || '-'}</span>
                        <span>Due: ${t.due_date || 'None'}</span>
                        <span>Imp: ${t.importance}</span>
                        <span>Est: ${t.estimated_hours}h</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    function renderResults(analyzed, suggestions) {
        resultsArea.classList.remove('hidden');
        
        analyzedList.innerHTML = analyzed.map(t => createTaskCard(t)).join('');
        suggestionsList.innerHTML = suggestions.map(t => createTaskCard(t, true)).join('');
    }

    function createTaskCard(task, isMini = false) {
        const badgeClass = task.priority_level.toLowerCase();
        const cycleWarning = task.has_cycle ? '<span style="color:red; font-weight:bold;">⚠️ CYCLE</span>' : '';
        
        if (isMini) {
            return `
                <div class="task-item">
                    <div>
                        <strong>${task.title}</strong>
                        <div class="task-meta">
                            <span>Score: ${task.score}</span>
                        </div>
                    </div>
                </div>
            `;
        }

        return `
            <div class="task-item">
                <div style="flex: 1;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong>${task.title} ${cycleWarning}</strong>
                        <span class="badge ${badgeClass}">${task.priority_level}</span>
                    </div>
                    <div class="task-meta">
                        <span>Due: ${task.due_date || 'N/A'}</span>
                        <span>Effort: ${task.estimated_hours}h</span>
                        <span>Imp: ${task.importance}</span>
                    </div>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem; color: var(--text);">
                        ${task.explanation}
                    </div>
                </div>
                <div class="score-circle" style="margin-left: 1rem;">
                    ${task.score}
                </div>
            </div>
        `;
    }
});
