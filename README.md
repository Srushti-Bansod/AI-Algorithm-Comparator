# Comparative Analysis of AI Algorithms

Visual head-to-head comparison of BFS, DFS, A\*, Greedy, UCS, and Dijkstra
solving mazes, treasure hunts, escape sims, and 8-puzzles.

## Project Structure

```
algo_battle/
├── algorithms.py   ← All 6 search algorithms + maze/puzzle generators (Python)
├── app.py          ← Flask web server (REST API)
├── index.html      ← Frontend UI 
└── requirements.txt
```
## How It Works

```
Browser (index.html)
      │
      │  POST /api/generate   ← pick a problem / size
      │  POST /api/solve      ← run all selected algorithms
      ▼
Flask Server (app.py)
      │
      │  calls ─────────────► algorithms.py
      │                         BFS / DFS / A* / Greedy / UCS / Dijkstra
      │
      │  returns JSON (path, visited cells, nodes, time, cost)
      ▼
Browser animates the results on HTML5 Canvas
```
## Quick Start

1. **Install dependencies** (only Flask needed):

   ```bash
   pip install flask
   ```

2. **Run the server**:

   ```bash
   python app.py
   ```

3. **Open your browser** at:

   ```
   http://localhost:5000
   ```

4. Pick a problem, select algorithms, hit **▶ START BATTLE**!

## Algorithms 
- **Breadth First Search(BFS)** - explores level by level (queue)
- **Depth First Search(DFS)** - dives deep first (stack) 
- **A\* Algorithm** - cost + heuristic estimate
- **Greedy Algorithm** - always moves toward goal
- **Uniform Cost Structure(UCS)** - cheapest node first (no heuristic)
- **Dijkstra Algorithm** - shortest path to all nodes

## Problems
- **Maze Solver** - classic recursive-backtracking maze, find S→G
- **Treasure Hunt** - open grid with terrain costs, find nearest treasure
- **Escape Sim** - escape a room with fire hazards through any exit
- **8-Puzzle** - slide tiles to reach goal state [1,2,3,4,5,6,7,8,_]

