from schematic.schemas.data_model_parser import DataModelParser
from schematic.schemas.data_model_graph import DataModelGraph
from schematic.schemas.data_model_graph import DataModelGraphExplorer

# Instantiate DataModelParser
data_model_parser = DataModelParser(
    path_to_data_model=path / to / csv_or_jsonld_data_model
)

# Parse Model
parsed_data_model = data_model_parser.parse_model()

# Instantiate DataModelGraph
data_model_grapher = DataModelGraph(parsed_data_model)

# Generate graph
graph_data_model = data_model_grapher.generate_data_model_graph()

# Instantiate DataModelGraphExplorer
DMGE = DataModelGraphExplorer(graph_data_model)

# Get components in the data model (defined by the DependsOn Component Column)
component_digraph = DMGE.get_digraph_by_edge_type("requiresComponent")
components = component_digraph.nodes()

# Remove Components we dont want to show up in the drop down menu
components_to_remove = ["Patient", "File", "Publication"]
components = sorted(list(set(components) - set(components_to_remove)))

# Get component display names **note no longer need to provide the mm_graph as an argument since it is available already to DMGE
display_names = DMGE.get_nodes_display_names(node_list=components)

# Record information about each component
for index, component in enumerate(components):
    deps = DMGE.get_node_dependencies(source_node=component)
    schema_type = "file" if "Filename" in deps else "record"
    schemas.append(
        {
            "display_name": display_names[index],
            "schema_name": component,
            "type": schema_type,
        }
    )
