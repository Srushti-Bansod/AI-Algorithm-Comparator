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

# ─── ESCAPE SIMULATION MAP ──────────────────────────────────────────────────

def generate_escape(rows, cols):
    """
    Generate an escape simulation map with exits on edges and fire in corners.
    Returns: (grid, src, exits, fire)
    """
    grid = [[0] * cols for _ in range(rows)]

    # Walls on borders and random interior walls
    for r in range(rows):
        for c in range(cols):
            if r == 0 or c == 0 or r == rows - 1 or c == cols - 1:
                grid[r][c] = 1
            elif random.random() < 0.2:
                grid[r][c] = 1

    # Open exits at mid-edges
    exits = [
        (0, cols // 2),
        (rows - 1, cols // 2),
        (rows // 2, 0),
        (rows // 2, cols - 1),
    ]
    for er, ec in exits:
        grid[er][ec] = 0

    # Agent starts in center
    src = (rows // 2, cols // 2)
    grid[src[0]][src[1]] = 0

    # Fire in corners
    fire = [(1, 1), (1, cols - 2), (rows - 2, 1), (rows - 2, cols - 2)]
    for fr, fc in fire:
        grid[fr][fc] = 0

    return grid, src, exits, fire


# ─── SHARED SEARCH HELPER ───────────────────────────────────────────────────

def grid_search(algo, grid, src, is_goal_fn, neighbors_fn, heuristic_fn, cost_fn, max_nodes=60000):
    """
    Core search dispatcher. Runs the chosen algorithm on a grid.

    Parameters:
        algo         — algorithm name: 'bfs', 'dfs', 'astar', 'greedy', 'ucs', 'dijkstra'
        grid         — 2D list of cell values
        src          — (row, col) start position
        is_goal_fn   — function(r, c) -> bool: True if this cell is the goal
        neighbors_fn — function(r, c) -> list of (nr, nc)
        heuristic_fn — function(r, c) -> estimated distance to goal (for A* / Greedy)
        cost_fn      — function(nr, nc) -> movement cost to enter that cell
        max_nodes    — safety cap so we never loop forever

    Returns dict:
        found   — True if goal was reached
        path    — list of (r, c) from start to goal
        visited — list of (r, c) in exploration order (for animation)
        nodes   — number of nodes explored
        cost    — total path cost
    """
    rows = len(grid)
    cols = len(grid[0])

    # prev maps each cell key -> parent cell (for path reconstruction)
    prev = {}

    def reconstruct(r, c):
        """Trace back from goal to start using `prev`."""
        path = []
        cur = (r, c)
        while cur is not None:
            path.append(cur)
            cur = prev.get(cur)
        path.reverse()
        return path

    visited_order = []   # cells in the order they were explored (for animation)
    nodes_visited = 0
    
    # ── BFS ──────────────────────────────────────────────────────────────────
    if algo == 'bfs':
        # Queue: first in, first out → explores all neighbors at distance d before d+1
        queue = deque([(src[0], src[1])])
        seen = {(src[0], src[1])}
        prev[(src[0], src[1])] = None

        while queue and nodes_visited < max_nodes:
            r, c = queue.popleft()
            nodes_visited += 1
            visited_order.append((r, c))

            if is_goal_fn(r, c):
                path = reconstruct(r, c)
                return {"found": True, "path": path, "visited": visited_order, "nodes": nodes_visited, "cost": len(path) - 1}

            for nr, nc in neighbors_fn(r, c):
                if (nr, nc) not in seen:
                    seen.add((nr, nc))
                    prev[(nr, nc)] = (r, c)
                    queue.append((nr, nc))

    # ── DFS ──────────────────────────────────────────────────────────────────
    elif algo == 'dfs':
        # Stack: last in, first out → dives deep before exploring siblings
        stack = [(src[0], src[1])]
        seen = set()
        prev[(src[0], src[1])] = None

        while stack and nodes_visited < max_nodes:
            r, c = stack.pop()
            if (r, c) in seen:
                continue
            seen.add((r, c))
            nodes_visited += 1
            visited_order.append((r, c))

            if is_goal_fn(r, c):
                path = reconstruct(r, c)
                return {"found": True, "path": path, "visited": visited_order, "nodes": nodes_visited, "cost": len(path) - 1}

            for nr, nc in neighbors_fn(r, c):
                if (nr, nc) not in seen:
                    prev[(nr, nc)] = (r, c)
                    stack.append((nr, nc))

    # ── A* ───────────────────────────────────────────────────────────────────
    elif algo == 'astar':
        # Priority queue sorted by f = g (cost so far) + h (estimated cost to goal)
        # This guarantees the optimal path if heuristic never overestimates
        g_cost = {(src[0], src[1]): 0}
        h0 = heuristic_fn(src[0], src[1])
        heap = [(h0, 0, src[0], src[1])]   # (f, g, r, c)
        counter = 0
        prev[(src[0], src[1])] = None

        while heap and nodes_visited < max_nodes:
            f, g, r, c = heapq.heappop(heap)
            nodes_visited += 1
            visited_order.append((r, c))

            if is_goal_fn(r, c):
                path = reconstruct(r, c)
                return {"found": True, "path": path, "visited": visited_order, "nodes": nodes_visited, "cost": g}

            for nr, nc in neighbors_fn(r, c):
                ng = g + cost_fn(nr, nc)
                if (nr, nc) not in g_cost or ng < g_cost[(nr, nc)]:
                    g_cost[(nr, nc)] = ng
                    prev[(nr, nc)] = (r, c)
                    f_new = ng + heuristic_fn(nr, nc)
                    counter += 1
                    heapq.heappush(heap, (f_new, counter, nr, nc))
    # ── GREEDY ───────────────────────────────────────────────────────────────
    elif algo == 'greedy':
        # Always move to the neighbor closest to the goal (heuristic only, ignores cost)
        heap = [(heuristic_fn(src[0], src[1]), 0, src[0], src[1])]
        seen = {(src[0], src[1])}
        prev[(src[0], src[1])] = None
        counter = 0

        while heap and nodes_visited < max_nodes:
            h, _, r, c = heapq.heappop(heap)
            nodes_visited += 1
            visited_order.append((r, c))

            if is_goal_fn(r, c):
                path = reconstruct(r, c)
                return {"found": True, "path": path, "visited": visited_order, "nodes": nodes_visited, "cost": len(path) - 1}

            for nr, nc in neighbors_fn(r, c):
                if (nr, nc) not in seen:
                    seen.add((nr, nc))
                    prev[(nr, nc)] = (r, c)
                    counter += 1
                    heapq.heappush(heap, (heuristic_fn(nr, nc), counter, nr, nc))
                    
