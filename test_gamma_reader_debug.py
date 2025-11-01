#!/usr/bin/env python3
"""
GAMMA Reader - DEBUG VERSION
Shows exactly what's happening at each step
"""

import time
import json
from playwright.sync_api import sync_playwright

def test_gamma_reading():
    GAMMA_URL = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc"

    print("="*70)
    print("GAMMA PRESENTATION READER - DEBUG MODE")
    print("="*70)
    print(f"\nOpening: {GAMMA_URL}\n")

    with sync_playwright() as p:
        # Launch browser maximized
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        # Open GAMMA
        print("[1] Opening GAMMA presentation...")
        page.goto(GAMMA_URL)

        print("[2] Waiting 5 seconds for page to load...")
        time.sleep(5)

        # Take screenshot of initial state
        page.screenshot(path='debug_01_initial.png')
        print("    Screenshot saved: debug_01_initial.png")

        print("[3] Waiting 2 more seconds...")
        time.sleep(2)

        # Try presentation mode - attempt multiple methods
        print("[4] Attempting to enter presentation mode...")
        print("    Method 1: Ctrl+Shift+Enter")
        page.keyboard.down('Control')
        page.keyboard.down('Shift')
        page.keyboard.press('Enter')
        page.keyboard.up('Shift')
        page.keyboard.up('Control')

        print("[5] Waiting 5 seconds for presentation mode...")
        time.sleep(5)

        # Take screenshot after presentation mode
        page.screenshot(path='debug_02_after_presentation.png')
        print("    Screenshot saved: debug_02_after_presentation.png")

        # Enter spotlight mode
        print("[6] Pressing 'S' for spotlight mode...")
        page.keyboard.press('s')

        print("[7] Waiting 3 seconds for spotlight mode...")
        time.sleep(3)

        # Take screenshot after spotlight
        page.screenshot(path='debug_03_after_spotlight.png')
        print("    Screenshot saved: debug_03_after_spotlight.png")

        print("\n" + "="*70)
        print("READING SLIDES")
        print("="*70 + "\n")

        slides_found = []
        previous_text = ""

        for i in range(50):
            slide_num = i + 1

            print(f"\n[SLIDE {slide_num}]")

            # Read current slide text
            current_text = page.evaluate("""() => {
                return document.body.innerText;
            }""")

            # Save text to file for inspection
            with open(f'debug_slide_{slide_num:02d}_text.txt', 'w', encoding='utf-8') as f:
                f.write(current_text)

            print(f"  Text length: {len(current_text)} characters")
            print(f"  Saved to: debug_slide_{slide_num:02d}_text.txt")

            # Take screenshot
            screenshot_file = f'debug_slide_{slide_num:02d}.png'
            page.screenshot(path=screenshot_file)
            print(f"  Screenshot: {screenshot_file}")

            # Check if content changed
            if current_text == previous_text and i > 0:
                print(f"\n  ⚠️ TEXT IS IDENTICAL TO PREVIOUS SLIDE!")
                print(f"  This means either:")
                print(f"    - We've reached the end")
                print(f"    - Spacebar isn't working")
                print(f"    - We're not in presentation mode")
                print(f"\n  Total slides detected: {slide_num - 1}")
                break

            # Show preview
            preview = current_text[:150].replace('\n', ' ').strip()
            print(f"  Preview: {preview}...")

            slides_found.append({
                'number': slide_num,
                'text': current_text,
                'preview': preview
            })

            # Press spacebar
            print(f"  Pressing SPACEBAR...")
            page.keyboard.press('Space')

            print(f"  Waiting 1.5 seconds...")
            time.sleep(1.5)

            previous_text = current_text

        print("\n" + "="*70)
        print(f"COMPLETE - Found {len(slides_found)} slides")
        print("="*70)

        # Save results
        with open('debug_results.json', 'w', encoding='utf-8') as f:
            json.dump(slides_found, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Results saved to: debug_results.json")
        print(f"📸 Check the debug_*.png screenshots to see what happened")
        print(f"📄 Check the debug_slide_*_text.txt files to see what text was read")

        print("\n" + "="*70)
        print("INSTRUCTIONS FOR DEBUGGING:")
        print("="*70)
        print("1. Look at debug_01_initial.png - is the page loaded?")
        print("2. Look at debug_02_after_presentation.png - did presentation mode start?")
        print("3. Look at debug_03_after_spotlight.png - is it in spotlight mode?")
        print("4. Compare debug_slide_01.png and debug_slide_02.png - did it advance?")
        print("5. Read debug_slide_01_text.txt - what text is being captured?")

        print("\nBrowser will stay open for 10 seconds so you can see the final state...")
        time.sleep(10)

        browser.close()

if __name__ == "__main__":
    try:
        from playwright.sync_api import sync_playwright
        test_gamma_reading()
    except ImportError:
        print("\nERROR: Playwright not installed!")
        print("\nPlease run:")
        print("  pip install playwright")
        print("  playwright install chromium")
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
