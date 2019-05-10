from ast import literal_eval
from typing import List, Tuple

import networkx
from extended_networkx_tools import Creator, AnalyticsGraph, Analytics
from simulated_annealing import Annealing2


class GraphUtils:

    @staticmethod
    def remove_nodes(nxg: networkx.Graph, remove_node_count: int):
        removed_nodes = []
        node_count = len(nxg.nodes)
        for i in range(0, remove_node_count):
            remove_id = node_count - i - 1
            removed_nodes.append((remove_id, nxg.nodes[remove_id]['x'], nxg.nodes[remove_id]['y']))
            nxg.remove_node(remove_id)
        removed_nodes.reverse()
        return removed_nodes

    @staticmethod
    def append_nodes(nxg: networkx.Graph, nodes: List[Tuple[int, int, int]]):
        solve_for_nodes = []
        for node in nodes:
            nxg.add_node(node[0], x=node[1], y=node[2])
            Creator.add_weighted_edge(nxg, node[0], node[0 ] -1)
            solve_for_nodes.append(node[0])
        return solve_for_nodes

    @staticmethod
    def get_results(analytics_graph: AnalyticsGraph, task, custom_data=None):
        task['EdgeCount'] = len(analytics_graph.graph().edges)
        task['ConvergenceRate'] = float(analytics_graph.get_convergence_rate())
        task['EnergyCost'] = Annealing2.get_optimization_function(task['Optimization'])(analytics_graph).real
        task['EdgeCost'] = analytics_graph.get_edge_cost()
        task['Diameter'] = networkx.diameter(analytics_graph.graph())
        task['AverageEccentricity'] = Analytics.get_average_eccentricity(analytics_graph.graph())
        task['Eccentricities'] = Analytics.get_eccentricity_distribution(analytics_graph.graph())

        if custom_data is not None:
            task['CustomData'] = custom_data

        return task

    @staticmethod
    def parse_extra_data(task):
        extra_data = {}
        if len(task['ExtraData']) > 0:
            extra_data = literal_eval(task['ExtraData'])
        return extra_data

    @staticmethod
    def get_annealer(graph: networkx.Graph, task):
        extra_data = GraphUtils.parse_extra_data(task)

        start_temp = extra_data['start_temp'] if 'start_temp' in extra_data else 10000
        iterations = extra_data['iterations'] if 'iterations' in extra_data else 200

        return Annealing2(graph, start_temperature=start_temp, iterations=iterations)

    @staticmethod
    def get_node_data(task):
        nodes = {}
        extra_data = GraphUtils.parse_extra_data(task)
        if 'NodeData' in task and task['NodeData'] is not None:
            nodes = literal_eval(task['NodeData'].replace('[', '(').replace(']', ')').replace('"', ''))
        elif 'NodeData' in extra_data and extra_data['NodeData'] is not None:
            nodes = {}
            for node_id, coord in extra_data['NodeData'].items():
                nodes[int(node_id)] = tuple(coord)
        return nodes

    @staticmethod
    def get_edge_data(task):
        edges = {}
        extra_data = GraphUtils.parse_extra_data(task)
        if 'EdgeData' in task and task['EdgeData'] is not None:
            edges = literal_eval(task['EdgeData'].replace('"', ''))
        elif 'EdgeData' in extra_data and extra_data['EdgeData'] is not None:
            edges = {}
            for node_id, con_nodes in extra_data['EdgeData'].items():
                edges[int(node_id)] = map(int, con_nodes)
        return edges
