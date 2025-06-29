def get_field_key(x, y):
    """
    Generates a unique string key for a map field based on its coordinates.
    This is essential for storing and retrieving fields from a dictionary,
    which is the primary data structure for the map board.
    """
    return "f" + str(x) + "x" + str(y)

def validate_location(x, y, board):
    """
    Checks if a given (x, y) coordinate exists on the board.
    It's kept to safely handle neighbor-finding logic at the edges of the map,
    preventing errors from requests for out-of-bounds fields.
    """
    if get_field_key(x, y) in board.fields:
        return Point2D(x, y)
    else:
        return None

class Board:
    """
    A data structure that holds the state of the entire map, including all fields,
    land groups, and towns. It is essential as it acts as the central container
    for all map-related data during generation.
    """
    def __init__(self):
        """Initializes the board with default dimensions and empty data structures."""
        self.map_number = 0
        self.x_max = 20
        self.y_max = 11
        self.hex_width = 50
        self.hex_height = 40
        self.fields = {}
        self.land_count = 0
        self.land_groups = []
        self.towns = []
        self.parties_capitals = [None] * 4
        self.town_names = []

    def get_neighbor_field(self, field, neighbor_index):
        """
        Retrieves a specific neighbor of a field.
        This is a required helper for any algorithm that needs to traverse the map graph.
        """
        neighbor_location = field.neighbors[neighbor_index]
        if neighbor_location is None:
            return None
        key = get_field_key(neighbor_location.x, neighbor_location.y)
        return self.fields.get(key)

class Field:
    """
    A data structure for a single hexagonal tile on the map.
    It holds all properties of a tile, such as its type (land/water),
    coordinates, and any structures on it (town, port). It is the fundamental
    building block of the map.
    """
    def __init__(self):
        """Initializes a field with default values."""
        self.f_x = 0
        self.f_y = 0
        self.x = 0
        self.y = 0
        self.land_id = 0
        self.type = ""
        self.capital = 0
        self.neighbors = [None] * 6
        self.is_land = False
        self.estate = ""
        self.town_name = ""

class Point2D:
    """
    A simple data structure to hold 2D coordinates.
    It is used by `validate_location` and is a necessary component for
    representing locations on the map grid.
    """
    def __init__(self, x, y):
        """Initializes a point with X and Y coordinates."""
        self.x = x
        self.y = y