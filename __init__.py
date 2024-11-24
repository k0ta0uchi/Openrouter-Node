from .openrouter_node import OpenrouterNode, OpenrouterNodeImage  # Adjust the import based on your actual file name and class

# Define the node mappings
NODE_CLASS_MAPPINGS = {
    "OpenrouterNode": OpenrouterNode,  # Unique key name with the node class
    "OpenrouterNodeImage": OpenrouterNodeImage
}

# Optional: Define display names for nodes if you want to customize how they appear in the UI
NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenrouterNode": "OpenRouter Node",  # Display name in the UI
    "OpenrouterNodeImage": "OpenRouter Node with Image"  # Display name in the UI
}