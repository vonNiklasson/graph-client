from typing import Dict

import networkx as nx
import numpy as np

from extended_networkx_tools import AnalyticsGraph, Creator

from utils.GraphUtils import GraphUtils
from utils.Solvers import Random, Spec


class Field:

    @staticmethod
    def solve(task) -> (AnalyticsGraph, Dict):

        recalc = False
        if 'Recalc' in task:
            recalc = task['Recalc'] == 'True'

        if recalc:
            nodes = GraphUtils.get_node_data(task)
            edges = GraphUtils.get_edge_data(task)
            graph = Creator.from_spec(nodes, edges)
            analytics_graph = AnalyticsGraph(graph)
            custom_data = {}
        else:
            if 'NodeData' in task:
                analytics_graph, custom_data = Spec.solve(task)
            else:
                # Pass the graph to the random solver
                analytics_graph, custom_data = Random.solve(task)

        # Get the custom results from the field
        custom_results = Field.get_custom_results(analytics_graph.graph(), task)
        custom_data.update(custom_results)

        return analytics_graph, custom_data

    @staticmethod
    def get_coverage_matrix(nxg: nx.Graph, area_dimension: int, radius: int, overlap=False):
        mx = np.zeros((area_dimension, area_dimension))

        for node in nxg.nodes(data=True):
            x = node[1]['x']
            y = node[1]['y']

            # Get the offset area for x coordinate
            x_start = max(x-radius, 0)
            x_stop = min(x+radius+1, area_dimension)
            # Get the offset area for y coordinate
            y_start = max(y-radius, 0)
            y_stop = min(y+radius+1, area_dimension)

            # Fill the radius area
            if not overlap:
                mx[x_start:x_stop, y_start:y_stop] = 1
            else:
                mx[x_start:x_stop, y_start:y_stop] += 1

        return mx

    @staticmethod
    def get_detection_matrix(nxg: nx.Graph, area_dimension: int, radius: int):
        mx = np.zeros((area_dimension, area_dimension))

        ecc = nx.eccentricity(nxg)

        for node in nxg.nodes(data=True):
            node_id = node[0]
            x = node[1]['x']
            y = node[1]['y']

            # Get the offset area for x coordinate
            x_start = max(x-radius, 0)
            x_stop = min(x+radius+1, area_dimension)
            # Get the offset area for y coordinate
            y_start = max(y-radius, 0)
            y_stop = min(y+radius+1, area_dimension)

            # Get the current eccentricity
            eccentricity = ecc[node_id]

            # Get a logical mask for the current area that will replace higher eccentricity
            # and add if zero
            mask = np.logical_or(
                mx[x_start:x_stop, y_start:y_stop] > eccentricity,
                mx[x_start:x_stop, y_start:y_stop] == 0)

            # Apply the eccentricity
            mx[x_start:x_stop, y_start:y_stop][mask] = eccentricity

        return mx

    @staticmethod
    def get_custom_results(graph: nx.Graph, task):
        # Extract relevant information
        extra_data = GraphUtils.parse_extra_data(task)
        area_dimension = extra_data['area_dimension']
        radius = extra_data['radius']

        coverage_mx = Field.get_coverage_matrix(graph, area_dimension=area_dimension, radius=radius, overlap=True)
        detection_mx = Field.get_detection_matrix(graph, area_dimension=area_dimension, radius=radius)

        # Total number of units in the field
        total_units = area_dimension**2
        # Total number of covered units
        covered_units = np.count_nonzero(coverage_mx)
        # Total number of uncovered units
        uncovered_units = total_units - covered_units
        # Total number of units that overlap each other
        overlapping_units = len(coverage_mx[coverage_mx > 1])
        # Total number of units that overlap each other
        overlapping_units_accumulated = sum(coverage_mx[coverage_mx > 1] - 1)
        # The percentage coverage of the field
        coverage = covered_units / total_units
        # The average detection speed of the whole field
        average_detection_speed = detection_mx.sum() / covered_units

        custom_results = {
            'total_units': total_units,
            'covered_units': covered_units,
            'uncovered_units': uncovered_units,
            'overlapping_units': overlapping_units,
            'overlapping_units_accumulated': overlapping_units_accumulated,
            'coverage': coverage,
            'average_detection_speed': average_detection_speed
        }

        return custom_results
