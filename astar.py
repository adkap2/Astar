import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))

pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0) # RGB
GREEN = (0, 255, 0) # RGB
BLUE = (0, 255, 0) # RGB
YELLOW = (255, 255, 0) # RGB
WHITE = (255, 255, 255) # RGB
BLACK = (0, 0, 0) # RGB
PURPLE = (128, 0, 128) # RGB
ORANGE = (255, 165, 0) # RGB
GREY = (128, 128, 128) # RGB
TURQUOISE = (64, 224, 208) # RGB

class Spot:

    def __init__(self, row, col, width, total_rows):

        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):    
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE
    
    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE
    
    def make_end(self):
        self.color = TURQUOISE
    
    def make_path(self):
        self.color = PURPLE

    def draw(self, win):    
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row +1][self.col].is_barrier(): # Down
            self.neighbors.append(grid[self.row +1][self.col])

        if self.row > 0 and not grid[self.row -1][self.col].is_barrier(): # Up
            self.neighbors.append(grid[self.row -1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col +1].is_barrier(): # Right
            self.neighbors.append(grid[self.row][self.col +1])

        if self.col > 0 and not grid[self.row][self.col -1].is_barrier():    # Left
            self.neighbors.append(grid[self.row][self.col -1])
        
        

    def __lt__(self, other):
        return False

def h(p1, p2): # Heuristic function
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2) # Manhattan distance

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()

    open_set.put((0, count, start)) # f score, count, node
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row} # g score for each spot
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row} # f score for each spot
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start} # To keep track of items in the priority queue

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2] # Get the node with the lowest f score
        open_set_hash.remove(current)

        if current == end:
            # Make path
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1 # Distance from start to neighbor

            if temp_g_score < g_score[neighbor]: # If we found a better path
                came_from[neighbor] = current # Update the path
                g_score[neighbor] = temp_g_score # Update the g score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos()) # Update the f score

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor)) # Add the neighbor to the priority queue
                    open_set_hash.add(neighbor) # Add the neighbor to the hash set
                    neighbor.make_open() # Make the neighbor green

        draw()

        if current != start:
            current.make_closed()

    return False
    



def make_grid(rows, width):
    grid = []
    gap = width // rows # Integer division

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot) # Append a spot object to the grid

    return grid

def draw_grid(win, rows, width):

    gap = width // rows

    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))

        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):

    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()



def get_clicked_pos(pos, rows, width):

    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


def main(width, height):

    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True

    while run:
        draw(WIN, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


            if pygame.mouse.get_pressed()[0]: # Left mouse button
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]

                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    algorithm(lambda: draw(WIN, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)


    pygame.quit()

main(WIDTH, WIDTH)
