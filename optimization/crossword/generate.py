import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            print(variable, direction, word)
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters


    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                #print(letters[i][j])
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        #print(self.crossword.variables)
        #print(self.domains)
        self.enforce_node_consistency()
        #print('after ')
        #print(self.domains)
        self.ac3()
        #print('after ')
        #print(self.domains)
        #print(f"assignment: {self.backtrack(dict())}")
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            length = var.length
            domain_var = self.domains[var].copy()
            self.domains[var] = {
                word for word in domain_var
                if len(word) == length
            }
            
        

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        if not overlap:
            return False
        s1, s2 = overlap
        revised = False
        to_remove = set()
        for x_word in self.domains[x]:
            if not any(x_word[s1] == y_word[s2] for y_word in self.domains[y]):
                to_remove.add(x_word)

        if to_remove:
            self.domains[x] = set(self.domains[x]) - to_remove
            revised = True
        return revised


    def ac3(self, arcs=None):
        from collections import deque
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = deque((x, y) 
                    for x in self.crossword.variables 
                    for y in self.crossword.neighbors(x))
        else:
            arcs = deque(arcs)
        while arcs:
            x, y = arcs.popleft()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    arcs.append((z, x))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.crossword.variables)


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        #check if all words in assignment are distincts
        #avec set on est assuré que tout les éléments (mots) sont distincts 
        if len(set(assignment.values())) != len(assignment.values()):
            return False
        
        #check if each word matchs var length
        for var, word in assignment.items():
            if len(word) != var.length:
                return False
            
        #check if there is no conflict between two neighbors
        for var in assignment:
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if assignment[var][i] != assignment[neighbor][j]:
                        return False

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = self.crossword.neighbors(var)
        var_words = self.domains[var]
        def count_elimination(word):
            count = 0
            for neighbor in neighbors:
                if neighbor in assignment:
                    continue

                overlap = self.crossword.overlaps[var, neighbor]

                if overlap is None:
                    continue

                i, j = overlap
                for neighbor_word in self.domains[neighbor]:
                    if word[i] != neighbor_word[j]:
                        count += 1
            return count
        
        return sorted(var_words, key=count_elimination)



    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_var = set((var, len(self.domains[var])) for var in self.crossword.variables
                             if var not in assignment)
        max_degree = float("-inf")
        min_length = float("inf")
        chosen_var = None
        for var, length in unassigned_var:
            if length < min_length: 
                min_length = length
                chosen_var = var
            elif length == min_length:
                degree = len(self.crossword.neighbors(var))
                if degree >= max_degree:
                    max_degree = degree
                    chosen_var = var

        return  chosen_var

    

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for word in self.domains[var]:
            assignment[var] = word
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result:
                    return result
                del assignment[var]
        return None
    
    def backtrack_inference(assignments):
        raise NotImplemented
    

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
