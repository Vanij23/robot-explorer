import time
from playwright.sync_api import sync_playwright

# CHANGE THIS to your hosted URL once it's live (e.g. GitHub Pages / Netlify link)
URL = "http://localhost:8000/index.html"

frame_count = 0

def on_robot_state(state):
    global frame_count
    frame_count += 1
    if frame_count % 30 == 0:  # only print ~2x/sec so it's readable
        print(f"x={state['x']:.2f}  z={state['z']:.2f}  yaw={state['rotationY']:.2f}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Expose a Python function that the page's JS can call directly
    page.expose_function("onRobotState", on_robot_state)

    # Inject a tiny listener that re-broadcasts the page's existing
    # postMessage("robot-state") events straight into our Python function
    page.add_init_script("""
        window.addEventListener("message", (e) => {
            if (e.source !== window || e.data?.type !== "robot-state") return;
            window.onRobotState(e.data);
        });
    """)

    page.goto(URL)
    print("Connected! Streaming live robot state below.")
    print("(Try driving with WASD in the browser window right now.)\n")

    time.sleep(4)  # give you a few seconds to manually drive it first

    print("\n>>> Now Python is going to drive the robot forward for 2 seconds...")
    page.evaluate("""() => window.postMessage({type:"robot-command", forward:true, run:true}, "*")""")
    time.sleep(2)
    page.evaluate("""() => window.postMessage({type:"robot-command", forward:false}, "*")""")
    print(">>> Done driving. Robot should have moved forward on its own.\n")

    input("Press Enter to close the browser...")
    browser.close()