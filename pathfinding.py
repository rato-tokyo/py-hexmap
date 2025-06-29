import math
from board import Point2D, getFieldKey

class Pathfinder:
    """
    Handles pathfinding between two points on the map.
    This class is crucial for the `generatePorts` method, which needs to find
    paths between towns to determine where land meets water, a key step in
    creating realistic coastlines and harbors.
    """
    def __init__(self):
        """Initializes the Pathfinder."""
        pass

    def findPath(self, board, startField, endField, avoidEstate, avoidWater):
        """
        Implements the A* pathfinding algorithm to find the shortest path.
        It is retained because it's a core component of `generatePorts`, which
        significantly influences the final map layout by creating port towns.
        """
        if startField is None or endField is None:
            return None

        if startField.Type == "water":
            avoidWater = False

        tiles = []
        path = []
        tileLength = {}
        pathFieldLength = {}

        tiles.append(Tile())
        tiles[-1].Field = startField
        tiles[-1].TotalCost = 0

        moveCost = [5, 5, 5, 5, 5, 5]

        while (len(path) == 0 or (len(path) > 0 and path[-1].Field != endField)) and len(tiles) > 0:
            currentTile = tiles[0]
            tiles = tiles[1:]
            for neighborNum in range(6):
                neighbor = board.getNeighborField(currentTile.Field, neighborNum)
                if self.canWalk(currentTile.Field, neighbor, avoidEstate, avoidWater) or (neighbor == endField):
                    newTile = Tile()
                    newTile.Field = neighbor
                    distance = self.getDistance(newTile.Field, endField)
                    newTile.Parent = currentTile
                    newTile.DistCost = moveCost[neighborNum] + distance
                    newTile.TotalCost = currentTile.TotalCost + moveCost[neighborNum]

                    key = self.getFieldStrKey(newTile.Field)
                    if key not in pathFieldLength:
                        if key not in tileLength:
                            tileLength[key] = len(tiles)
                            tiles.append(newTile)
                    elif path[pathFieldLength[key]].TotalCost > newTile.TotalCost:
                        path[pathFieldLength[key]] = newTile
            pathFieldLength[self.getFieldStrKey(currentTile.Field)] = len(path)
            path.append(currentTile)
            if len(tiles) > 0:
                tileForSwap = 0
                for tileNum in range(1, len(tiles)):
                    if tiles[tileNum].DistCost < tiles[tileForSwap].DistCost:
                        tileForSwap = tileNum
                temp = tiles[0]
                tiles[0] = tiles[tileForSwap]
                tiles[tileForSwap] = temp

        if len(tiles) == 0:
            return None

        finalPath = []
        pathIndex = len(path) - 1
        while len(finalPath) == 0 or (len(finalPath) > 0 and finalPath[-1] != startField):
            finalPath.append(path[pathIndex].Field)
            if path[pathIndex].Parent is None:
                break
            pathIndex = pathFieldLength[self.getFieldStrKey(path[pathIndex].Parent.Field)]
        self.reverseArray(finalPath)
        return finalPath

    def canWalk(self, a, b, avoidEstate, avoidWater):
        """
        Determines if movement is possible between two fields.
        This logic is a required helper for the `findPath` algorithm.
        """
        if a is None or b is None:
            return False
        for n in range(len(avoidEstate)):
            if b.Estate == avoidEstate[n]:
                return False
        if not avoidWater:
            return True
        if a.Type == "water" and b.Type == "water":
            return True
        if a.Type == "land" and b.Type == "land":
            return True
        if a.Type == "water" and b.Type == "land":
            return True
        if b.Type == "water" and a.Estate == "port":
            return True
        return False

    def getFieldStrKey(self, field):
        """
        A helper function to get the string key for a field.
        Required by `findPath` for dictionary lookups.
        """
        return getFieldKey(field.FX, field.FY)

    def getDistance(self, a, b):
        """
        Calculates the heuristic distance between two fields for the A* algorithm.
        This is a necessary component of the `findPath` method.
        """
        acx = a.FX * 5
        bcx = b.FX * 5
        if a.FX % 2 == 0:
            acy = a.FY * 10
        else:
            acy = (a.FY * 10) + 5
        if b.FX % 2 == 0:
            bcy = b.FY * 10
        else:
            bcy = (b.FY * 10) + 5
        return math.sqrt(math.pow(float(acx - bcx), 2) + math.pow(float(acy - bcy), 2))

    def reverseArray(self, arr):
        """
        Reverses an array in place.
        This is required by `findPath` to return the path from start to end.
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
        self.Field = None
        self.Parent = None
        self.DistCost = 0.0
        self.TotalCost = 0.0
