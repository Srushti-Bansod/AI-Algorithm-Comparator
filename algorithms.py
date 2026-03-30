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

  # ── UCS ──────────────────────────────────────────────────────────────────
    elif algo == 'ucs':
        # Like BFS but expands cheapest node first (no heuristic)
        g_cost = {(src[0], src[1]): 0}
        heap = [(0, 0, src[0], src[1])]
        prev[(src[0], src[1])] = None
        counter = 0

        while heap and nodes_visited < max_nodes:
            g, _, r, c = heapq.heappop(heap)
            if g > g_cost.get((r, c), float('inf')):
                continue  # stale entry
            nodes_visited += 1
            visited_order.append((r, c))

            if is_goal_fn(r, c):
                path = reconstruct(r, c)
                return {"found": True, "path": path, "visited": visited_order, "nodes": nodes_visited, "cost": g}

            for nr, nc in neighbors_fn(r, c):
                ng = g + cost_fn(nr, nc)
                if ng < g_cost.get((nr, nc), float('inf')):
                    g_cost[(nr, nc)] = ng
                    prev[(nr, nc)] = (r, c)
                    counter += 1
                    heapq.heappush(heap, (ng, counter, nr, nc))

    # ── DIJKSTRA ─────────────────────────────────────────────────────────────
    elif algo == 'dijkstra':
        # Finds shortest paths from source to ALL reachable cells
        # Stops once the goal is reached
        dist = {(src[0], src[1]): 0}
        heap = [(0, 0, src[0], src[1])]
        visited_set = set()
        prev[(src[0], src[1])] = None
        counter = 0

        while heap and nodes_visited < max_nodes:
            g, _, r, c = heapq.heappop(heap)
            if (r, c) in visited_set:
                continue
            visited_set.add((r, c))
            nodes_visited += 1
            visited_order.append((r, c))

            if is_goal_fn(r, c):
                path = reconstruct(r, c)
                return {"found": True, "path": path, "visited": visited_order, "nodes": nodes_visited, "cost": g}

            for nr, nc in neighbors_fn(r, c):
                if (nr, nc) not in visited_set:
                    ng = g + cost_fn(nr, nc)
                    if ng < dist.get((nr, nc), float('inf')):
                        dist[(nr, nc)] = ng
                        prev[(nr, nc)] = (r, c)
                        counter += 1
                        heapq.heappush(heap, (ng, counter, nr, nc))

    return {"found": False, "path": [], "visited": visited_order, "nodes": nodes_visited, "cost": 0}

# ─── PROBLEM-SPECIFIC SOLVERS ────────────────────────────────────────────────
def solve_maze(algo, grid, src, dst):
    """Solve a maze: find path from src to dst."""
    rows, cols = len(grid), len(grid[0])

    def neighbors(r, c):
        result = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                result.append((nr, nc))
        return result

    def heuristic(r, c):
        # Manhattan distance to destination (admissible for grids)
        return abs(r - dst[0]) + abs(c - dst[1])

    def cost(r, c):
        return 1  # all moves cost the same in a maze

    def is_goal(r, c):
        return (r, c) == dst

    return grid_search(algo, grid, src, is_goal, neighbors, heuristic, cost)


def solve_treasure(algo, grid, src, treasures):
    """Find path from src to the nearest treasure."""
    if not treasures:
        return {"found": False, "path": [], "visited": [], "nodes": 0, "cost": 0}

    rows, cols = len(grid), len(grid[0])

    # Target: closest treasure by Manhattan distance
    target = min(treasures, key=lambda t: abs(t[0] - src[0]) + abs(t[1] - src[1]))

    def neighbors(r, c):
        result = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 99:
                result.append((nr, nc))
        return result

    def heuristic(r, c):
        return abs(r - target[0]) + abs(c - target[1])

    def cost(r, c):
        # Terrain cost: value 1/2/3 maps directly to movement cost
        v = grid[r][c]
        return v if v in (1, 2, 3) else 1

    def is_goal(r, c):
        return (r, c) == target

    return grid_search(algo, grid, src, is_goal, neighbors, heuristic, cost)


def solve_escape(algo, grid, src, exits, fire):
    """Find path from src to any exit, avoiding fire (high cost)."""
    if not exits:
        return {"found": False, "path": [], "visited": [], "nodes": 0, "cost": 0}

    rows, cols = len(grid), len(grid[0])
    fire_set = set(fire)

    def neighbors(r, c):
        result = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                result.append((nr, nc))
        return result

    def heuristic(r, c):
        # Distance to nearest exit
        return min(abs(r - er) + abs(c - ec) for er, ec in exits)

    def cost(r, c):
        # Fire tiles are passable but very costly
        return 5 if (r, c) in fire_set else 1

    def is_goal(r, c):
        return (r, c) in set(exits)

    return grid_search(algo, grid, src, is_goal, neighbors, heuristic, cost)

