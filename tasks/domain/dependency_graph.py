
def build_dependency_graph(tasks):

    graph = {}
    for task in tasks:
        t_id = task.get('id')
        if t_id is not None:

            deps = task.get('dependencies', [])

            dep_ids = []
            for d in deps:
                if isinstance(d, dict):
                    dep_ids.append(d.get('id'))
                elif hasattr(d, 'id'):
                    dep_ids.append(d.id)
                else:
                    dep_ids.append(d)
            
            graph[t_id] = dep_ids
    return graph

def detect_cycles(graph):

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
                return path
    return None

def calculate_dependents_count(tasks):

    reverse_graph = {}
    

    for task in tasks:
        t_id = task.get('id')
        if t_id is not None:
            reverse_graph[t_id] = []
            
    for task in tasks:
        t_id = task.get('id')
        deps = task.get('dependencies', [])
        

        dep_ids = []
        for d in deps:
            if isinstance(d, dict): dep_ids.append(d.get('id'))
            elif hasattr(d, 'id'): dep_ids.append(d.id)
            else: dep_ids.append(d)
            
        for dep_id in dep_ids:
            if dep_id in reverse_graph:
                reverse_graph[dep_id].append(t_id)
                

    for task in tasks:
        t_id = task.get('id')
        if t_id is not None:
            task['dependents_count'] = len(reverse_graph.get(t_id, []))
            
    return tasks
