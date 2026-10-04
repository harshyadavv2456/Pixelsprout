      if (k === "Escape") { mode = "title"; return; }
      if (k === "?" || k === "h" || k === "H") { mode = "help"; return; }
      if (k === "ArrowLeft" || k === "a" || k === "A") { ev.preventDefault(); useKey = true; keyCol = (keyCol + COLS - 1) % COLS; return; }
      if (k === "ArrowRight" || k === "d" || k === "D") { ev.preventDefault(); useKey = true; keyCol = (keyCol + 1) % COLS; return; }
      if (k === "ArrowDown" || k === "Enter" || k === " ") { ev.preventDefault(); useKey = true; drop(keyCol); return; }
      if (k >= "1" && k <= "6") { useKey = true; keyCol = parseInt(k, 10) - 1; drop(keyCol); }
    }

    function resize() {
      var rect = canvas.getBoundingClientRect();
      dpr = Math.min(2, window.devicePixelRatio || 1);
      cssW = Math.max(280, rect.width || 360);
      cssH = Math.max(320, rect.height || 640);
      canvas.width = Math.round(cssW * dpr);
      canvas.height = Math.round(cssH * dpr);
    }

    function frame(now) {
      if (dead) return;
      if (!last) last = now;
      var dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      update(dt);
      draw();
      raf = requestAnimationFrame(frame);
    }

    canvas.style.touchAction = "none";
    canvas.addEventListener("pointerdown", pointerDown);
    canvas.addEventListener("pointermove", pointerMove);
    window.addEventListener("keydown", keydown);
    var ro = new ResizeObserver(resize);
    ro.observe(canvas.parentElement || canvas);
    resize();
    raf = requestAnimationFrame(frame);

    var api = {
      destroy: function () {
        dead = true;
        cancelAnimationFrame(raf);
        canvas.removeEventListener("pointerdown", pointerDown);
        canvas.removeEventListener("pointermove", pointerMove);
        window.removeEventListener("keydown", keydown);
        ro.disconnect();
        delete canvas.__moonbloom;
      }
    };
    canvas.__moonbloom = api;
    return api;
  }

  window.Moonbloom = { mount: mount };
})();
