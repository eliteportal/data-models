import re
import json
import pandas as pd
import plotly.graph_objects as go
import urllib
from dotenv import dotenv_values
from pathlib import Path
import os

import networkx as nx
from pyvis.network import Network


# import models
## how to handle sometimes list sometimes str
class data_model_json_ld:
    """Creates a networkgraph from JSON-LD files"""

    def __init__(self, name: str, url: str, directed: bool):
        self.name = name
        self.url = url
        self.directed = directed

    def get_data_model(self):
        """Get the data model as a JSON-LD format from the web"""
        with urllib.request.urlopen(self.url) as url:
            self.data_model = json.load(url)

    def write_out_model(self):
        with open(f"{self.name}.jsonld", "w") as outfile:
            outfile.write(json.dumps(self.data_model))

    def create_network_graph(self):
        """Creates network graph using networkx from a json-ld object

        Args:
            data_model (list): schematic formated json-ld
            name (str): data model name

        Returns:
            networkx.Graph: network graph object
        """
        pattern_replace = "rdf[s]|sms|bts|:"
        # create nodes
        nodes = []
        self.links = []
        valid_values = []  # to remove excess nodes

        # parse the model
        for l in self.data_model["@graph"]:
            try:
                node_temp = re.sub(pattern_replace, "", l["@id"])
            except Exception as e:
                print(l)
                raise (e)

            # add attributes for nodes
            attr_dict = {}
            edge_keys = [
                "rdfs:subClassOf",
                "schema:domainIncludes",
                "sms:requiresDependency",
            ]

            keys = l.keys()

            # attr_keys = [k for k in keys if k not in edge_keys]

            if "@type" in keys:
                if isinstance(l["@type"], list):
                    attr_dict["type"] = [
                        re.sub(pattern_replace, "", t) for t in l["@type"]
                    ]
                else:
                    attr_dict["type"] = re.sub(pattern_replace, "", l["@type"])

            if "sms:required" in keys:
                attr_dict["required"] = re.sub(pattern_replace, "", l["sms:required"])

            # valid values
            if "schema:rangeIncludes" in keys:
                if isinstance(l["schema:rangeIncludes"], list):
                    attr_dict["validValues"] = [
                        re.sub(pattern_replace, "", x["@id"])
                        for x in l["schema:rangeIncludes"]
                    ]

                    valid_values += attr_dict["validValues"]
                elif isinstance(l["schema:rangeIncludes"], dict):
                    attr_dict["validValues"] = [
                        re.sub(pattern_replace, "", v)
                        for k, v in l["schema:rangeIncludes"].items()
                    ]
                else:
                    attr_dict["validValues"] = l["schema:rangeIncludes"]

            # create edges ---------------------------------------------------------------------------------------------
            if "rdfs:subClassOf" in keys:  # get parent relationships
                if isinstance(l["rdfs:subClassOf"], list):
                    for s in l["rdfs:subClassOf"]:
                        self.links.append(
                            (
                                re.sub(pattern_replace, "", s["@id"]),
                                node_temp,
                                {"relationship": "subClass"},
                            )
                        )
                else:
                    self.links.append(
                        (
                            re.sub(pattern_replace, "", l["rdfs:subClassOf"]["@id"]),
                            node_temp,
                            {"relationship": "subClass"},
                        )
                    )

            if "schema:domainIncludes" in keys:  # get child relationships
                if isinstance(l["schema:domainIncludes"], list):
                    for d in l["schema:domainIncludes"]:
                        self.links.append(
                            (
                                node_temp,
                                re.sub(pattern_replace, "", d["@id"]),
                                {"relationship": "validValue"},
                            )
                        )

            if "sms:requiresDependency" in keys:  # parent relationships
                if isinstance(l["sms:requiresDependency"], list):
                    for r in l["sms:requiresDependency"]:
                        self.links.append(
                            (
                                node_temp,
                                re.sub(pattern_replace, "", r["@id"]),
                                {"relationship": "Dependency"},
                            )
                        )
            # add new node
            nodes.append((node_temp, attr_dict))
        # Create the graph

        self.graph = nx.MultiDiGraph()

        self.graph.name = self.name

        self.graph.add_nodes_from(nodes)

        # get unique edges
        # self.links = list(set(self.links))

        self.graph.add_edges_from(self.links)

        # add template property for filtering
        self.graph.nodes["Component"]["role"] = "Template"
        for n in list(nx.all_neighbors(self.graph, "Component")):
            self.graph.nodes[n]["role"] = "Template"

        reverse_components = [l for l in list(self.graph.edges) if l[1] == "Component"]

        new_component_edges = [(l[1], l[0]) for l in reverse_components]

        self.graph.remove_edges_from(reverse_components)

        self.graph.add_edges_from(new_component_edges)

        # trim graph. Remove any nodes without edges
        node_removals = [
            n
            for n in self.graph.nodes
            if len(list(nx.all_neighbors(self.graph, n))) == 0
        ]

        node_removals += valid_values

        self.graph.remove_nodes_from(node_removals)

        # remove duplicate edges
        edge_removals = []
        for e in self.graph.edges:
            # print(e)
            if e[2] > 0:
                edge_removals.append(e)
        self.graph.remove_edges_from(edge_removals)

        print(self.graph)

    def create_graph_viz(self, output_path=None):
        """Creates an HTML file of the graph to be viewed in a browser

        Args:
            output_path (string): path to write the file out to
        """
        # Can be visualized in the browser
        nt = Network(
            height="800px",
            directed=True,
            notebook=True,
            cdn_resources="remote",
            select_menu=True,
            filter_menu=True,
            neighborhood_highlight=True,
        )
        nt.toggle_physics(True)
        nt.show_buttons(filter_=["physics"])
        # populates the nodes and edges data structures
        nt.from_nx(self.graph)

        nt.repulsion(central_gravity=0.035)

        if output_path is None:
            output_path = (
                "../_includes/" + self.name + "_network_graph.html"
            )  # needs to be in the includes dir

        nt.save_graph(output_path)  # open html in browser
        print(f"Graph created at {output_path}")

    def print_data_model(self):
        print(json.dumps(self.data_model, indent=2))

    def get_node_attrs(self, node):
        """Return the attributes of the node to look for

        Args:
            node (str): label of node

        Returns:
            dict: attributes of node
        """
        return dict(self.graph.nodes(data=True))[node]

    def full_workflow(self):
        self.get_data_model()
        # self.write_out_model()
        self.create_network_graph()
        self.create_graph_viz()


if __name__ == "__main__":
    # network_graph
    cwd = Path(__file__).parent

    os.chdir(cwd)

    config = dotenv_values(".env")
    el_jsonld_url = config["json_model"]
    project_name = "EL"

    network_graph = data_model_json_ld(
        name=project_name, url=el_jsonld_url, directed=True
    )

    # create data models
    try:
        network_graph.full_workflow()
        print("Successfully created network graph")

    except Exception as e:
        print(f"Could not create graph for {project_name}")
        print(e)
        print("-" * 20)
