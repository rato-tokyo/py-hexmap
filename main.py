import math
import json

# Global function equivalent to getFieldKey in Go
def getFieldKey(x, y):
    return "f" + str(x) + "x" + str(y)

# Global function equivalent to validateLocation in Go
def validateLocation(x, y, board):
    if getFieldKey(x, y) in board.Fields:
        return Point2D(x, y)
    else:
        return None

# Pathfinder class
class Pathfinder:
    def __init__(self):
        pass

    def findPath(self, board, startField, endField, avoidEstate, avoidWater):
        # If start or end field is None, return None
        if startField is None or endField is None:
            return None

        if startField.Type == "water":
            avoidWater = False

        tiles = []
        path = []
        tileLength = {}
        pathFieldLength = {}

        # Append starting tile
        tiles.append(Tile())
        tiles[-1].Field = startField
        tiles[-1].TotalCost = 0

        moveCost = [5, 5, 5, 5, 5, 5]

        # Loop until path is found or no tiles remain
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
            # Added to prevent undefined error
            if path[pathIndex].Parent is None:
                break
            pathIndex = pathFieldLength[self.getFieldStrKey(path[pathIndex].Parent.Field)]
        self.reverseArray(finalPath)
        return finalPath

    def canWalk(self, a, b, avoidEstate, avoidWater):
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
        return getFieldKey(field.FX, field.FY)

    def getDistance(self, a, b):
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
        i, j = 0, len(arr) - 1
        while i < j:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
            j -= 1

# Tile class
class Tile:
    def __init__(self):
        self.Field = None
        self.Parent = None
        self.DistCost = 0.0
        self.TotalCost = 0.0

# HexMap class
class HexMap:
    def __init__(self, mapNumber):
        self.RandomSeed = mapNumber
        self.Board = NewBoard()
        self.Board.MapNumber = mapNumber
        self.Board.TownNames = generateAllTowns()
        self.Pathfinder = NewPathfinder()

    def rand(self, n):
        self.RandomSeed = (self.RandomSeed * 9301 + 49297) % 233280
        return int(math.floor((self.RandomSeed / 233280) * n))

    def getField(self, x, y, board):
        key = getFieldKey(x, y)
        return board.Fields.get(key)

    def addField(self, x, y, board):
        key = getFieldKey(x, y)
        board.Fields[key] = Field()
        field = board.Fields[key]
        field.FX = x
        field.FY = y
        # Calculate pixel positions using integer arithmetic as in Go
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
        newFields = 0
        for n in range(6):
            neighbor = board.getNeighborField(field, n)
            if neighbor is not None and neighbor.Type == "land" and neighbor.LandId < 0:
                board.LandGroups[landId].append(neighbor)
                neighbor.LandId = landId
                newFields += 1
        return newFields

    def generateLandGroups(self, board):
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
        for index in range(len(arr)):
            tmp = arr[index]
            randIndex = self.rand(len(arr))
            # Swap with random index
            arr[index] = arr[randIndex]
            arr[randIndex] = tmp

    def generatePorts(self, board):
        portNum = 0
        pathNum = 0
        for town in range(len(board.Towns) - 1):
            path = self.Pathfinder.findPath(board, board.Towns[town], board.Towns[town+1], ["town"], True)
            if path is None or len(path) > portNum:
                path = self.Pathfinder.findPath(board, board.Towns[town], board.Towns[town+1], ["town"], False)
                pathNum += 1
            for pathIndex in range(1, len(path) - 1):
                if path[pathIndex].Type == "land" and path[pathIndex+1].Type == "water":
                    path[pathIndex].Estate = "port"
                    portNum += 1
                if path[pathIndex].Type == "land" and path[pathIndex-1].Type == "water":
                    path[pathIndex].Estate = "port"
                    portNum += 1

    def randTown(self):
        townNames = self.Board.TownNames
        randIndex = self.rand(len(townNames))
        # Swap values between index 0 and randIndex
        townName = townNames[randIndex]
        townNames[randIndex] = townNames[0]
        townNames[0] = townName
        # Return the town at index 0 and remove from the list
        self.Board.TownNames = townNames[1:]
        return townName

    def generateBoard(self, board):
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
        self.generateBoard(self.Board)

# Board class
class Board:
    def __init__(self):
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
        neighborLocation = field.Neighbors[neighborIndex]
        if neighborLocation is None:
            return None
        key = getFieldKey(neighborLocation.X, neighborLocation.Y)
        return self.Fields.get(key)

# Field class
class Field:
    def __init__(self):
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

# Point2D class
class Point2D:
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

