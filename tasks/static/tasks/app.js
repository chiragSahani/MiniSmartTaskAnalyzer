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
                    </div >
                </div >

            <div class="score-indicator">
                <div class="score-circle">
                    ${task.score}
                </div>
                <span style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem;">SCORE</span>
            </div>
            </div >
            `;
    }
});
