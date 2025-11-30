
def build_dependency_graph(tasks):
    """
    Builds a graph where key is task_id and value is list of dependency task_ids.
    tasks: list of task dicts, expected to have 'id' and 'dependencies' (list of ids)
    """
    graph = {}
    for task in tasks:
        t_id = task.get('id')
        if t_id is not None:
            # Ensure dependencies are a list of IDs
            deps = task.get('dependencies', [])
            # If deps are objects, extract IDs (handle both cases)
            dep_ids = []
            for d in deps:
                if isinstance(d, dict):
                    dep_ids.append(d.get('id'))
                elif hasattr(d, 'id'): # Django model
                    dep_ids.append(d.id)
                else:
                    dep_ids.append(d) # Assume it's an ID
            
            graph[t_id] = dep_ids
    return graph

def detect_cycles(graph):
    """
    Returns a list of task IDs involved in a cycle, or None if no cycle.
    Uses DFS.
    """
    visited = set()
    recursion_stack = set()
    
    def dfs(node, path):
        visited.add(node)
        recursion_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, path):
                    return True
            elif neighbor in recursion_stack:
                return True
        
        recursion_stack.remove(node)
        path.pop()
        return False

    for node in graph:
        if node not in visited:
            path = []
            if dfs(node, path):
                return path # Return the path that forms the cycle
    return None

def calculate_dependents_count(tasks):
    """
    Enriches tasks with 'dependents_count' (number of tasks that depend on this task).
    """
    # 1. Build reverse graph (who depends on me?)
    # task_id -> list of tasks that depend on it
    reverse_graph = {}
    
    # Initialize for all tasks
    for task in tasks:
        t_id = task.get('id')
        if t_id is not None:
            reverse_graph[t_id] = []
            
    for task in tasks:
        t_id = task.get('id')
        deps = task.get('dependencies', [])
        
        # Normalize deps to IDs
        dep_ids = []
        for d in deps:
            if isinstance(d, dict): dep_ids.append(d.get('id'))
            elif hasattr(d, 'id'): dep_ids.append(d.id)
            else: dep_ids.append(d)
            
        for dep_id in dep_ids:
            if dep_id in reverse_graph:
                reverse_graph[dep_id].append(t_id)
                
    # 2. Update tasks
    for task in tasks:
        t_id = task.get('id')
        if t_id is not None:
            task['dependents_count'] = len(reverse_graph.get(t_id, []))
            
    return tasks
