import math
from board import Board, Field, Point2D, getFieldKey, validateLocation
from pathfinding import Pathfinder
from towns import generateAllTowns

class HexMap:
    """
    The main class that orchestrates the entire map generation process.
    It holds the board, the seeded random number generator, and calls all
    the necessary methods to build the map from scratch. It must be kept
    as it is the core of the project.
    """
    def __init__(self, mapNumber):
        """
        Initializes the HexMap with a specific seed (mapNumber).
        This setup is crucial for generating a deterministic, reproducible map.
        """
        self.RandomSeed = mapNumber
        self.Board = Board()
        self.Board.MapNumber = mapNumber
        self.Board.TownNames = generateAllTowns()
        self.Pathfinder = Pathfinder()

    def rand(self, n):
        """
        A seeded pseudo-random number generator.
        This is the most critical function for ensuring that map generation is
        deterministic. Every "random" decision in the map generation process
        uses this function, so for the same seed, the map is always identical.
        """
        self.RandomSeed = (self.RandomSeed * 9301 + 49297) % 233280
        return int(math.floor((self.RandomSeed / 233280) * n))

    def getField(self, x, y, board):
        """
        Retrieves a field from the board's dictionary.
        A necessary helper for many map generation methods.
        """
        key = getFieldKey(x, y)
        return board.Fields.get(key)

    def addField(self, x, y, board):
        """
        Creates a new field and adds it to the board.
        This is a fundamental step in the `generateBoard` process.
        """
        key = getFieldKey(x, y)
        board.Fields[key] = Field()
        field = board.Fields[key]
        field.FX = x
        field.FY = y
        field.X = x * (((board.HexWidth // 4) * 3)) + (board.HexWidth // 2)
        if x % 2 == 0:
            field.Y = y * board.HexHeight + (board.HexHeight // 2)
        else:
            field.Y = y * board.HexHeight + board.HexHeight
        field.LandId = -1
        if (x == 1 and y == 1) or (x == board.XMax - 2 and y == 1) or (x == board.XMax - 2 and y == board.YMax - 2) or (x == 1 and y == board.YMax - 2):
            field.Type = "land"
        else:
            if self.rand(10) <= 1:
                field.Type = "land"
            else:
                field.Type = "water"
        field.Capital = -1
        field.Estate = ""
        field.TownName = ""

    def findNeighbors(self, field, board):
        """
        Calculates and stores the neighbors for a given field.
        This is essential for almost all map algorithms, including land generation
        and pathfinding, as it defines the connectivity of the map.
        """
        field.Neighbors = [None] * 6
        fx = field.FX
        fy = field.FY
        if fx % 2 == 0:
            field.Neighbors[0] = validateLocation(fx + 1, fy, board)
            field.Neighbors[1] = validateLocation(fx, fy + 1, board)
            field.Neighbors[2] = validateLocation(fx - 1, fy, board)
            field.Neighbors[3] = validateLocation(fx - 1, fy - 1, board)
            field.Neighbors[4] = validateLocation(fx, fy - 1, board)
            field.Neighbors[5] = validateLocation(fx + 1, fy - 1, board)
        else:
            field.Neighbors[0] = validateLocation(fx + 1, fy + 1, board)
            field.Neighbors[1] = validateLocation(fx, fy + 1, board)
            field.Neighbors[2] = validateLocation(fx - 1, fy + 1, board)
            field.Neighbors[3] = validateLocation(fx - 1, fy, board)
            field.Neighbors[4] = validateLocation(fx, fy - 1, board)
            field.Neighbors[5] = validateLocation(fx + 1, fy, board)

    def setLandFields(self, board):
        """
        Expands initial land seeds into larger, more organic landmasses.
        This function is a core part of the map generation process, turning
        a sparse set of land tiles into continents and islands.
        """
        for x in range(self.Board.XMax):
            for y in range(self.Board.YMax):
                field = self.getField(x, y, board)
                if field.Type == "water":
                    landFields = 0
                    for n in range(6):
                        neighbor = board.getNeighborField(field, n)
                        if neighbor is None:
                            continue
                        if neighbor.Type == "land":
                            landFields += 1
                    if landFields >= 1:
                        self.getField(x, y, board).IsLand = True

        for x in range(self.Board.XMax):
            for y in range(self.Board.YMax):
                if self.getField(x, y, board).IsLand:
                    self.getField(x, y, board).Type = "land"

        for x in range(self.Board.XMax):
            for y in range(self.Board.YMax):
                field = self.getField(x, y, board)
                if field.Type == "water":
                    waterFields = 0
                    for n in range(6):
                        neighbor = board.getNeighborField(field, n)
                        if neighbor is None:
                            continue
                        if neighbor.Type == "water":
                            waterFields += 1
                    if waterFields == 0:
                        self.getField(x, y, board).Type = "land"

    def addNeighborsToLandGroup(self, field, board, landId):
        """
        A helper function for `generateLandGroups` to recursively find all
        connected land tiles belonging to a single landmass.
        """
        newFields = 0
        for n in range(6):
            neighbor = board.getNeighborField(field, n)
            if neighbor is not None and neighbor.Type == "land" and neighbor.LandId < 0:
                board.LandGroups[landId].append(neighbor)
                neighbor.LandId = landId
                newFields += 1
        return newFields

    def generateLandGroups(self, board):
        """
        Identifies and groups connected land tiles into distinct landmasses (islands).
        This is a prerequisite for town generation, which places towns
        based on the size of these land groups.
        """
        for x in range(board.XMax):
            for y in range(board.YMax):
                if self.getField(x, y, board).Type == "land":
                    board.LandCount = board.LandCount + 1

        for x in range(board.XMax):
            for y in range(board.YMax):
                if self.getField(x, y, board).Type == "land" and self.getField(x, y, board).LandId < 0:
                    countLandId = len(board.LandGroups)
                    board.LandGroups.append([])
                    board.LandGroups[countLandId].append(self.getField(x, y, board))
                    self.getField(x, y, board).LandId = countLandId
                    groupSize = 0
                    fieldCount = groupSize
                    while groupSize >= fieldCount:
                        groupSize = groupSize + self.addNeighborsToLandGroup(board.LandGroups[countLandId][fieldCount], board, countLandId)
                        fieldCount += 1

    def generatePartyCapitals(self, board):
        """
        Places the four starting capitals on the map.
        This is a required step that ensures the four corners of the map
        are initialized correctly as starting points.
        """
        capital = 0
        for x in range(board.XMax):
            for y in range(board.YMax):
                if (x == 1 and y == 1) or (x == board.XMax - 2 and y == 1) or (x == board.XMax - 2 and y == board.YMax - 2) or (x == 1 and y == board.YMax - 2):
                    self.getField(x, y, board).Estate = "town"
                    board.Towns.append(self.getField(x, y, board))
                    self.getField(x, y, board).Capital = capital
                    board.PartiesCapitals[capital] = self.getField(x, y, board)
                    capital += 1

    def generateTowns(self, board):
        """
        Populates landmasses with towns. The number of towns is based on the
        size of the landmass. This process consumes numbers from the seeded RNG,
        making it a crucial step for deterministic map generation. Removing it
        would alter the RNG sequence and change the entire map layout,
        causing tests to fail.
        """
        for landNum in range(len(board.LandGroups)):
            townCount = int(math.floor((len(board.LandGroups[landNum]) / 10) + 1))
            for townNum in range(townCount):
                created = False
                attempts = 0
                while not created:
                    attempts += 1
                    if attempts > 10:
                        created = True
                    townIndex = self.rand(len(board.LandGroups[landNum]))
                    if board.LandGroups[landNum][townIndex].Estate == "":
                        ok = True
                        for n in range(6):
                            field = board.LandGroups[landNum][townIndex]
                            neighbor = board.getNeighborField(field, n)
                            if neighbor is None:
                                continue
                            if neighbor.Type == "water" or neighbor.Estate != "":
                                ok = False
                        if ok:
                            board.LandGroups[landNum][townIndex].Estate = "town"
                            board.Towns.append(board.LandGroups[landNum][townIndex])
                            created = True

    def shuffle(self, arr):
        """
        Shuffles an array using the seeded RNG.
        This is used on the list of towns and is essential for ensuring the
        randomness is deterministic and reproducible.
        """
        for index in range(len(arr)):
            tmp = arr[index]
            randIndex = self.rand(len(arr))
            arr[index] = arr[randIndex]
            arr[randIndex] = tmp

    def generatePorts(self, board):
        """
        Creates ports where land and water meet.
        This method relies on the `Pathfinder` to find paths between towns.
        It's a key part of making the map feel realistic and is necessary
        for the final map structure.
        """
        portNum = 0
        pathNum = 0
        for town in range(len(board.Towns) - 1):
            path = self.Pathfinder.findPath(board, board.Towns[town], board.Towns[town+1], ["town"], True)
            if path is None or len(path) > portNum:
                path = self.Pathfinder.findPath(board, board.Towns[town], board.Towns[town+1], ["town"], False)
                pathNum += 1
            if path is None: continue
            for pathIndex in range(1, len(path) - 1):
                if path[pathIndex].Type == "land" and path[pathIndex+1].Type == "water":
                    path[pathIndex].Estate = "port"
                    portNum += 1
                if path[pathIndex].Type == "land" and path[pathIndex-1].Type == "water":
                    path[pathIndex].Estate = "port"
                    portNum += 1

    def generateBoard(self, board):
        """
        Executes all the map generation steps in the correct order.
        This is the main orchestrator and must be kept. It ensures that
        each layer of the map is built upon the previous one correctly.
        """
        for x in range(6):
            for y in range(4):
                self.rand(6)
                self.rand(6)
                self.rand(2)
                self.rand(2)
                self.rand(4)

        for x in range(board.XMax):
            for y in range(board.YMax):
                self.addField(x, y, board)

        for x in range(board.XMax):
            for y in range(board.YMax):
                field = self.getField(x, y, board)
                self.findNeighbors(field, board)

        self.setLandFields(board)
        self.generateLandGroups(board)
        self.generatePartyCapitals(board)
        self.generateTowns(board)
        self.shuffle(board.Towns)
        self.generatePorts(board)

    def GenerateMap(self):
        """
        A simple wrapper that kicks off the map generation process.
        It is the public entry point for generating the map on a HexMap instance.
        """
        self.generateBoard(self.Board)
