import time

import networkx
from extended_networkx_tools import Creator, Analytics
from simulated_annealing import Annealing2
from utils.ServerUtil import ServerUtil
from datetime import datetime


class GraphThread:

    @staticmethod
    def start_thread(base_url, client_name, thread_id):
        current_sleep = 10
        gt = GraphThread(base_url, client_name, thread_id)
        while True:
            try:
                gt.run()
                current_sleep = 10
            except Exception as e:
                gt.print('Crashed, restarting in %d seconds' % current_sleep)
                time.sleep(current_sleep)
                current_sleep += 10

    client_name: str
    server: ServerUtil
    thread_id: int

    def __init__(self, base_url, client_name, thread_id):
        self.client_name = client_name
        self.thread_id = thread_id
        self.server = ServerUtil(base_url)

    def run(self):
        # Get a new task from the server
        task = self.get_task()
        self.print("(%d) Received graph with %d nodes" % (task['Id'], task['NodeCount']))

        # Solve it and get a graph
        graph = self.solve_task(task=task)
        self.print("(%d) Solved graph" % task['Id'])
        # Get the results
        results = self.get_results(graph=graph, task=task)

        # Upload it to the server
        self.upload_results(results=results, graph=graph)
        self.print("(%d) Uploaded results" % (task['Id']))

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
        task['ConvergenceRate'] = Analytics.convergence_rate(graph)
        task['EnergyCost'] = Annealing2.get_optimization_function(task['Optimization'])(graph)
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

    def print(self, msg):
        ts = datetime.now().strftime('%H:%M:%S')
        print("%s   P%d: %s" % (ts, self.thread_id, msg))
