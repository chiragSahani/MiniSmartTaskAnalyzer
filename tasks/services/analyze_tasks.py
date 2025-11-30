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

        strategy = STRATEGIES.get(strategy_name)
        if not strategy:
            raise ValueError(f"Unknown strategy: {strategy_name}")


        graph = build_dependency_graph(tasks)
        cycle = detect_cycles(graph)
        

        
        tasks = calculate_dependents_count(tasks)
        

        scored_tasks = strategy.score_tasks(tasks, config=config)
        

        if cycle:
            cycle_set = set(cycle)
            for task in scored_tasks:
                if task.get('id') in cycle_set:
                    task['has_cycle'] = True
                    task['explanation'] = f"[CYCLE DETECTED] {task.get('explanation', '')}"

        return scored_tasks

class SuggestTasksUseCase:
    def execute(self, tasks, config=None):

        analyzer = AnalyzeTasksUseCase()
        scored_tasks = analyzer.execute(tasks, strategy_name="smart_balance", config=config)
        

        return scored_tasks[:3]
