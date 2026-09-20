
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

x=18.17 z=24.24 yaw=-1.11


A few seconds in, Python sends a drive-forward command on its own — the
robot visibly moves without the keyboard being touched, and the terminal
prints confirmation once done.

## Why this mechanism

- **vs. a Chrome extension + native messaging**: an extension needs to be
  installed, granted host permissions on the specific hosted origin, and
  paired with a native-messaging host just to get bytes to Python. CDP gets
  the same push-based access with one Python script and no packaged
  browser add-on.
- **vs. hand-rolling raw CDP over `websockets`**: Playwright *is* CDP under
  the hood — it just handles the connection/lifecycle boilerplate, so the
  bridge code stays short and easy to read.
- **vs. a self-hosted WebSocket relay**: that approach needs a script added
  *inside* the hosted page to open the socket — a change to the "static"
  deliverable on every redeploy. This bridge needs zero changes to
  `index.html` or the hosting itself.

## Trade-offs, honestly

- **Latency**: the exposed-function round trip through CDP is a few
  milliseconds — well under one render frame at 60fps, comfortably inside
  the "sub-second" real-time bar.
- **Security / permissions**: this is real browser automation — Python has
  full read/write access to whatever tab it's attached to (DOM, JS,
  network). That's the right level of access for this task, but not
  something to point at a tab with untrusted content or a logged-in session
  you don't control.
- **Dependency weight**: needs a real Chromium binary locally
  (`playwright install chromium`, a couple hundred MB) — heavier than a bare
  WebSocket client, in exchange for needing zero changes to the hosted page.
- **Tab lifetime**: like any CDP-based approach, if the tab closes or
  navigates away, the bridge session ends and needs reattaching.

  <img width="1917" height="1078" alt="Screenshot 2026-09-20 163142" src="https://github.com/user-attachments/assets/8ced38cc-e44e-44ef-ae9f-aab4d26f5f67" />
  <img width="1917" height="1078" alt="Screenshot 2026-09-20 162950" src="https://github.com/user-attachments/assets/1015d57a-e70a-4304-b144-cee3b8539c84" />
<img width="1917" height="1078" alt="Screenshot 2026-09-20 163159" src="https://github.com/user-attachments/assets/8a8a247d-d684-43e6-8e38-a565936c7329" />
<img width="1917" height="1078" alt="Screenshot 2026-09-20 163247" src="https://github.com/user-attachments/assets/58884cc2-fcae-42de-b6e5-ae985dcce31e" />
<img width="1917" height="1078" alt="Screenshot 2026-09-20 162922" src="https://github.com/user-attachments/assets/6f2c2468-0964-43f2-b7ae-0c8fea96bb07" />
