import sys

class Node:
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action   

class StackFrontier:
    def __init__(self):
        self.frontier = []
    
    def add(self, node):
        self.frontier.append(node)
    
    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)
    
    def empty(self):
        return len(self.frontier) == 0
            
    def remove(self):
        if self.empty():
            raise Exception("Empty Frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise ("Empty Frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node
        
class Maze:
    def __init__(self, fileName):
        self.solution = None
        self.fileName = fileName
        with open(self.fileName) as file:
            contents = file.read()
        
        #check for start and goal point
        if contents.count("A") != 1 or contents.count("B") != 1:
            raise Exception("There must be exactly one starting point A and one goal point B")
        
        #get height and width of maze
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        #get walls of the maze
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else: 
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)
    
    def printSolution(self):
        #self.solution est sous la forme (actions, cells) où actions et cells représentent resp la séquence des actions et cases à suivre pour trouver la solution.
        if self.solution is None:
            print("No solution")
        else:
            cells = self.solution[1]
            for i in range(self.height):
                for j in range(self.width):
                    if self.walls[i][j] == True:
                        print("█", end="")
                    elif (i, j) == self.start:
                        print("A", end="")
                    elif (i, j) == self.goal:
                        print("B", end="")
                    elif (i, j) in cells:
                        print("*", end="")
                    else:
                        print(" ", end="")
                print()


    def neighbors(self, state):
        row, col = state
        candidates = [
                    ("up",    (row - 1, col)),
                    ("down",  (row + 1, col)),
                    ("left",  (row,     col - 1)),
                    ("right", (row,     col + 1))]
        
        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result
    
    def solve(self):
        #starting point and initial frontier
        initialNode = Node(state = self.start, parent = None, action = None)
        frontier = QueueFrontier()
        frontier.add(initialNode)

        #keep track of explored node
        self.explored_set = set()
        self.explored_count = 0

        while True:
            #check exception
            if frontier.empty():
                raise Exception("No solution")
            
            #remove a node from the frontier
            currentNode = frontier.remove()
            self.explored_count += 1
            
            #check if currentNode contains goal state
            if currentNode.state == self.goal:
                actions, cells = [], []
                while currentNode.parent is not None:
                    actions.append(currentNode.action)
                    cells.append(currentNode.state)
                    currentNode = currentNode.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return
            
            #mark current node as explored
            self.explored_set.add(currentNode.state)

            #add neighbors node to frontier
            neighbors = self.neighbors(currentNode.state)
            for action, (r, c) in neighbors:
                newNode = Node(state = (r, c), parent = currentNode, action = action)
                if not frontier.contains_state(newNode.state) and newNode.state not in self.explored_set:
                    frontier.add(newNode)



if len(sys.argv) != 2:
    sys.exit("Usage: python3 maze.py maze.txt")

m = Maze(sys.argv[1])
print("Maze:")
print("Solving...")
m.solve()
print("States Explored:", m.explored_count)
print("Solution:")
m.printSolution()
