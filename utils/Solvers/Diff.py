from ast import literal_eval
from typing import Dict

from extended_networkx_tools import AnalyticsGraph, Creator
from simulated_annealing import Annealing2

from utils import Solvers
from utils.GraphUtils import GraphUtils


class Diff:

    @staticmethod
    def solve(task) -> (AnalyticsGraph, Dict):
        # Get relevant data
        optimization = task['Optimization']

        nodes = {}
        edges = {}

        if task['NodeData'] is not None:
            nodes = literal_eval(task['NodeData'])
        if task['EdgeData'] is not None:
            edges = literal_eval(task['EdgeData'])

        removed_node_count = task['RemovedNodeCount']

        # If there's no nodes to be removed, it's rather a graph to be solved
        # from spec.
        if removed_node_count == 0:
            return Solvers.Random.solve(task)

        # Create the partial graph object
        partial_graph = Creator.from_spec(nodes, edges)
        removed_nodes = GraphUtils.remove_nodes(partial_graph, removed_node_count)
        # Initialize the solver
        partial_annealing = GraphUtils.get_annealer(graph=partial_graph, task=task)
        partial_annealing.set_optimization_parameter(optimization)
        # Solve the graph
        partial_analytics_graph = partial_annealing.solve()

        # Create the fill graph, extend the partial with empty nodes
        full_graph = partial_analytics_graph.graph().copy()
        solve_for_nodes = GraphUtils.append_nodes(full_graph, removed_nodes)

        # Initialize the solver
        full_annealing = GraphUtils.get_annealer(graph=full_graph, task=task)

        full_analytics_graph = full_annealing.solve(solve_for_nodes=solve_for_nodes)

        return full_analytics_graph, {}
