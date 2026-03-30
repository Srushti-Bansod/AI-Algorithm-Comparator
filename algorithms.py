import random
import heapq
from collections import deque

# ─── MAZE GENERATION ────────────────────────────────────────────────────────
def generate_maze(rows, cols):
    """
    Generate a maze using recursive backtracking (DFS carving).
    Walls = 1, open = 0.
    Returns: (grid, start, end)
    """
    # Start with all walls
    grid = [[1] * cols for _ in range(rows)]

    visited = [[False] * cols for _ in range(rows)]

    def carve(r, c):
        visited[r][c] = True
        grid[r][c] = 0
        # Shuffle directions so maze is random each time
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1 and not visited[nr][nc]:
                # Remove the wall between current cell and neighbor
                grid[r + dr // 2][c + dc // 2] = 0
                carve(nr, nc)

    carve(1, 1)
    start = (1, 1)
    end = (rows - 2, cols - 2)
    grid[end[0]][end[1]] = 0
    return grid, start, end


# ─── TREASURE HUNT MAP ──────────────────────────────────────────────────────
def generate_treasure(rows, cols):
    """
    Generate a treasure hunt map with open terrain (cost 1/2/3), walls (99),
    treasure spots, and traps.
    Returns: (grid, src, treasures, traps)
    """
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if r == 0 or c == 0 or r == rows - 1 or c == cols - 1:
                row.append(99)  # border walls
            else:
                rnd = random.random()
                if rnd < 0.18:
                    row.append(99)   # wall
                elif rnd < 0.32:
                    row.append(3)    # dense terrain (cost 3)
                elif rnd < 0.52:
                    row.append(2)    # rough terrain (cost 2)
                else:
                    row.append(1)    # open (cost 1)
        grid.append(row)

    grid[1][1] = 1  # make sure start is open

    # Place 3 treasure spots
    treasures = []
    attempts = 0
    while len(treasures) < 3 and attempts < 500:
        attempts += 1
        r = random.randint(1, rows - 2)
        c = random.randint(1, cols - 2)
        if grid[r][c] != 99 and abs(r - 1) + abs(c - 1) > 6:
            if (r, c) not in treasures:
                treasures.append((r, c))

    # Place 4 traps
    traps = []
    for _ in range(4):
        for att in range(200):
            r = random.randint(1, rows - 2)
            c = random.randint(1, cols - 2)
            if grid[r][c] != 99 and (r, c) not in treasures and (r, c) != (1, 1):
                traps.append((r, c))
                break

    src = (1, 1)
    return grid, src, treasures, traps
