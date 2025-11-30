from tasks.domain.scoring_strategies import (
    FastestWinsStrategy,
    HighImpactStrategy,
    DeadlineDrivenStrategy,
    SmartBalanceStrategy
)
from tasks.domain.dependency_graph import (
    build_dependency_graph,
    detect_cycles,
    calculate_dependents_count
)

STRATEGIES = {
    "fastest_wins": FastestWinsStrategy(),
    "high_impact": HighImpactStrategy(),
    "deadline_driven": DeadlineDrivenStrategy(),
    "smart_balance": SmartBalanceStrategy(),
}

class AnalyzeTasksUseCase:
    def execute(self, tasks, strategy_name="smart_balance", config=None):
        """
        tasks: list of task dicts
        strategy_name: string key for strategy
        config: dict of configuration overrides
        """
        strategy = STRATEGIES.get(strategy_name)
        if not strategy:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        # 1. Enrich with dependency info (dependents_count)
        # This is needed for Smart Balance, but good for all to have.
        # Also check for cycles.
        graph = build_dependency_graph(tasks)
        cycle = detect_cycles(graph)
        
        # We can attach cycle info to the result metadata or raise error.
        # Requirement says "Detect circular dependencies" and "Bonus: visualization hint".
        # Let's attach a warning to the tasks involved in the cycle.
        
        tasks = calculate_dependents_count(tasks)
        
        # 2. Score and Sort
        scored_tasks = strategy.score_tasks(tasks, config=config)
        
        # 3. Add cycle warnings if any
        if cycle:
            cycle_set = set(cycle)
            for task in scored_tasks:
                if task.get('id') in cycle_set:
                    task['has_cycle'] = True
                    task['explanation'] = f"[CYCLE DETECTED] {task.get('explanation', '')}"

        return scored_tasks

class SuggestTasksUseCase:
    def execute(self, tasks, config=None):
        """
        Returns top 3 tasks using Smart Balance strategy.
        """
        analyzer = AnalyzeTasksUseCase()
        scored_tasks = analyzer.execute(tasks, strategy_name="smart_balance", config=config)
        
        # Filter out completed tasks if we had a status field (we don't yet).
        # Just take top 3.
        return scored_tasks[:3]
