# AI-Algorithm-Comparator
# ⚡ Algorithm Battlefield
Visual head-to-head comparison of BFS, DFS, A\*, Greedy, UCS, and Dijkstra
solving mazes, treasure hunts, escape sims, and 8-puzzles.

## Project Structure

```
algo_battle/
├── algorithms.py   ← All 6 search algorithms + maze/puzzle generators (Python)
├── app.py          ← Flask web server (REST API)
├── index.html      ← Frontend UI (same look as original, calls Flask)
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
