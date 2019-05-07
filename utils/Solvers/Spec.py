from ast import literal_eval
from typing import Dict

from extended_networkx_tools import AnalyticsGraph, Creator
from simulated_annealing import Annealing2

from utils.GraphUtils import GraphUtils


class Spec:

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

        # Create the partial graph object
        graph = Creator.from_spec(nodes, edges)
        # Initialize the solver
        annealing = GraphUtils.get_annealer(graph=graph, task=task)
        annealing.set_optimization_parameter(optimization)
        # Solve the graph
        analytics_graph = annealing.solve()

        return analytics_graph, {}
