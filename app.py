import time
from flask import Flask, jsonify, request, send_from_directory
from algorithms import (
    generate_maze, generate_treasure, generate_escape, shuffle_puzzle,
    solve_maze, solve_treasure, solve_escape, solve_puzzle,
    PUZZLE_GOAL
)

app = Flask(__name__, static_folder='.')

#  State stored in memory
state = {
    'prob': 'maze',
    'rows': 11,
    'cols': 17,
    'grid': [],
    'src': (1, 1),
    'dst': None,
    'treasures': [],
    'traps': [],
    'exits': [],
    'fire': [],
    'puzzle': [],
}

def refresh_grid():
    """Regenerate the current problem's grid based on state['prob']."""
    prob = state['prob']
    r, c = state['rows'], state['cols']

    if prob == 'maze':
        grid, src, dst = generate_maze(r, c)
        state.update(grid=grid, src=src, dst=dst, treasures=[], traps=[], exits=[], fire=[])

    elif prob == 'treasure':
        grid, src, treasures, traps = generate_treasure(r, c)
        state.update(grid=grid, src=src, dst=None, treasures=treasures, traps=traps, exits=[], fire=[])

    elif prob == 'escape':
        grid, src, exits, fire = generate_escape(r, c)
        state.update(grid=grid, src=src, dst=None, treasures=[], traps=[], exits=exits, fire=fire)

    elif prob == 'puzzle':
        puzzle = shuffle_puzzle()
        state.update(grid=[], src=None, dst=None, puzzle=puzzle, treasures=[], traps=[], exits=[], fire=[])

# Generate initial maze on startup
refresh_grid()

# ─── ROUTES ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('.', 'index.html')


@app.route('/api/generate', methods=['POST'])
def api_generate():
    """
    Generate a new problem.
    Body (JSON):
        prob  — 'maze' | 'treasure' | 'escape' | 'puzzle'
        rows  — grid height (optional)
        cols  — grid width (optional)
    """
    data = request.get_json() or {}
    state['prob'] = data.get('prob', state['prob'])
    if 'rows' in data:
        state['rows'] = data['rows']
    if 'cols' in data:
        state['cols'] = data['cols']

    refresh_grid()

    return jsonify(get_state_payload())


@app.route('/api/solve', methods=['POST'])
def api_solve():
    """
    Solve the current problem with selected algorithms.
    Body (JSON):
        algos — list of algorithm names e.g. ['bfs', 'dfs', 'astar']

    Returns timing + path + visited order for each algorithm.
    """
    data = request.get_json() or {}
    algos = data.get('algos', ['bfs', 'dfs', 'astar', 'greedy'])

    results = {}
    for algo in algos:
        t0 = time.perf_counter()
        result = run_algorithm(algo)
        elapsed_ms = round((time.perf_counter() - t0) * 1000)
        result['time'] = elapsed_ms
        result['pathLen'] = len(result['path'])
        results[algo] = result

    return jsonify({'results': results, 'problem': get_state_payload()})


def run_algorithm(algo):
    """Dispatch algorithm to the right problem solver."""
    prob = state['prob']

    if prob == 'maze':
        res = solve_maze(algo, state['grid'], state['src'], state['dst'])

    elif prob == 'treasure':
        res = solve_treasure(algo, state['grid'], state['src'], state['treasures'])

    elif prob == 'escape':
        res = solve_escape(algo, state['grid'], state['src'], state['exits'], state['fire'])

    elif prob == 'puzzle':
        res = solve_puzzle(algo, state['puzzle'])

    else:
        res = {"found": False, "path": [], "visited": [], "nodes": 0, "cost": 0}

    return res
