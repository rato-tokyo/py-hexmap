from .generator import HexMap
from .utils import fields_to_dict_representation

# A list of sample map IDs used for testing purposes.
# This ensures that the map generation logic is tested against a variety of seeds.
# This list is primarily for internal testing and not part of the public API.
map_sample_list=[0,10,1000,123456,9999,99999,999999]

def generate_map_data(map_id: int, x_max: int = 20, y_max: int = 11) -> dict:
    """
    Generates map data as a dictionary for a given seed and dimensions.

    This is the primary public function for generating map data.
    It encapsulates the entire map generation process and returns a dictionary
    representation of the map, suitable for serialization (e.g., to JSON).

    Args:
        map_id (int): The seed for the random number generator.
        x_max (int): The maximum X-coordinate for the map (width). Defaults to 20.
        y_max (int): The maximum Y-coordinate for the map (height). Defaults to 11.

    Returns:
        dict: A dictionary where keys are field identifiers (e.g., "f0x0") and
              values are dictionaries representing the properties of each field.
    """
    hex_map = HexMap(map_id, x_max, y_max)
    hex_map.generate_map()
    return fields_to_dict_representation(hex_map.board.fields, x_max, y_max)
