import math
from .board import Point2D, get_field_key

class Pathfinder:
    """
    Handles pathfinding between two points on the map.
    This class is crucial for the `generate_ports` method, which needs to find
    paths between towns to determine where land meets water, a key step in
    creating realistic coastlines and harbors.
    """
    def __init__(self):
        """Initializes the Pathfinder."""
        pass

    def find_path(self, board, start_field, end_field, avoid_estate, avoid_water):
        """
        Implements the A* pathfinding algorithm to find the shortest path.
        It is retained because it's a core component of `generate_ports`, which
        significantly influences the final map layout by creating port towns.
        """
        if start_field is None or end_field is None:
            return None

        if start_field.type == "water":
            avoid_water = False

        tiles = []
        path = []
        tile_length = {}
        path_field_length = {}

        tiles.append(Tile())
        tiles[-1].field = start_field
        tiles[-1].total_cost = 0

        move_cost = [5, 5, 5, 5, 5, 5]

        while (len(path) == 0 or (len(path) > 0 and path[-1].field != end_field)) and len(tiles) > 0:
            current_tile = tiles[0]
            tiles = tiles[1:]
            for neighbor_num in range(6):
                neighbor = board.get_neighbor_field(current_tile.field, neighbor_num)
                if self.can_walk(current_tile.field, neighbor, avoid_estate, avoid_water) or (neighbor == end_field):
                    new_tile = Tile()
                    new_tile.field = neighbor
                    distance = self.get_distance(new_tile.field, end_field)
                    new_tile.parent = current_tile
                    new_tile.dist_cost = move_cost[neighbor_num] + distance
                    new_tile.total_cost = current_tile.total_cost + move_cost[neighbor_num]

                    key = self.get_field_str_key(new_tile.field)
                    if key not in path_field_length:
                        if key not in tile_length:
                            tile_length[key] = len(tiles)
                            tiles.append(new_tile)
                    elif path[path_field_length[key]].total_cost > new_tile.total_cost:
                        path[path_field_length[key]] = new_tile
            path_field_length[self.get_field_str_key(current_tile.field)] = len(path)
            path.append(current_tile)
            if len(tiles) > 0:
                tile_for_swap = 0
                for tile_num in range(1, len(tiles)):
                    if tiles[tile_num].dist_cost < tiles[tile_for_swap].dist_cost:
                        tile_for_swap = tile_num
                temp = tiles[0]
                tiles[0] = tiles[tile_for_swap]
                tiles[tile_for_swap] = temp

        if len(tiles) == 0:
            return None

        final_path = []
        path_index = len(path) - 1
        while len(final_path) == 0 or (len(final_path) > 0 and final_path[-1] != start_field):
            final_path.append(path[path_index].field)
            if path[path_index].parent is None:
                break
            path_index = path_field_length[self.get_field_str_key(path[path_index].parent.field)]
        self.reverse_array(final_path)
        return final_path

    def can_walk(self, a, b, avoid_estate, avoid_water):
        """
        Determines if movement is possible between two fields.
        This logic is a required helper for the `find_path` algorithm.
        """
        if a is None or b is None:
            return False
        for n in range(len(avoid_estate)):
            if b.estate == avoid_estate[n]:
                return False
        if not avoid_water:
            return True
        if a.type == "water" and b.type == "water":
            return True
        if a.type == "land" and b.type == "land":
            return True
        if a.type == "water" and b.type == "land":
            return True
        if b.type == "water" and a.estate == "port":
            return True
        return False

    def get_field_str_key(self, field):
        """
        A helper function to get the string key for a field.
        Required by `find_path` for dictionary lookups.
        """
        return get_field_key(field.f_x, field.f_y)

    def get_distance(self, a, b):
        """
        Calculates the heuristic distance between two fields for the A* algorithm.
        This is a necessary component of the `find_path` method.
        """
        acx = a.f_x * 5
        bcx = b.f_x * 5
        if a.f_x % 2 == 0:
            acy = a.f_y * 10
        else:
            acy = (a.f_y * 10) + 5
        if b.f_x % 2 == 0:
            bcy = b.f_y * 10
        else:
            bcy = (b.f_y * 10) + 5
        return math.sqrt(math.pow(float(acx - bcx), 2) + math.pow(float(acy - bcy), 2))

    def reverse_array(self, arr):
        """
        Reverses an array in place.
        This is required by `find_path` to return the path from start to end.
        """
        i, j = 0, len(arr) - 1
        while i < j:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
            j -= 1

class Tile:
    """
    A data structure representing a node in the pathfinding algorithm.
    It's essential for the `Pathfinder` class to store costs and parent pointers
    as it explores the map.
    """
    def __init__(self):
        """Initializes a Tile for pathfinding."""
        self.field = None
        self.parent = None
        self.dist_cost = 0.0
        self.total_cost = 0.0