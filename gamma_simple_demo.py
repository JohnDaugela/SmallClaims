#!/usr/bin/env python3
"""
GAMMA Presentation Demo - Simple Keyboard Control
Uses PyAutoGUI to send keyboard commands to the active window

USAGE:
1. Open your GAMMA presentation in a browser
2. Run this script
3. Click on the browser window to focus it
4. Watch the automation happen!
"""

import time
import pyautogui

def countdown(seconds=5):
    """Give user time to focus on the browser window"""
    print(f"\n⏰ You have {seconds} seconds to focus on your GAMMA browser window...")
    for i in range(seconds, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    print("   GO! 🚀\n")

def demo_gamma_clicks(num_clicks=5, delay_between_clicks=2):
    """
    Automate GAMMA presentation by sending keyboard commands

    Args:
        num_clicks: Number of spacebar presses
        delay_between_clicks: Seconds to wait between clicks
    """
    # Countdown so user can focus browser
    countdown(5)

    # Press 'S' for spotlight mode
    print("💡 Pressing 'S' for spotlight mode...")
    pyautogui.press('s')
    time.sleep(1)

    # Press F11 for fullscreen
    print("🖥️  Pressing 'F11' for fullscreen...")
    pyautogui.press('f11')
    time.sleep(1)

    # Click through presentation
    print(f"\n▶️  Clicking through presentation ({num_clicks} times)...\n")
    for i in range(num_clicks):
        print(f"   Press {i+1}: SPACEBAR")
        pyautogui.press('space')
        time.sleep(delay_between_clicks)

    print("\n✅ Demo complete!")
    print("   Press ESC to exit fullscreen mode")
    print("   Press S again to exit spotlight mode")

if __name__ == "__main__":
    print("=" * 60)
    print("GAMMA Presentation Automation - Simple Demo")
    print("=" * 60)
    print()
    print("📋 INSTRUCTIONS:")
    print("   1. Open this URL in your browser:")
    print("      https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc")
    print("   2. When ready, click on the browser window")
    print()

    input("Press ENTER when your browser window is ready...")

    demo_gamma_clicks(num_clicks=10, delay_between_clicks=2)
