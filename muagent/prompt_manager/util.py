from collections import defaultdict



class GraphCycleError(Exception):
    """Custom exception for graph cycle detection."""
    pass



def edges_to_graph_with_cycle_detection(intervals):
    """Converts a list of intervals into a directed graph and checks for cycles.

    Args:
        intervals (list of tuple): List of intervals where each interval is defined by (start, end).

    Returns:
        tuple: A tuple containing a list of start nodes (nodes with indegree of 0) and the constructed graph.

    Raises:
        GraphCycleError: If the graph contains a cycle.
    """

    graph = defaultdict(list)  # Adjacency list for the graph
    indegree = defaultdict(int)  # Count of incoming edges for each node

    # Build the graph and the indegree table
    for start, end in intervals:
        graph[start].append(end)  # Add directed edge from start to end
        indegree[end] += 1  # Increment indegree of end node
        # Ensure every node is in the graph (even nodes without outgoing edges)
        if start not in indegree:
            indegree[start] = 0  # Initialize indegree for start node

    # Find all starting nodes (indegree of 0)
    start_nodes = [node for node in indegree if indegree[node] == 0]

    # Detect cycle in the graph
    if detect_cycle(graph):
        raise GraphCycleError("Graph contains a cycle!")  # Raise error if cycle is found

    return start_nodes, graph



def detect_cycle(graph):
    """Detects if a directed graph contains a cycle using DFS.

    Args:
        graph (dict): The adjacency list of the graph.

    Returns:
        bool: True if a cycle is detected, False otherwise.
    """
    
    visited = set()  # To keep track of visited nodes
    rec_stack = set()  # To keep track of nodes currently in the recursion stack

    def dfs(node):
        """Performs a DFS on the graph to detect cycles.

        Args:
            node: Current node being visited.

        Returns:
            bool: True if a cycle is detected.
        """
        # If node is in recursion stack, a cycle is found
        if node in rec_stack:
            return True
        # If node is already visited, no need to check it again
        if node in visited:
            return False

        # Mark the current node as visited and add to recursion stack
        visited.add(node)
        rec_stack.add(node)

        # Use list() to copy neighbors to avoid modifying while iterating
        for neighbor in list(graph[node]):
            if dfs(neighbor):  # Recursive call for each neighbor
                return True  # Cycle detected in the neighbor

        # Remove the node from the recursion stack after visiting
        rec_stack.remove(node)
        return False  # No cycle detected in this path

    # Iterate over each node in the graph to detect cycles
    for node in list(graph.keys()):
        if node not in visited:  # Proceed if the node hasn't been visited yet
            if dfs(node):  # Start DFS
                return True  # Cycle found

    return False  # No cycles found in the graph