def getFieldKey(x, y):
    """
    Generates a unique string key for a map field based on its coordinates.
    This is essential for storing and retrieving fields from a dictionary,
    which is the primary data structure for the map board.
    """
    return "f" + str(x) + "x" + str(y)

def validateLocation(x, y, board):
    """
    Checks if a given (x, y) coordinate exists on the board.
    It's kept to safely handle neighbor-finding logic at the edges of the map,
    preventing errors from requests for out-of-bounds fields.
    """
    if getFieldKey(x, y) in board.Fields:
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
        self.MapNumber = 0
        self.XMax = 20
        self.YMax = 11
        self.HexWidth = 50
        self.HexHeight = 40
        self.Fields = {}
        self.LandCount = 0
        self.LandGroups = []
        self.Towns = []
        self.PartiesCapitals = [None] * 4
        self.TownNames = []

    def getNeighborField(self, field, neighborIndex):
        """
        Retrieves a specific neighbor of a field.
        This is a required helper for any algorithm that needs to traverse the map graph.
        """
        neighborLocation = field.Neighbors[neighborIndex]
        if neighborLocation is None:
            return None
        key = getFieldKey(neighborLocation.X, neighborLocation.Y)
        return self.Fields.get(key)

class Field:
    """
    A data structure for a single hexagonal tile on the map.
    It holds all properties of a tile, such as its type (land/water),
    coordinates, and any structures on it (town, port). It is the fundamental
    building block of the map.
    """
    def __init__(self):
        """Initializes a field with default values."""
        self.FX = 0
        self.FY = 0
        self.X = 0
        self.Y = 0
        self.LandId = 0
        self.Type = ""
        self.Capital = 0
        self.Neighbors = [None] * 6
        self.IsLand = False
        self.Estate = ""
        self.TownName = ""

class Point2D:
    """
    A simple data structure to hold 2D coordinates.
    It is used by `validateLocation` and is a necessary component for
    representing locations on the map grid.
    """
    def __init__(self, X, Y):
        """Initializes a point with X and Y coordinates."""
        self.X = X
        self.Y = Y
