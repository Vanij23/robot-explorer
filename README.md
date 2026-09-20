# Robot Explorer — Browser ↔ Local Python Bridge

**Proxie DevOps Assignment — Round 1**

Bridges a hosted, purely static copy of `index.html` (the Three.js Robot
Explorer) to a local Python process, in real time, in both directions —
without turning the hosting into a real backend.

**Live hosted app:** https://robot-explorer-umber.vercel.app/

## What it does

- **Read**: streams the robot's live `x`, `z`, and `rotationY` out of the
  running page as it's emitted — every animation frame, pushed straight into
  Python. Not polling, not a screenshot scrape.
- **Write**: sends a command from Python back into the live tab that drives
  the robot forward on its own — proving control works in both directions.

## How it works

The bridge uses **Playwright**, a Python library that drives a real Chrome/
Chromium browser over the **Chrome DevTools Protocol (CDP)** — the same
protocol powering Chrome's own DevTools panel.

1. `page.expose_function("onRobotState", ...)` creates a real JavaScript
   function inside the page's own context. Calling it from JS hops straight
   back into a Python callback (CDP's `Runtime.addBinding` under the hood).
2. A tiny injected script (`page.add_init_script`) re-wires the app's
   *existing* broadcast — `window.postMessage({ type: "robot-state", ... })`
   — straight into that exposed function. This means one push per animation
   frame, no polling loop guessing when something changed.
3. To control the robot, Python calls `page.evaluate(...)`, which runs
   `window.postMessage({ type: "robot-command", ... })` inside the live
   page — the exact same hook a keyboard handler would use.

The hosted page (`index.html`) itself is never modified and never gets a
backend. It's served as plain static files by Vercel; the bridge lives
entirely outside it, observing and controlling the tab from the outside.

## Project setup (what was actually built)

- Wrote and ran everything in **VS Code**, using its built-in terminal.
- Created a Python **virtual environment** (`venv`) to keep this project's
  dependencies isolated from the rest of the machine.
- Installed **Playwright** (`pip install playwright`) plus its managed
  Chromium browser (`playwright install chromium`).
- Verified the bridge first against `index.html` served locally
  (`python -m http.server 8000`), confirming both the read stream and the
  write commands worked before touching real hosting.
- Pushed `index.html` to a **GitHub** repository, then connected that repo
  to **Vercel** for a one-click static deploy — no server, no build step,
  just the static file being served publicly.
- Re-pointed the bridge at the live Vercel URL and re-ran it, confirming the
  exact same read/write behavior against the real public internet, not
  `localhost`.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

## Running it

```bash
python bridge.py
```

`bridge.py` is already pointed at the live hosted URL:
```python
URL = "https://robot-explorer-umber.vercel.app/"
```

On running, a Chromium window opens showing the hosted robot page, and the
terminal starts printing the live state stream:
