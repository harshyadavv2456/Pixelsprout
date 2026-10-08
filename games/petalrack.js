(function () {
  var COLS = 8, ROWS = 8;
  var SHAPES = [
    [[0, 0]],
    [[0, 0], [1, 0]],
    [[0, 0], [0, 1]],
    [[0, 0], [1, 0], [2, 0]],
    [[0, 0], [0, 1], [0, 2]],
    [[0, 0], [1, 0], [0, 1]],
    [[0, 0], [1, 0], [1, 1]],
    [[0, 0], [1, 0], [2, 0], [1, 1]],
    [[0, 0], [1, 0], [2, 0], [2, 1]],
    [[0, 0], [1, 0], [2, 0], [3, 0]],
    [[0, 0], [0, 1], [1, 1], [2, 1]],
    [[0, 0], [1, 0], [1, 1], [2, 1]],
    [[0, 1], [1, 0], [1, 1], [1, 2]]
  ];
  var COLORS = ["#f28ab0", "#f6c15b", "#8fd18a", "#c4b0f2", "#7ec8d6"];

  function rand(n) { return Math.floor(Math.random() * n); }
  function piece() {
    var cells = SHAPES[rand(SHAPES.length)];
    return { cells: cells, color: COLORS[rand(COLORS.length)] };
  }
  function bounds(cells) {
    var w = 0, h = 0, i;
    for (i = 0; i < cells.length; i++) {
      if (cells[i][0] + 1 > w) w = cells[i][0] + 1;
      if (cells[i][1] + 1 > h) h = cells[i][1] + 1;
    }
    return { w: w, h: h };
  }
  function fits(board, p, c, r) {
    var i, x, y;
    for (i = 0; i < p.cells.length; i++) {
      x = c + p.cells[i][0];
      y = r + p.cells[i][1];
      if (x < 0 || y < 0 || x >= COLS || y >= ROWS || board[y][x]) return false;
    }
    return true;
  }
  function anyFit(board, p) {
    var b = bounds(p.cells), c, r;
    for (r = 0; r <= ROWS - b.h; r++) {
      for (c = 0; c <= COLS - b.w; c++) if (fits(board, p, c, r)) return true;
    }
    return false;
  }

  function mount(canvas) {
    var ctx = canvas.getContext("2d");
    var dpr = 1;
    var state = "title";
    var board, tray, selected, score, best, combo, hover, msg;
    best = parseInt(localStorage.getItem("petalrack-best") || "0", 10) || 0;

    function empty() {
      var b = [], y, x;
      for (y = 0; y < ROWS; y++) {
        b[y] = [];
        for (x = 0; x < COLS; x++) b[y][x] = null;
      }
      return b;
    }
    function reset() {
      board = empty();
      tray = [piece(), piece(), piece()];
      selected = 0;
      score = 0;
      combo = 0;
      hover = null;
      msg = "";
      state = "play";
    }
    function layout() {
      var rect = canvas.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(280, rect.width) * dpr;
      canvas.height = Math.max(420, rect.height) * dpr;
    }
    function cellSize() {
      var pad = 18 * dpr;
      var top = 78 * dpr;
      var bot = 118 * dpr;
      var w = canvas.width - pad * 2;
      var h = canvas.height - top - bot;
      return Math.min(w / COLS, h / ROWS);
    }
    function origin() {
      var s = cellSize();
      var padTop = 78 * dpr;
      var gridW = s * COLS;
      return { x: (canvas.width - gridW) / 2, y: padTop, s: s };
    }
    function place(p, c, r) {
      var i, x, y, cleared = 0, rows = [], cols = [], k;
      if (!fits(board, p, c, r)) return false;
      for (i = 0; i < p.cells.length; i++) {
        board[r + p.cells[i][1]][c + p.cells[i][0]] = p.color;
      }
      score += p.cells.length * 4;
      for (y = 0; y < ROWS; y++) {
        var full = true;
        for (x = 0; x < COLS; x++) if (!board[y][x]) full = false;
        if (full) rows.push(y);
      }
      for (x = 0; x < COLS; x++) {
        var fullc = true;
        for (y = 0; y < ROWS; y++) if (!board[y][x]) fullc = false;
        if (fullc) cols.push(x);
      }
      cleared = rows.length + cols.length;
      if (cleared) {
        combo += 1;
        score += cleared * 50 * combo;
        for (k = 0; k < rows.length; k++) for (x = 0; x < COLS; x++) board[rows[k]][x] = null;
        for (k = 0; k < cols.length; k++) for (y = 0; y < ROWS; y++) board[y][cols[k]] = null;
        msg = cleared > 1 ? "Harvest x" + cleared : "Harvest";
      } else {
        combo = 0;
        msg = "";
      }
      tray[selected] = null;
      var left = false;
      for (i = 0; i < tray.length; i++) if (tray[i]) left = true;
      if (!left) tray = [piece(), piece(), piece()];
      selected = 0;
      while (selected < 3 && !tray[selected]) selected++;
      if (selected > 2) selected = 0;
      var can = false;
      for (i = 0; i < tray.length; i++) if (tray[i] && anyFit(board, tray[i])) can = true;
      if (!can) {
        state = "over";
        if (score > best) {
          best = score;
          localStorage.setItem("petalrack-best", String(best));
        }
      }
      return true;
    }
    function blossom(x, y, s, color) {
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, s * 0.34, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "rgba(255,236,180,0.9)";
      ctx.beginPath();
      ctx.arc(x, y, s * 0.12, 0, Math.PI * 2);
      ctx.fill();
    }
    function drawPiece(p, x, y, s, alpha) {
      var i;
      ctx.globalAlpha = alpha;
      for (i = 0; i < p.cells.length; i++) {
        var cx = x + p.cells[i][0] * s + s / 2;
        var cy = y + p.cells[i][1] * s + s / 2;
        blossom(cx, cy, s, p.color);
      }
      ctx.globalAlpha = 1;
    }
    function draw() {
      var o = origin();
      var s = o.s;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      var g = ctx.createLinearGradient(0, 0, 0, canvas.height);
      g.addColorStop(0, "#14201a");
      g.addColorStop(1, "#0c1410");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#f6e7c4";
      ctx.font = "bold " + Math.round(22 * dpr) + "px Inter, sans-serif";
      ctx.fillText("Petalrack", 16 * dpr, 32 * dpr);
      ctx.font = Math.round(14 * dpr) + "px Inter, sans-serif";
      ctx.fillStyle = "#d7c49a";
      ctx.fillText("Score " + score + "   Best " + best, 16 * dpr, 54 * dpr);
      if (msg) {
        ctx.fillStyle = "#f6c15b";
        ctx.fillText(msg, canvas.width - 120 * dpr, 54 * dpr);
      }
      var x, y;
      for (y = 0; y < ROWS; y++) {
        for (x = 0; x < COLS; x++) {
          ctx.fillStyle = (x + y) % 2 ? "#243028" : "#1c2820";
          ctx.fillRect(o.x + x * s + 1, o.y + y * s + 1, s - 2, s - 2);
          if (board && board[y][x]) blossom(o.x + x * s + s / 2, o.y + y * s + s / 2, s, board[y][x]);
        }
      }
      if (state === "play" && hover && tray[selected] && fits(board, tray[selected], hover.c, hover.r)) {
        drawPiece(tray[selected], o.x + hover.c * s, o.y + hover.r * s, s, 0.45);
      }
      var trayY = o.y + ROWS * s + 16 * dpr;
      var i;
      for (i = 0; i < 3; i++) {
        var tx = 24 * dpr + i * (canvas.width / 3.3);
        if (i === selected && state === "play") {
          ctx.strokeStyle = "#f6c15b";
          ctx.lineWidth = 2;
          ctx.strokeRect(tx - 6, trayY - 6, 92 * dpr, 70 * dpr);
        }
        if (tray && tray[i]) drawPiece(tray[i], tx, trayY, Math.min(22 * dpr, s * 0.55), 1);
      }
      if (state !== "play") {
        ctx.fillStyle = "rgba(8,12,10,0.72)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#fff4d6";
        ctx.font = "bold " + Math.round(32 * dpr) + "px Inter, sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(state === "title" ? "Petalrack" : "Bed full", canvas.width / 2, canvas.height * 0.4);
        ctx.font = Math.round(16 * dpr) + "px Inter, sans-serif";
        ctx.fillStyle = "#e7d7b0";
        var line = state === "title" ? "Place blossoms. Fill a row or column to harvest." : "Score " + score + "   Best " + best;
        ctx.fillText(line, canvas.width / 2, canvas.height * 0.48);
        ctx.fillStyle = "#f6c15b";
        ctx.fillText("Tap, Space, or Enter", canvas.width / 2, canvas.height * 0.58);
        ctx.textAlign = "left";
      }
    }
    function pointerCell(ev) {
      var rect = canvas.getBoundingClientRect();
      var x = (ev.clientX - rect.left) * (canvas.width / rect.width);
      var y = (ev.clientY - rect.top) * (canvas.height / rect.height);
      var o = origin();
      return {
        x: x, y: y,
        c: Math.floor((x - o.x) / o.s),
        r: Math.floor((y - o.y) / o.s),
        trayY: o.y + ROWS * o.s
      };
    }
    function onPointer(ev) {
      if (state !== "play") {
        reset();
        draw();
        return;
      }
      var p = pointerCell(ev);
      if (p.y > p.trayY) {
        var slot = Math.floor((p.x / canvas.width) * 3);
        if (slot < 0) slot = 0;
        if (slot > 2) slot = 2;
        if (tray[slot]) selected = slot;
        draw();
        return;
      }
      if (p.c < 0 || p.r < 0 || p.c >= COLS || p.r >= ROWS) return;
      if (tray[selected]) place(tray[selected], p.c, p.r);
      draw();
    }
    function onMove(ev) {
      if (state !== "play") return;
      var p = pointerCell(ev);
      hover = { c: p.c, r: p.r };
      draw();
    }
    function onKey(ev) {
      var k = ev.key;
      if (k === " " || k === "Enter") {
        ev.preventDefault();
        if (state !== "play") reset();
        else if (hover && tray[selected]) place(tray[selected], hover.c, hover.r);
        draw();
        return;
      }
      if (state !== "play") return;
      if (k === "1" || k === "2" || k === "3") {
        var n = Number(k) - 1;
        if (tray[n]) selected = n;
      }
      if (k === "ArrowLeft" || k === "a" || k === "A") hover = { c: Math.max(0, (hover ? hover.c : 0) - 1), r: hover ? hover.r : 0 };
      if (k === "ArrowRight" || k === "d" || k === "D") hover = { c: Math.min(COLS - 1, (hover ? hover.c : 0) + 1), r: hover ? hover.r : 0 };
      if (k === "ArrowUp" || k === "w" || k === "W") hover = { c: hover ? hover.c : 0, r: Math.max(0, (hover ? hover.r : 0) - 1) };
      if (k === "ArrowDown" || k === "s" || k === "S") hover = { c: hover ? hover.c : 0, r: Math.min(ROWS - 1, (hover ? hover.r : 0) + 1) };
      if (k === "q" || k === "Q") { var i; for (i = selected - 1; i >= 0; i--) if (tray[i]) { selected = i; break; } }
      if (k === "e" || k === "E") { var j; for (j = selected + 1; j < 3; j++) if (tray[j]) { selected = j; break; } }
      draw();
    }
    layout();
    window.addEventListener("resize", function () { layout(); draw(); });
    canvas.addEventListener("pointerdown", onPointer);
    canvas.addEventListener("pointermove", onMove);
    window.addEventListener("keydown", onKey);
    draw();
  }
  window.Petalrack = { mount: mount };
})();