# Function to generate all towns
def generateAllTowns():
    return [
        "Abu Dhabi", "Abuja", "Accra", "Addis Ababa", "Algiers", "Amman", "Amsterdam", "Ankara", "Antananarivo", "Apia", "Ashgabat", "Asmara", "Astana", "Asunción", "Athens",
        "Baghdad", "Baku", "Bamako", "Bangkok", "Bangui", "Banjul", "Basseterre", "Beijing", "Beirut", "Belgrade", "Belmopan", "Berlin", "Bern", "Bishkek", "Bissau", "Bogotá",
        "Brasília", "Bratislava", "Brazzaville", "Bridgetown", "Brussels", "Bucharest", "Budapest", "Buenos Aires", "Bujumbura", "Cairo", "Canberra",
        "Cape Town", "Caracas", "Castries", "Chisinau", "Conakry", "Copenhagen", "Cotonou",
        "Dakar", "Damascus", "Dhaka", "Dili", "Djibouti", "Dodoma", "Doha", "Dublin", "Dushanbe", "Delhi",
        "Freetown", "Funafuti", "Gabarone", "Georgetown", "Guatemala City", "Hague", "Hanoi", "Harare", "Havana", "Helsinki", "Honiara", "Hong Kong",
        "Islamabad", "Jakarta", "Jerusalem", "Kabul", "Kampala", "Kathmandu", "Khartoum", "Kyiv", "Kigali", "Kingston", "Kingstown", "Kinshasa", "Kuala Lumpur", "Kuwait City",
        "La Paz", "Liberville", "Lilongwe", "Lima", "Lisbon", "Ljubljana", "Lobamba", "Lomé", "London", "Luanda", "Lusaka", "Luxembourg",
        "Madrid", "Majuro", "Malé", "Managua", "Manama", "Manila", "Maputo", "Maseru", "Mbabane", "Melekeok", "Mexico City", "Minsk", "Mogadishu", "Monaco", "Monrovia", "Montevideo", "Moroni", "Moscow", "Muscat",
        "Nairobi", "Nassau", "Naypyidaw", "N'Djamena", "New Delhi", "Niamey", "Nicosia", "Nouakchott", "Nuku'alofa", "Nuuk",
        "Oslo", "Ottawa", "Ouagadougou", "Palikir", "Panama City", "Paramaribo", "Paris", "Phnom Penh", "Podgorica", "Prague", "Praia", "Pretoria", "Pyongyang",
        "Quito", "Rabat", "Ramallah", "Reykjavík", "Riga", "Riyadh", "Rome", "Roseau",
        "San José", "San Marino", "San Salvador", "Sanaá", "Santiago", "Santo Domingo", "Sao Tomé", "Sarajevo", "Seoul", "Singapore", "Skopje", "Sofia", "South Tarawa", "St. George's", "St. John's", "Stockholm", "Sucre", "Suva",
        "Taipei", "Tallinn", "Tashkent", "Tbilisi", "Tegucigalpa", "Teheran", "Thimphu", "Tirana", "Tokyo", "Tripoli", "Tunis", "Ulaanbaatar",
        "Vaduz", "Valletta", "Victoria", "Vienna", "Vientiane", "Vilnius", "Warsaw", "Washington", "Wellington", "Windhoek", "Yamoussoukro", "Yaoundé", "Yerevan", "Zagreb", "Zielona Góra",
        "Poznań", "Wrocław", "Gdańsk", "Szczecin", "Łódź", "Białystok", "Toruń", "St. Petersburg", "Turku", "Örebro", "Chengdu",
        "Wuppertal", "Frankfurt", "Düsseldorf", "Essen", "Duisburg", "Magdeburg", "Bonn", "Brno", "Tours", "Bordeaux", "Nice", "Lyon", "Stara Zagora", "Milan", "Bologna", "Sydney", "Venice", "New York",
        "Barcelona", "Zaragoza", "Valencia", "Seville", "Graz", "Munich", "Birmingham", "Naples", "Cologne", "Turin", "Marseille", "Leeds", "Kraków", "Palermo", "Genoa",
        "Stuttgart", "Dortmund", "Rotterdam", "Glasgow", "Málaga", "Bremen", "Sheffield", "Antwerp", "Plovdiv", "Thessaloniki", "Kaunas", "Lublin", "Varna", "Ostrava", "Iaşi", "Katowice"
    ]

# Function to create a new HexMap (equivalent to NewHexMap in Go)
def NewHexMap(mapNumber):
    return HexMap(mapNumber)

# Function to create a new Pathfinder (equivalent to NewPathfinder in Go)
def NewPathfinder():
    return Pathfinder()

# Function to create a new Board (equivalent to NewBoard in Go)
def NewBoard():
    return Board()

def field_to_estate(field):
    if(str(field.Type)=="water"):
        return "water"
    elif(field.Capital != -1):
        return "capital"
    elif(field.Estate  =="" ):
        return "land"
    else:
        return field.Estate

def fields_to_matrix(fields):
    output= [["" for i in range(11)] for j in range(20)]
    for x in range(20):
        for y in range(11):
            key="f"+str(x)+"x"+str(y)
            output[x][y]=field_to_estate(fields[key])
    return output

def create_map_matrix(map_id):
    hex_map = NewHexMap(map_id)
    hex_map.GenerateMap()
    return fields_to_matrix(hex_map.Board.Fields)

map_sample_list=[0,10,1000,123456,9999,99999,999999]