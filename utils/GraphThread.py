import time
from typing import Tuple, List
from ast import literal_eval

import networkx
import logging
from extended_networkx_tools import Creator, Analytics, AnalyticsGraph
from simulated_annealing import Annealing2
from timeit import default_timer as timer
from utils.ServerUtil import ServerUtil
from datetime import datetime


class GraphThread:

    @staticmethod
    def start_thread(base_url, client_name, thread_id, color=None):
        current_sleep = 10
        gt = GraphThread(base_url, client_name, thread_id, color)
        while True:
            try:
                gt.run()
                current_sleep = 10
            except Exception as e:
                logging.exception("Failed when running thread")
                gt.print('Crashed, restarting in %d seconds' % current_sleep, Styles.FAIL)
                time.sleep(current_sleep)
                current_sleep += 10

    client_name: str
    server: ServerUtil
    thread_id: int
    color: None

    def __init__(self, base_url, client_name, thread_id, color):
        self.client_name = client_name
        self.thread_id = thread_id
        self.server = ServerUtil(base_url)
        self.color = color

    def run(self):
        # Get a new task from the server
        task = self.get_task()
        self.print("(%d) Received graph (%d nodes), type %s" % (task['Id'], task['NodeCount'], task['SolveType']))

        # Solve it and get a graph
        start = timer()
        analytics_graph = self.solve_task(task=task)
        end = timer()
        # Calculate deltatime
        delta_time = end - start
        time_minutes = round((delta_time / 60)-0.49)
        time_seconds = round(delta_time % 60)

        self.print("(%d) Solved graph (%d nodes) in %sm %ss" % (task['Id'], task['NodeCount'], time_minutes, time_seconds))

        # Get the results
        results = self.get_results(analytics_graph=analytics_graph, task=task)

        # Upload the results to the server
        self.upload_results(results=results, analytics_graph=analytics_graph)
        self.print("(%d) Uploaded results (%d nodes)" % (task['Id'], task['NodeCount']))

    def get_task(self):
        task = self.server.get_task(self.client_name)
        return task

    @staticmethod
    def solve_task(task) -> AnalyticsGraph:
        solve_type = task['SolveType']
        if solve_type == 'diff':
            return GraphThread.solve_task_diff(task)
        elif solve_type == 'spec':
            return GraphThread.solve_task_spec(task)
        elif solve_type == 'random':
            return GraphThread.solve_task_random(task)
        else:
            return GraphThread.solve_task_random(task)

    @staticmethod
    def solve_task_diff(task) -> AnalyticsGraph:
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
            return GraphThread.solve_task_spec(task)

        # Create the partial graph object
        partial_graph = Creator.from_spec(nodes, edges)
        removed_nodes = GraphThread.remove_nodes(partial_graph, removed_node_count)
        # Initialize the solver
        partial_annealing = Annealing2(partial_graph)
        partial_annealing.set_optimization_parameter(optimization)
        # Solve the graph
        partial_analytics_graph = partial_annealing.solve()

        # Create the fill graph, extend the partial with empty nodes
        full_graph = partial_analytics_graph.graph().copy()
        solve_for_nodes = GraphThread.append_nodes(full_graph, removed_nodes)

        # Initialize the solver
        full_annealing = Annealing2(full_graph)
        full_analytics_graph = full_annealing.solve(solve_for_nodes=solve_for_nodes)

        return full_analytics_graph

    @staticmethod
    def solve_task_spec(task) -> AnalyticsGraph:
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
        annealing = Annealing2(graph)
        annealing.set_optimization_parameter(optimization)
        # Solve the graph
        analytics_graph = annealing.solve()

        return analytics_graph

    @staticmethod
    def solve_task_random(task) -> AnalyticsGraph:
        # Get relevant data
        node_count = task['NodeCount']
        optimization = task['Optimization']

        # Create the partial graph object
        graph = Creator.from_random(node_count)
        # Initialize the solver
        annealing = Annealing2(graph)
        annealing.set_optimization_parameter(optimization)
        # Solve the graph
        analytics_graph = annealing.solve()

        return analytics_graph

    @staticmethod
    def get_results(analytics_graph: AnalyticsGraph, task):
        task['EdgeCount'] = analytics_graph.get_dimension()
        task['ConvergenceRate'] = float(analytics_graph.get_convergence_rate())
        task['EnergyCost'] = Annealing2.get_optimization_function(task['Optimization'])(analytics_graph).real
        task['EdgeCost'] = analytics_graph.get_edge_cost()
        task['Diameter'] = networkx.diameter(analytics_graph.graph())
        task['AverageEccentricity'] = Analytics.get_average_eccentricity(analytics_graph.graph())

        return task

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
            Creator.add_weighted_edge(nxg, node[0], node[0]-1)
            solve_for_nodes.append(node[0])
        return solve_for_nodes

    def upload_results(self, results, analytics_graph: AnalyticsGraph):
        worker_id = results['Id']
        results['Eccentricities'] = Analytics.get_eccentricity_distribution(analytics_graph.graph())

        self.server.upload_results(worker_id, results)
        self.server.upload_results(worker_id, {'Nodes': Analytics.get_node_dict(analytics_graph.graph())})
        self.server.upload_results(worker_id, {'Edges': Analytics.get_edge_dict(analytics_graph.graph())})

    def print(self, msg, type=None):
        start_color = None

        if type is None:
            start_color = self.color

        ts = datetime.now().strftime('%H:%M:%S')
        print("%s%s%s %s P%d: %s%s" % (Styles.BOLD, ts, Styles.ENDC, start_color, self.thread_id, msg, Styles.ENDC))

class Styles:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'