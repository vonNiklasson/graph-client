from ast import literal_eval
from typing import Dict

from extended_networkx_tools import AnalyticsGraph, Creator
from simulated_annealing import Annealing2

from utils.GraphUtils import GraphUtils


class Random:

    @staticmethod
    def solve(task) -> (AnalyticsGraph, Dict):
        # Get relevant data
        node_count = task['NodeCount']
        optimization = task['Optimization']
        extra_data = GraphUtils.parse_extra_data(task)

        area_dimension = node_count
        if 'area_dimension' in extra_data:
            area_dimension = extra_data['area_dimension']

        # Create the partial graph object
        graph = Creator.from_random(node_count, area_dimension=area_dimension)
        # Initialize the solver
        annealing = GraphUtils.get_annealer(graph=graph, task=task)
        annealing.set_optimization_parameter(optimization)
        # Solve the graph
        analytics_graph = annealing.solve()

        return analytics_graph, {}
