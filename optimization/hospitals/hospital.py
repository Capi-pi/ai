import math
import random
from PIL import Image, ImageDraw, ImageFont

class Space():
    def __init__(self, height, width, hospitals_nums):
        self.height = height
        self.width = width
        self.houses = set()
        self.hospitals_nums = hospitals_nums
        self.hospitals = set()

    def add_house(self, row, col):
        self.houses.add((row, col))

    def available_spaces(self):
        """Returns all cells not currently used by a house or hospital."""
        available = set(
            (row, col)
            for row in range(self.height)
            for col in range(self.width)
        )
        for house in self.houses:
            available.remove(house)
        for hospital in self.hospitals:
            available.remove(hospital)
        return available


    def get_cost(self, hospitals):
        """Calculates sum of distances from houses to nearest hospital."""
        cost = 0
        for row_house, col_house in self.houses:
            #find nearest hospitals
            d = float("inf")
            for r, c in hospitals:
                if abs(row_house - r) + abs(col_house - c) < d:
                    d = abs(row_house - r) + abs(col_house - c)
            cost += d
        return cost


    def get_neighbors(self, row, col):
        """Returns neighbors not already containing a house or hospital."""
        candidate_neighbors = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1)
        ]
        neighbors = []
        for r, c in candidate_neighbors:
            if 0 <= r < self.height and 0 <= c < self.width and (r, c) not in self.houses and (r, c) not in self.hospitals:
                neighbors.append((r, c))
        return neighbors

    #main algorithm for local search
    def hill_climb(self, image_prefix=None, log=False):
        """Performs hill-climbing to find a solution."""
        img_count = 0

        # Start by initializing hospitals randomly
        self.hospitals = set()
        for i in range(self.hospitals_nums):
            self.hospitals.add(random.choice(list(self.available_spaces())))
        current_cost = self.get_cost(self.hospitals)
        if log:
            print("Initial state: cost", current_cost)
        if image_prefix:
            self.output_image(f"{image_prefix}{str(img_count).zfill(3)}.png")

        # Continue until we reach maximum number of iterations
        searching = True
        iteration = 0
        while searching:
            img_count += 1
            best_neighbor = None
            best_neighbor_cost = current_cost
            for hospital in self.hospitals:
                
                for replacement in self.get_neighbors(*hospital):
                    neighbors = self.hospitals.copy()
                    neighbors.remove(hospital)
                    neighbors.add(replacement)
                    neighbors_cost = self.get_cost(neighbors)

                    #check if neighbors is better than the best_neighbors
                    if neighbors_cost < best_neighbor_cost:
                        best_neighbor_cost = neighbors_cost
                        best_neighbor = neighbors
            
            if best_neighbor_cost < current_cost:
                current_cost = best_neighbor_cost
                self.hospitals = best_neighbor
                if log:
                    print(f"{iteration} Nouveau meilleur coup: {current_cost}")
                iteration += 1
                if image_prefix:
                    self.output_image(f"{image_prefix}{str(img_count).zfill(3)}.png")

            else:
                if log:
                    print(f"{iteration} minimum local atteint: {current_cost}")
                if image_prefix:
                    self.output_image(f"{image_prefix}{str(img_count).zfill(3)}.png")
                return self.hospitals

    #best variant of hill climb
    def random_restart(self, n_restart, log=False):
        best_solution = None
        best_cost = float("inf")
    
        for i in range(n_restart):
            current_solution = self.hill_climb("restart{i}_hill_climb", log)
            current_cost = self.get_cost(current_solution)
            if log:
                print(f"restart {i}: cost = {current_cost}")

            if current_cost < best_cost:
                best_cost = current_cost
                best_solution = current_solution

        return best_solution

    
    def simulated_annealing(self, image_prefix, temperature_init, cooling_rate, log):
        """Performs simulated_annealing to find a solution."""
        img_count = 0

        # Start by initializing hospitals randomly
        self.hospitals = set()
        for i in range(self.hospitals_nums):
            self.hospitals.add(random.choice(list(self.available_spaces())))
        current_cost = self.get_cost(self.hospitals)
        if log:
            print("Initial state: cost", current_cost)
        if image_prefix:
            self.output_image(f"{image_prefix}{str(img_count).zfill(3)}.png")
        temperature = float(temperature_init)

        # Continue until we reach min temperature
        iteration = 0
        while temperature > 0.1:
            img_count += 1
            iteration += 1

            # Pick a random hospital to move
            hospital = random.choice(list(self.hospitals))
            neighbors = self.get_neighbors(*hospital)
            if not neighbors:
                continue

            # Pick a random neighbor
            replacement = random.choice(list(neighbors))
            new_hospitals = self.hospitals.copy()
            new_hospitals.remove(hospital)
            new_hospitals.add(replacement)
            new_cost = self.get_cost(new_hospitals)

            delta = new_cost - current_cost

            # Decide whether to accept
            if delta < 0:
                accept = True
            else:
                proba = math.exp(-delta / temperature)
                accept = random.random() < proba

            if accept:
                self.hospitals = new_hospitals
                current_cost = new_cost
                if log:
                    print(f"{iteration}: New state accepted with cost {current_cost}")
                if image_prefix:
                    self.output_image(f"{image_prefix}{str(img_count).zfill(3)}.png")

            temperature *= cooling_rate

        if log:
            print(f"Final cost after annealing: {current_cost}")





    def output_image(self, filename):
        """Generates image with all houses and hospitals."""
        cell_size = 100
        cell_border = 2
        cost_size = 40
        padding = 10

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size,
             self.height * cell_size + cost_size + padding * 2),
            "white"
        )
        house = Image.open("assets/images/House.png").resize(
            (cell_size, cell_size)
        )
        hospital = Image.open("assets/images/Hospital.png").resize(
            (cell_size, cell_size)
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 30)
        draw = ImageDraw.Draw(img)

        for i in range(self.height):
            for j in range(self.width):

                # Draw cell
                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                draw.rectangle(rect, fill="black")

                if (i, j) in self.houses:
                    img.paste(house, rect[0], house)
                if (i, j) in self.hospitals:
                    img.paste(hospital, rect[0], hospital)

        # Add cost
        draw.rectangle(
            (0, self.height * cell_size, self.width * cell_size,
             self.height * cell_size + cost_size + padding * 2),
            "black"
        )
        draw.text(
            (padding, self.height * cell_size + padding),
            f"Cost: {self.get_cost(self.hospitals)}",
            fill="white",
            font=font
        )
        img.save(filename)


n = 10
h = 20
w = 30
random.seed(0)
space1 = Space(h, w, 4)
for i in range(n):
    space1.add_house(random.randint(0, h - 1), random.randint(0, w - 1))

#space1.hill_climb("hill-climb", log=True)
#space1.random_restart(n_restart=8, log=True)
space1.hill_climb(image_prefix="hill-climb", temperature_init=100, cooling_rate=0.99, log=True)