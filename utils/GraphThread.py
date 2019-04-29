import time

import networkx
import logging
from extended_networkx_tools import Creator, Analytics
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
        self.print("(%d) Received graph (%d nodes)" % (task['Id'], task['NodeCount']))

        # Solve it and get a graph
        start = timer()
        graph = self.solve_task(task=task)
        end = timer()
        # Calculate deltatime
        delta_time = end - start
        time_minutes = round((delta_time / 60)-0.49)
        time_seconds = round(delta_time % 60)

        self.print("(%d) Solved graph (%d nodes) in %sm %ss" % (task['Id'], task['NodeCount'], time_minutes, time_seconds))

        # Get the results
        results = self.get_results(graph=graph, task=task)

        # Upload the results to the server
        self.upload_results(results=results, graph=graph)
        self.print("(%d) Uploaded results (%d nodes)" % (task['Id'], task['NodeCount']))

    def get_task(self):
        task = self.server.get_task(self.client_name)
        return task

    @staticmethod
    def solve_task(task):
        # Get relevant data
        node_count = task['NodeCount']
        optimization = task['Optimization']

        # Create the graph object
        graph = Creator.from_random(node_count)
        # Initialize the solver
        annealing = Annealing2(graph)
        annealing.set_optimization_parameter(optimization)
        # Solve the graph
        graph = annealing.solve(False)

        return graph

    @staticmethod
    def get_results(graph: networkx.Graph, task):
        task['EdgeCount'] = len(graph.edges)
        task['ConvergenceRate'] = float(Analytics.convergence_rate(graph))
        task['EnergyCost'] = Annealing2.get_optimization_function(task['Optimization'])(graph).real
        task['EdgeCost'] = Analytics.total_edge_cost(graph)
        task['Diameter'] = networkx.diameter(graph)
        task['AverageEccentricity'] = Analytics.get_average_eccentricity(graph)

        return task

    def upload_results(self, results, graph: networkx.Graph):
        worker_id = results['Id']
        results['Eccentricities'] = Analytics.get_eccentricity_distribution(graph)

        self.server.upload_results(worker_id, results)
        self.server.upload_results(worker_id, {'Nodes': Analytics.get_node_dict(graph)})
        self.server.upload_results(worker_id, {'Edges': Analytics.get_edge_dict(graph)})

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