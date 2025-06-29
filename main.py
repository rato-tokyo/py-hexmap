from generator import HexMap
from utils import fields_to_matrix

def create_map_matrix(map_id):
    """
    The main public function to generate a map matrix from a seed.
    This is the primary entry point for any external use of this library.
    It encapsulates the entire map generation process.
    """
    hex_map = HexMap(map_id)
    hex_map.GenerateMap()
    return fields_to_matrix(hex_map.Board.Fields)