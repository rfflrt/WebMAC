import random
from collections import deque
import json

difficulties = {"easy": {"rows": 9, "cols": 9, "mines": 10},
                "medium": {"rows": 16, "cols": 16, "mines": 40},
                "medium (Mobile)": {"rows": 15, "cols": 10, "mines": 30},
                "hard": {"rows": 20, "cols": 20, "mines": 110},
                "hard (Mobile)": {"rows": 20, "cols": 10, "mines": 80}}

def place_mines(rows, cols, count, safeR, safeC):
    safe = {(safeR + r, safeC + c)
        for r in range(-1, 2) for c in range(-1, 2)
        if 0 <= safeR+r and safeR+r < rows and
        0 <= safeC+c and safeC+c < cols}
    
    candidates = [(r,c) for r in range(rows) for c in range(cols)
                  if (r,c) not in safe]
    mines = random.sample(candidates, count)

    movers_qty = len(mines) * 0.1
    movers = set(random.sample(range(len(mines)), int(movers_qty)))

    return mines, movers

def count_adj(r, c, rows, cols, mines):
    count = 0
    for dr in range(-1,2):
        for dc in range(-1,2):
            if (r+dr,c+dc) in mines:
                count += 1
    return count

def reveal(r, c, rows, cols, mines, open, flags):
    if (r,c) in mines or (r,c) in open or (r,c) in flags:
        return set()
    
    new = set()
    queue = deque([(r,c)])
    visited={(r,c)}

    while queue:
        cr, cc = queue.popleft()
        new.add((cr, cc))
        if count_adj(cr, cc, rows, cols, mines) == 0:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    nr, nc = cr+dr, cc+dc
                    if (0 <= nr and nr < rows
                        and 0 <= nc and nc < cols
                        and (nr, nc) not in visited
                        and (nr, nc) not in mines
                        and (nr, nc) not in flags
                        and (nr, nc) not in open):
                        visited.add((nr, nc))
                        queue.append((nr, nc))
    return new

def reveal_numbered(r, c, rows, cols, mines, open, flags):
    if (r, c) not in open:
        return {"newly_open": set(), "hit_mine": False, "mine_cell": None}

    adj_count  = count_adj(r, c, rows, cols, mines)
    neighbours = [(r+dr, c+dc)
                  for dr in range(-1, 2) for dc in range(-1, 2)
                  if not (dr == dc == 0)
                  and 0 <= r+dr and r+dr < rows
                  and 0 <= c+dc and c+dc < cols]

    flag_count = sum(1 for nr, nc in neighbours if (nr, nc) in flags)

    if flag_count != adj_count:
        return {"newly_open": set(), "hit_mine": False, "mine_cell": None}

    new = set()
    for nr, nc in neighbours:
        if (nr, nc) in flags or (nr, nc) in open:
            continue

        if (nr, nc) in mines:
            return {"newly_open": new, "hit_mine": True, "mine_cell": [nr, nc]}

        new_cell = reveal(nr, nc, rows, cols, mines, open | new, flags)
        new |= new_cell

    return {"newly_open": new, "hit_mine": False, "mine_cell": None}

def won(rows, cols, mine_count, open):
    return len(open) == rows * cols - mine_count

def move_mines(mines, movers, rows, cols, open, flags):
    new_mines = [None] * len(mines)
    for i, (r,c) in enumerate(mines):
        if i not in movers:
            new_mines[i] = [r,c]
            continue

        if (r,c) in flags:
            new_mines[i] = [r,c]
            continue

        possible = [(r+dr, c+dc) for dr in range(-1, 2) for dc in range(-1,2)
                    if not (dr == 0 or dc == 0)
                    and 0 <= r+dr and r+dr < rows
                    and 0 <= c+dc and c+dc < cols
                    and (r+dr, c+dc) not in open
                    and (r+dr, c+dc) not in flags
                    and (r+dr, c+dc) not in mines]
        
        if possible:
            nr, nc = random.choice(possible)
            new_mines[i] = [nr,nc]
        else:
            new_mines[i] = [r,c]
    
    return new_mines

def build_board(rows, cols, mines, open, flags, reveal_all=False):
    board = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if (r, c) in flags:
                cell = {"r": r, "c": c, "state": "flag"}
            elif (r, c) in open:
                cell = {"r": r, "c": c, "state": "open",
                        "adj": count_adj(r, c, rows, cols, mines), "mine": False}
            elif reveal_all:
                cell = {"r": r, "c": c, "state": "open",
                        "mine": (r, c) in mines,
                        "adj": count_adj(r, c, rows, cols, mines)}
            else:
                cell = {"r": r, "c": c, "state": "hidden"}
            row.append(cell)
        board.append(row)
    return board


# HELPERS
def to_set(json_str: str):
    return {tuple(x) for x in json.loads(json_str)}

def to_json(s: set):
    return json.dumps([list(x) for x in s])