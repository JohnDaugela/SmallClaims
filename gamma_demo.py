#!/usr/bin/env python3
"""
GAMMA Presentation Demo - Test basic automation
Opens a GAMMA presentation and clicks through it
"""

import time
from playwright.sync_api import sync_playwright

def demo_gamma_presentation(gamma_url, num_clicks=5):
    """
    Open a GAMMA presentation and click through it

    Args:
        gamma_url: URL to the GAMMA presentation
        num_clicks: Number of spacebar presses to demo
    """
    with sync_playwright() as p:
        # Launch browser (use headless=False to see what's happening)
        print("🚀 Launching browser...")
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Navigate to GAMMA presentation
        print(f"📂 Opening GAMMA presentation: {gamma_url}")
        page.goto(gamma_url)

        # Wait for page to load
        time.sleep(3)

        # Press 'S' for spotlight mode
        print("💡 Pressing 'S' for spotlight mode...")
        page.keyboard.press('s')
        time.sleep(1)

        # Press F11 for fullscreen (might not work in all browsers/OS)
        print("🖥️  Attempting fullscreen (F11)...")
        page.keyboard.press('F11')
        time.sleep(1)

        # Click through presentation
        print(f"\n▶️  Clicking through {num_clicks} times...\n")
        for i in range(num_clicks):
            print(f"   Click {i+1}: Pressing SPACEBAR")
            page.keyboard.press('Space')
            time.sleep(2)  # Wait 2 seconds between clicks so you can see the changes

            # Take a screenshot for debugging
            screenshot_path = f"/home/user/SmallClaims/screenshot_{i+1}.png"
            page.screenshot(path=screenshot_path)
            print(f"   📸 Screenshot saved: {screenshot_path}")

        print("\n✅ Demo complete! Browser will stay open for 10 seconds...")
        time.sleep(10)

        browser.close()
        print("👋 Browser closed.")

if __name__ == "__main__":
    # Your GAMMA presentation URL
    GAMMA_URL = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc"

    print("=" * 60)
    print("GAMMA Presentation Automation - Demo")
    print("=" * 60)
    print()

    demo_gamma_presentation(GAMMA_URL, num_clicks=5)
