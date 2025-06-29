from .generator import HexMap
from .utils import fields_to_matrix

# A list of sample map IDs used for testing purposes.
# This ensures that the map generation logic is tested against a variety of seeds.
map_sample_list=[0,10,1000,123456,9999,99999,999999]

def create_map_matrix(map_id):
    """
    The main public function to generate a map matrix from a seed.
    This is the primary entry point for any external use of this library.
    It encapsulates the entire map generation process.
    """
    hex_map = HexMap(map_id)
    hex_map.generate_map()
    return fields_to_matrix(hex_map.board.fields)