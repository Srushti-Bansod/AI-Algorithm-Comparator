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