# ─── 8-PUZZLE SOLVER ─────────────────────────────────────────────────────────

PUZZLE_GOAL = [1, 2, 3, 4, 5, 6, 7, 8, 0]
PUZZLE_GOAL_KEY = ','.join(map(str, PUZZLE_GOAL))


def puzzle_moves(state):
    """
    Return all states reachable from this state by sliding one tile.
    The blank (0) can move up/down/left/right.
    """
    blank = state.index(0)
    br, bc = blank // 3, blank % 3
    moves = []
    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nr, nc = br + dr, bc + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            new_state = state[:]
            new_state[blank] = new_state[nr * 3 + nc]
            new_state[nr * 3 + nc] = 0
            moves.append(new_state)
    return moves


def puzzle_heuristic(state):
    """Manhattan distance: sum of each tile's distance from its goal position."""
    h = 0
    for i, v in enumerate(state):
        if v == 0:
            continue
        goal_pos = PUZZLE_GOAL.index(v)
        h += abs(i // 3 - goal_pos // 3) + abs(i % 3 - goal_pos % 3)
    return h


def solve_puzzle(algo, init):
    """
    Solve the 8-puzzle starting from `init` state (list of 9 ints, 0 = blank).
    Returns same dict format as grid_search.
    """
    MAX = 15000
    nodes = 0
    visited_order = []

    def key(state):
        return ','.join(map(str, state))

    init_key = key(init)

    # BFS / UCS / Dijkstra — all treat puzzle moves as uniform cost
    if algo in ('bfs', 'ucs', 'dijkstra'):
        queue = deque([{'state': init[:], 'path': [init[:]]}])
        seen = {init_key}

        while queue and nodes < MAX:
            cur = queue.popleft()
            s, p = cur['state'], cur['path']
            nodes += 1
            visited_order.append(s[:])

            if key(s) == PUZZLE_GOAL_KEY:
                return {"found": True, "path": p, "visited": visited_order, "nodes": nodes, "cost": len(p) - 1}

            for ns in puzzle_moves(s):
                k = key(ns)
                if k not in seen:
                    seen.add(k)
                    queue.append({'state': ns, 'path': p + [ns]})

    elif algo == 'dfs':
        stack = [{'state': init[:], 'path': [init[:]]}]
        seen = set()

        while stack and nodes < MAX:
            cur = stack.pop()
            s, p = cur['state'], cur['path']
            k = key(s)
            if k in seen:
                continue
            seen.add(k)
            nodes += 1
            visited_order.append(s[:])

            if k == PUZZLE_GOAL_KEY:
                return {"found": True, "path": p, "visited": visited_order, "nodes": nodes, "cost": len(p) - 1}

            for ns in puzzle_moves(s):
                if key(ns) not in seen:
                    stack.append({'state': ns, 'path': p + [ns]})

    elif algo == 'astar':
        # f = g (moves so far) + h (Manhattan distance)
        g_cost = {init_key: 0}
        counter = 0
        heap = [(puzzle_heuristic(init), 0, counter, init[:], [init[:]])]

        while heap and nodes < MAX:
            f, g, _, s, p = heapq.heappop(heap)
            k = key(s)
            nodes += 1
            visited_order.append(s[:])

            if k == PUZZLE_GOAL_KEY:
                return {"found": True, "path": p, "visited": visited_order, "nodes": nodes, "cost": g}

            for ns in puzzle_moves(s):
                ng = g + 1
                nk = key(ns)
                if nk not in g_cost or ng < g_cost[nk]:
                    g_cost[nk] = ng
                    counter += 1
                    heapq.heappush(heap, (ng + puzzle_heuristic(ns), ng, counter, ns, p + [ns]))

    elif algo == 'greedy':
        counter = 0
        heap = [(puzzle_heuristic(init), 0, counter, init[:], [init[:]])]
        seen = {init_key}

        while heap and nodes < MAX:
            h, _, _, s, p = heapq.heappop(heap)
            nodes += 1
            visited_order.append(s[:])

            if key(s) == PUZZLE_GOAL_KEY:
                return {"found": True, "path": p, "visited": visited_order, "nodes": nodes, "cost": len(p) - 1}

            for ns in puzzle_moves(s):
                nk = key(ns)
                if nk not in seen:
                    seen.add(nk)
                    counter += 1
                    heapq.heappush(heap, (puzzle_heuristic(ns), 0, counter, ns, p + [ns]))

    return {"found": False, "path": [], "visited": visited_order, "nodes": nodes, "cost": 0}


def shuffle_puzzle():
    """Generate a solvable shuffled 8-puzzle state by making random moves from goal."""
    state = PUZZLE_GOAL[:]
    for _ in range(200):
        moves = puzzle_moves(state)
        state = random.choice(moves)
    return state
