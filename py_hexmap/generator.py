import math
from .board import Board, Field, Point2D, get_field_key, validate_location
from .pathfinding import Pathfinder
from .towns import generate_all_towns

class HexMap:
    """
    The main class that orchestrates the entire map generation process.
    It holds the board, the seeded random number generator, and calls all
    the necessary methods to build the map from scratch. It must be kept
    as it is the core of the project.
    """
    def __init__(self, map_number):
        """
        Initializes the HexMap with a specific seed (map_number).
        This setup is crucial for generating a deterministic, reproducible map.
        """
        self.random_seed = map_number
        self.board = Board()
        self.board.map_number = map_number
        self.board.town_names = generate_all_towns()
        self.pathfinder = Pathfinder()

    def _rand(self, n):
        """
        A seeded pseudo-random number generator.
        This is the most critical function for ensuring that map generation is
        deterministic. Every "random" decision in the map generation process
        uses this function, so for the same seed, the map is always identical.
        """
        self.random_seed = (self.random_seed * 9301 + 49297) % 233280
        return int(math.floor((self.random_seed / 233280) * n))

    def get_field(self, x, y, board):
        """
        Retrieves a field from the board's dictionary.
        A necessary helper for many map generation methods.
        """
        key = get_field_key(x, y)
        return board.fields.get(key)

    def add_field(self, x, y, board):
        """
        Creates a new field and adds it to the board.
        This is a fundamental step in the `generate_board` process.
        """
        key = get_field_key(x, y)
        board.fields[key] = Field()
        field = board.fields[key]
        field.f_x = x
        field.f_y = y
        field.x = x * (((board.hex_width // 4) * 3)) + (board.hex_width // 2)
        if x % 2 == 0:
            field.y = y * board.hex_height + (board.hex_height // 2)
        else:
            field.y = y * board.hex_height + board.hex_height
        field.land_id = -1
        if (x == 1 and y == 1) or (x == board.x_max - 2 and y == 1) or (x == board.x_max - 2 and y == board.y_max - 2) or (x == 1 and y == board.y_max - 2):
            field.type = "land"
        else:
            if self._rand(10) <= 1:
                field.type = "land"
            else:
                field.type = "water"
        field.capital = -1
        field.estate = ""
        field.town_name = ""

    def find_neighbors(self, field, board):
        """
        Calculates and stores the neighbors for a given field.
        This is essential for almost all map algorithms, including land generation
        and pathfinding, as it defines the connectivity of the map.
        """
        field.neighbors = [None] * 6
        f_x = field.f_x
        f_y = field.f_y
        if f_x % 2 == 0:
            field.neighbors[0] = validate_location(f_x + 1, f_y, board)
            field.neighbors[1] = validate_location(f_x, f_y + 1, board)
            field.neighbors[2] = validate_location(f_x - 1, f_y, board)
            field.neighbors[3] = validate_location(f_x - 1, f_y - 1, board)
            field.neighbors[4] = validate_location(f_x, f_y - 1, board)
            field.neighbors[5] = validate_location(f_x + 1, f_y - 1, board)
        else:
            field.neighbors[0] = validate_location(f_x + 1, f_y + 1, board)
            field.neighbors[1] = validate_location(f_x, f_y + 1, board)
            field.neighbors[2] = validate_location(f_x - 1, f_y + 1, board)
            field.neighbors[3] = validate_location(f_x - 1, f_y, board)
            field.neighbors[4] = validate_location(f_x, f_y - 1, board)
            field.neighbors[5] = validate_location(f_x + 1, f_y, board)

    def set_land_fields(self, board):
        """
        Expands initial land seeds into larger, more organic landmasses.
        This function is a core part of the map generation process, turning
        a sparse set of land tiles into continents and islands.
        """
        for x in range(self.board.x_max):
            for y in range(self.board.y_max):
                field = self.get_field(x, y, board)
                if field.type == "water":
                    land_fields = 0
                    for n in range(6):
                        neighbor = board.get_neighbor_field(field, n)
                        if neighbor is None:
                            continue
                        if neighbor.type == "land":
                            land_fields += 1
                    if land_fields >= 1:
                        self.get_field(x, y, board).is_land = True

        for x in range(self.board.x_max):
            for y in range(self.board.y_max):
                if self.get_field(x, y, board).is_land:
                    self.get_field(x, y, board).type = "land"

        for x in range(self.board.x_max):
            for y in range(self.board.y_max):
                field = self.get_field(x, y, board)
                if field.type == "water":
                    water_fields = 0
                    for n in range(6):
                        neighbor = board.get_neighbor_field(field, n)
                        if neighbor is None:
                            continue
                        if neighbor.type == "water":
                            water_fields += 1
                    if water_fields == 0:
                        self.get_field(x, y, board).type = "land"

    def add_neighbors_to_land_group(self, field, board, land_id):
        """
        A helper function for `generate_land_groups` to recursively find all
        connected land tiles belonging to a single landmass.
        """
        new_fields = 0
        for n in range(6):
            neighbor = board.get_neighbor_field(field, n)
            if neighbor is not None and neighbor.type == "land" and neighbor.land_id < 0:
                board.land_groups[land_id].append(neighbor)
                neighbor.land_id = land_id
                new_fields += 1
        return new_fields

    def generate_land_groups(self, board):
        """
        Identifies and groups connected land tiles into distinct landmasses (islands).
        This is a prerequisite for town generation, which places towns
        based on the size of these land groups.
        """
        for x in range(board.x_max):
            for y in range(board.y_max):
                if self.get_field(x, y, board).type == "land":
                    board.land_count = board.land_count + 1

        for x in range(board.x_max):
            for y in range(board.y_max):
                if self.get_field(x, y, board).type == "land" and self.get_field(x, y, board).land_id < 0:
                    count_land_id = len(board.land_groups)
                    board.land_groups.append([])
                    board.land_groups[count_land_id].append(self.get_field(x, y, board))
                    self.get_field(x, y, board).land_id = count_land_id
                    group_size = 0
                    field_count = group_size
                    while group_size >= field_count:
                        group_size = group_size + self.add_neighbors_to_land_group(board.land_groups[count_land_id][field_count], board, count_land_id)
                        field_count += 1

    def generate_party_capitals(self, board):
        """
        Places the four starting capitals on the map.
        This is a required step that ensures the four corners of the map
        are initialized correctly as starting points.
        """
        capital = 0
        for x in range(board.x_max):
            for y in range(board.y_max):
                if (x == 1 and y == 1) or (x == board.x_max - 2 and y == 1) or (x == board.x_max - 2 and y == board.y_max - 2) or (x == 1 and y == board.y_max - 2):
                    self.get_field(x, y, board).estate = "town"
                    self.get_field(x, y, board).town_name = self.rand_town()
                    board.towns.append(self.get_field(x, y, board))
                    self.get_field(x, y, board).capital = capital
                    board.parties_capitals[capital] = self.get_field(x, y, board)
                    capital += 1

    def generate_towns(self, board):
        """
        Populates landmasses with towns. The number of towns is based on the
        size of the landmass. This process consumes numbers from the seeded RNG,
        making it a crucial step for deterministic map generation. Removing it
        would alter the RNG sequence and change the entire map layout,
        causing tests to fail.
        """
        for land_num in range(len(board.land_groups)):
            town_count = int(math.floor((len(board.land_groups[land_num]) / 10) + 1))
            for town_num in range(town_count):
                created = False
                attempts = 0
                while not created:
                    attempts += 1
                    if attempts > 10:
                        created = True
                    town_index = self._rand(len(board.land_groups[land_num]))
                    if board.land_groups[land_num][town_index].estate == "":
                        ok = True
                        for n in range(6):
                            field = board.land_groups[land_num][town_index]
                            neighbor = board.get_neighbor_field(field, n)
                            if neighbor is None:
                                continue
                            if neighbor.type == "water" or neighbor.estate != "":
                                ok = False
                        if ok:
                            board.land_groups[land_num][town_index].estate = "town"
                            board.land_groups[land_num][town_index].town_name = self.rand_town()
                            board.towns.append(board.land_groups[land_num][town_index])
                            created = True

    def shuffle(self, arr):
        """
        Shuffles an array using the seeded RNG.
        This is used on the list of towns and is essential for ensuring the
        randomness is deterministic and reproducible.
        """
        for index in range(len(arr)):
            tmp = arr[index]
            rand_index = self._rand(len(arr))
            arr[index] = arr[rand_index]
            arr[rand_index] = tmp

    def generate_ports(self, board):
        """
        Creates ports where land and water meet.
        This method relies on the `Pathfinder` to find paths between towns.
        It's a key part of making the map feel realistic and is necessary
        for the final map structure.
        """
        port_num = 0
        path_num = 0
        for town in range(len(board.towns) - 1):
            path = self.pathfinder.find_path(board, board.towns[town], board.towns[town+1], ["town"], True)
            if path is None or len(path) > port_num:
                path = self.pathfinder.find_path(board, board.towns[town], board.towns[town+1], ["town"], False)
                path_num += 1
            if path is None: continue
            for path_index in range(1, len(path) - 1):
                if path[path_index].type == "land" and path[path_index+1].type == "water":
                    path[path_index].estate = "port"
                    port_num += 1
                if path[path_index].type == "land" and path[path_index-1].type == "water":
                    path[path_index].estate = "port"
                    port_num += 1

    def rand_town(self):
        """
        Selects a random town name from the list and removes it to prevent duplicates.
        """
        town_names = self.board.town_names
        rand_index = self._rand(len(town_names))
        town_name = town_names[rand_index]
        town_names[rand_index] = town_names[0]
        town_names[0] = town_name
        self.board.town_names = town_names[1:]
        return town_name

    def generate_board(self, board):
        """
        Executes all the map generation steps in the correct order.
        This is the main orchestrator and must be kept. It ensures that
        each layer of the map is built upon the previous one correctly.
        """
        for x in range(6):
            for y in range(4):
                self._rand(6)
                self._rand(6)
                self._rand(2)
                self._rand(2)
                self._rand(4)

        for x in range(board.x_max):
            for y in range(board.y_max):
                self.add_field(x, y, board)

        for x in range(board.x_max):
            for y in range(board.y_max):
                field = self.get_field(x, y, board)
                self.find_neighbors(field, board)

        self.set_land_fields(board)
        self.generate_land_groups(board)
        self.generate_party_capitals(board)
        self.generate_towns(board)
        self.shuffle(board.towns)
        self.generate_ports(board)

    def generate_map(self):
        """
        A simple wrapper that kicks off the map generation process.
        It is the public entry point for generating the map on a HexMap instance.
        """
        self.generate_board(self.board)