document.addEventListener("htmx:afterSwap", () => {
  const gd = document.getElementById("game-data");
  if(gd) initGame(gd.dataset);
});

document.addEventListener("DOMContentLoaded", () => {
  const gd = document.getElementById("game-data");
  if (gd) initGame(gd.dataset);
});

timerInterval = null;
tickInterval = null;

function initGame(dataset){
    console.log("initGame called")
    const game_id = parseInt(dataset.gameId)
    const rows = parseInt(dataset.rows)
    const cols = parseInt(dataset.cols)

    let flagMode = false;
    let gameOver = false;
    let hintCell = null;
    let timerStart = null;

    timerInterval = setInterval(() => {
    if(!timerStart || gameOver) return;
    const s = Math.floor((Date.now() - timerStart) / 1000);
    const timer = document.getElementById("timer");
    if (timer) timer.textContent =
      `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
    }, 500);

    window.toggleFlag = function (){
        flagMode = !flagMode;
        const lbl = document.getElementById("flag-label");
        const btn = document.getElementById("flag-btn");
        if (lbl) lbl.textContent = flagMode ? "ON" : "OFF";
        if (btn) btn.classList.toggle("active", flagMode);
    };

    function calcCellSize() {
        const boardWrap = document.getElementById("board-wrap");

        const topOffset = boardWrap
        ? boardWrap.getBoundingClientRect().top
        : 160;

        const gap = 2;
        const padding = 14;

        const availH = window.innerHeight - topOffset - 8 - padding - ((rows - 1) * gap);
        const availW = window.innerWidth  - 16 - padding - ((cols - 1) * gap);

        const byH = Math.floor(availH / rows);
        const byW = Math.floor(availW / cols);

        return Math.min(byH, byW, 40);
    }

    function applySize(){
        const el = document.getElementById("board");
        if (!el) return;
        const size = calcCellSize();
        el.style.gridTemplateColumns = `repeat(${cols}, ${size}px)`;
        el.style.fontSize = `${Math.max(8, Math.floor(size * 0.5))}px`;
        el.querySelectorAll(".cell").forEach(c => {
        c.style.width  = size + "px";
        c.style.height = size + "px";
    });
  }

    window.addEventListener("resize", applySize);

    function renderBoard(boardData){
        const board = document.getElementById("board");
        if(!board) return;

        if(!board.children.length){
            const size = calcCellSize();
            board.style.gridTemplateColumns = `repeat(${cols}, ${size}px)`;
            board.style.fontSize = `${Math.max(8, Math.floor(size * 0.5))}px`;

            for(let r = 0; r < rows; r++){
                for(let c = 0; c < cols; c++){
                    const div = document.createElement("div");
                    div.id = `c-${r}-${c}`;
                    div.className = "cell"
                    div.style.width  = size + "px";
                    div.style.height = size + "px";
                    div.addEventListener("click", ()  => handleClick(r, c));
                    div.addEventListener("contextmenu", e => { e.preventDefault(); handleRightClick(r, c); });
                    let pressTimer;
                    div.addEventListener("touchstart", () => {
                        pressTimer = setTimeout(() => { handleRightClick(r, c); pressTimer = null; }, 500);
                    }, { passive: true });
                    div.addEventListener("touchend", () => { if (pressTimer) clearTimeout(pressTimer); });
                    board.appendChild(div);
                }
            }
        }

        for(const row of boardData)
            for(const cell of row)
                paintCell(cell);
    }

    function paintCell(data){
        const cell = document.getElementById(`c-${data.r}-${data.c}`);
        if(!cell) return;
        cell.className = "cell";
        cell.textContent = "";

        const isHint = hintCell && hintCell[0] === data.r && hintCell[1] === data.c;

        if (data.state === "flag"){
            cell.classList.add("cell-flag");
            cell.textContent = "🚩";
        }
        else if(data.state === "open"){
            if(data.mine){
                cell.classList.add("cell-mine");
                cell.textContent = "💣";
            }
            else{
                cell.classList.add("cell-open");
                if(data.adj > 0){
                    cell.textContent = data.adj;
                    cell.classList.add(`n${data.adj}`);
                }
            }
        }
        else
        cell.classList.add(isHint ? "cell-hint" : "cell-hidden");
    }

    function handleClick(r, c){
        if (gameOver) return;
        if(flagMode) sendAction("flag", r, c);
        else sendAction("reveal", r, c);
    }
    
    function handleRightClick(r, c){
        if (gameOver) return;
        sendAction("flag", r, c);
    }

    async function sendAction(action, row, col){
        const fd = new FormData();
        fd.append("action", action);
        fd.append("row", row);
        fd.append("col", col);
        const res  = await fetch(`/game/${game_id}/action`, {method: "POST", body: fd});
        const data = await res.json();
        applyUpdate(data);
    }

    function applyUpdate(data){
        if(!timerStart && data.status !== "lost") timerStart = Date.now();

        if(data.board) renderBoard(data.board);

        if(data.flags_remaining !== undefined){
            const mine_ct = document.getElementById("mine-count");
            if(mine_ct) mine_ct.textContent = data.flags_remaining;
        }

        if(data.hint_cell){
            hintCell = data.hint_cell;
            const [hr, hc] = hintCell;
            paintCell({ r: hr, c: hc, state: "hidden" });
            setTimeout(() => {
                hintCell = null;
                paintCell({ r: hr, c: hc, state: "hidden" });
            }, 5000);
        }

        if(data.status === "won"){
            gameOver = true;
            showOverlay("🏆", "You won!");
        }
        else if(data.status === "lost"){
            gameOver = true;
            showOverlay("💥", "BOOM!", "You hit a mine.");
        }
    }

    tickInterval = setInterval(async () => {
        if(gameOver || !document.getElementById("board")){
            clearInterval(tickInterval);
            return;
        }
        const res  = await fetch(`/game/${game_id}/tick`, { method: "POST" });
        const data = await res.json();
        if (data.board) renderBoard(data.board);
    }, 2000);

    document.body.removeEventListener("boardUpdate", window._boardUpdateHandler);
    window._boardUpdateHandler = e => applyUpdate(e.detail);
    document.body.addEventListener("boardUpdate", window._boardUpdateHandler);

    function showOverlay(icon, title, msg) {
        const over = document.getElementById("overlay");
        if (!over) return;
        document.getElementById("overlay-icon").textContent = icon;
        document.getElementById("overlay-title").textContent = title;
        document.getElementById("overlay-msg").textContent = msg;
        over.classList.remove("hidden");
    }

    renderBoard(
        Array.from({ length: rows }, (_, r) =>
            Array.from({ length: cols }, (_, c) => ({ r, c, state: "hidden" })))
    );
}