#!/usr/bin/env python3
"""
=============================================================================
GAMMA AUTO PRESENTER - Standalone Version
=============================================================================

WHAT THIS DOES:
- Automatically controls your GAMMA presentation
- Presses 'Ctrl+Shift+Enter' to enter presentation mode
- Presses 'S' for spotlight mode
- Presses spacebar at regular intervals to advance slides

SETUP (One-time only):
1. Open Command Prompt (Windows key + R, type 'cmd', press Enter)
2. Type: pip install pyautogui
3. Press Enter and wait for it to finish
4. Close Command Prompt

HOW TO USE:
1. Open your GAMMA presentation in a web browser
2. Double-click this file to run it
3. Follow the on-screen instructions
4. Switch to your browser window when prompted
5. Watch the automation!

GAMMA PRESENTATION URL:
https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc

=============================================================================
"""

import time
import sys

# Check if pyautogui is installed
try:
    import pyautogui
except ImportError:
    print("\n" + "="*70)
    print("ERROR: PyAutoGUI is not installed!")
    print("="*70)
    print("\nTo install it:")
    print("1. Open Command Prompt (Windows key + R, type 'cmd', press Enter)")
    print("2. Type: pip install pyautogui")
    print("3. Press Enter and wait for installation to complete")
    print("4. Run this script again")
    print("\n" + "="*70)
    input("\nPress Enter to exit...")
    sys.exit(1)

# Configuration
GAMMA_URL = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc"
NUMBER_OF_CLICKS = 15  # How many times to press spacebar
SECONDS_BETWEEN_CLICKS = 3  # How long to wait between each spacebar press
COUNTDOWN_SECONDS = 5  # How long you have to switch to the browser

def print_header():
    """Print a nice header"""
    print("\n" + "="*70)
    print(" "*20 + "GAMMA AUTO PRESENTER")
    print("="*70)

def print_instructions():
    """Print usage instructions"""
    print("\n📋 INSTRUCTIONS:")
    print("-" * 70)
    print("1. Open your GAMMA presentation in a web browser:")
    print(f"   {GAMMA_URL}")
    print()
    print("2. Make sure the presentation is visible on your screen")
    print()
    print("3. When ready, press Enter below")
    print()
    print("4. You'll have 5 seconds to click on the browser window")
    print()
    print("5. The automation will then:")
    print("   • Press 'Ctrl+Shift+Enter' to enter presentation mode")
    print("   • Press 'S' to enter spotlight mode")
    print("   • Press spacebar every 3 seconds to advance")
    print("-" * 70)

def countdown(seconds):
    """Countdown timer to give user time to switch windows"""
    print(f"\n⏰ QUICK! Click on your browser window NOW!")
    print(f"   Starting in {seconds} seconds...")
    print()
    for i in range(seconds, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    print("   🚀 GO!\n")

def run_automation():
    """Run the GAMMA presentation automation"""

    # Give user time to switch to browser
    countdown(COUNTDOWN_SECONDS)

    # Press Ctrl+Shift+Enter for presentation mode
    print("🎬 Pressing 'Ctrl+Shift+Enter' to enter presentation mode...")
    pyautogui.hotkey('ctrl', 'shift', 'enter')
    time.sleep(2.5)  # Give it time to load presentation mode

    # Press 'S' for spotlight mode
    print("💡 Pressing 'S' for spotlight mode...")
    pyautogui.press('s')
    time.sleep(2.5)  # Give it time to load spotlight mode

    # Click through presentation
    print(f"\n▶️  Now clicking through presentation...")
    print(f"   ({NUMBER_OF_CLICKS} clicks, {SECONDS_BETWEEN_CLICKS} seconds apart)")
    print()

    for i in range(NUMBER_OF_CLICKS):
        click_num = i + 1
        print(f"   Click {click_num}/{NUMBER_OF_CLICKS}: SPACEBAR")
        pyautogui.press('space')
        time.sleep(SECONDS_BETWEEN_CLICKS)

    print("\n✅ AUTOMATION COMPLETE!")
    print()
    print("To exit:")
    print("   • Press ESC to exit presentation mode")
    print("   • Press 'S' again to exit spotlight mode (if needed)")

def main():
    """Main function"""
    print_header()
    print_instructions()

    # Wait for user to be ready
    input("\n👉 Press ENTER when your browser is open and ready...")

    # Run the automation
    try:
        run_automation()
    except KeyboardInterrupt:
        print("\n\n⚠️  Automation stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\n❌ Error occurred: {e}")

    print("\n" + "="*70)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
