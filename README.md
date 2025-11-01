# GAMMA Auto Presenter Demo

Two demo approaches to automatically control GAMMA presentations:

## Option 1: Simple Keyboard Control (Recommended for quick testing)

**File:** `gamma_simple_demo.py`

This uses PyAutoGUI to send keyboard commands to whatever window is focused.

### Setup:
```bash
pip install pyautogui
```

### Run:
```bash
python gamma_simple_demo.py
```

### How it works:
1. Manually open your GAMMA presentation in a browser
2. Run the script
3. Press ENTER when prompted
4. Click on the browser window to focus it within 5 seconds
5. Watch it automatically:
   - Press 'S' for spotlight mode
   - Press 'F11' for fullscreen
   - Press SPACEBAR 10 times (2 seconds apart)

**Pros:** Simple, works immediately, no browser driver needed
**Cons:** Must manually open browser, can't capture screenshots or detect changes

---

## Option 2: Full Browser Automation (Advanced)

**File:** `gamma_demo.py`

This uses Playwright to fully control a browser programmatically.

### Setup:
```bash
pip install playwright
playwright install chromium
```

### Run:
```bash
python gamma_demo.py
```

### How it works:
1. Automatically opens the GAMMA presentation
2. Takes screenshots after each click
3. Can detect what changed between clicks
4. More reliable for complex automation

**Pros:** Full control, can detect changes, take screenshots
**Cons:** Requires browser drivers, more complex setup

---

## Testing

Start with **Option 1** to verify basic functionality:
- Does spotlight mode work?
- Does spacebar advance slides/points correctly?
- How many spacebar presses does your full presentation need?

Then move to **Option 2** for the full automation system.
