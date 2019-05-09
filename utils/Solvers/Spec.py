from typing import Dict

from extended_networkx_tools import AnalyticsGraph, Creator

from utils.GraphUtils import GraphUtils


class Spec:

    @staticmethod
    def solve(task) -> (AnalyticsGraph, Dict):
        # Get relevant data
        optimization = task['Optimization']

        nodes = GraphUtils.get_node_data(task)
        edges = GraphUtils.get_edge_data(task)

        # Create the partial graph object
        graph = Creator.from_spec(nodes, edges)
        # Initialize the solver
        annealing = GraphUtils.get_annealer(graph=graph, task=task)
        annealing.set_optimization_parameter(optimization)
        # Solve the graph
        analytics_graph = annealing.solve()

        return analytics_graph, {}
