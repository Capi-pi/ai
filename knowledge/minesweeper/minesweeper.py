import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        
    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells = self.cells - {cell}
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells = self.cells - {cell}


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        #mark the cell as safe and as a move that has been made
        self.moves_made.add(cell)
        self.mark_safe(cell)

        #add new sentence to AI's knowldge base
        cell_set = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (0 <= i < self.height and 0 <= j < self.width) and (i, j) not in self.moves_made and (i, j) not in self.mines:
                    cell_set.add((i, j))
        new_sentence = Sentence(cell_set, count)
        mines, safes = new_sentence.known_mines(), new_sentence.known_safes()
        if mines:                                       #si non vide
            self.mines |= mines
        if safes:                                       #si non vide
            self.safes |= safes     

        #mark any additional cells as safe or as mines given the new AI's knowledge base
        knowledge_copy = self.knowledge.copy()
        for sentence in knowledge_copy:
            if new_sentence.cells <= sentence.cells:
                mines = sentence.known_mines()
                safes = sentence.known_safes()
                if mines:                               #si non vide
                    self.mines |= mines
                if safes:                               #si non vide
                    self.safes |= safes
                new_cells = sentence.cells - new_sentence.cells
                new_count = sentence.count - new_sentence.count
                if len(new_cells) > 0 and Sentence(new_cells, new_count) not in self.knowledge:
                    self.knowledge.append(Sentence(cells= new_cells,
                                                count = new_count))
        self.knowledge.append(Sentence(cell_set, count))

        # Inference loop: repeat until no new knowledge is gained
        updated = True
        while updated:
            updated = False
            for sentence in self.knowledge:
                new_mines = sentence.known_mines()
                new_safes = sentence.known_safes()

                if new_mines:
                    for cell in new_mines:
                        if cell not in self.mines:
                            self.mark_mine(cell)
                            updated = True

                if new_safes:
                    for cell in new_safes:
                        if cell not in self.safes:
                            self.mark_safe(cell)
                            updated = True


    def make_safe_move(self):
        """
        Returns a safe cell 
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        return a random move when there is no safe move available
        """
        choices = [
            (i,j)
            for i in range(self.height)
            for j in range(self.width)
            if (i,j) not in self.moves_made and (i,j) not in self.mines
        ]
        return random.choice(choices) if choices else None
