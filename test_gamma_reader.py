#!/usr/bin/env python3
"""
Simple GAMMA Reader Test
Just reads through your GAMMA presentation and shows what's on each slide
"""

import time
import json
from playwright.sync_api import sync_playwright

def test_gamma_reading():
    GAMMA_URL = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc"

    print("="*70)
    print("GAMMA PRESENTATION READER TEST")
    print("="*70)
    print(f"\nOpening: {GAMMA_URL}\n")

    with sync_playwright() as p:
        # Launch browser with maximized window
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        # Open GAMMA
        print("Opening GAMMA presentation...")
        page.goto(GAMMA_URL)

        print("Waiting for presentation to load (5 seconds)...")
        time.sleep(5)

        print("Window is maximized. Waiting 2 seconds...")
        time.sleep(2)

        # Enter presentation mode
        print("Pressing Ctrl+Shift+Enter for presentation mode...")
        page.keyboard.press('Control+Shift+Enter')

        print("Waiting 5 seconds for presentation mode to load...")
        time.sleep(5)

        # Enter spotlight mode
        print("Pressing 'S' for spotlight mode...")
        page.keyboard.press('s')

        print("Waiting 3 seconds for spotlight mode to load...\n")
        time.sleep(3)

        print("="*70)
        print("READING SLIDES")
        print("="*70 + "\n")

        slides_found = []
        previous_text = ""

        for i in range(50):  # Max 50 slides
            slide_num = i + 1

            # Read current slide text from DOM
            current_text = page.evaluate("""() => {
                return document.body.innerText;
            }""")

            # Check if content changed
            if current_text == previous_text and i > 0:
                print(f"\nNo change detected - reached end!")
                print(f"Total slides: {slide_num - 1}")
                break

            # Show what we found
            preview = current_text[:100].replace('\n', ' ').strip()
            print(f"Slide {slide_num}: {preview}...")

            slides_found.append({
                'number': slide_num,
                'text': current_text,
                'preview': preview
            })

            # Advance to next slide
            page.keyboard.press('Space')
            time.sleep(1.5)

            previous_text = current_text

        print("\n" + "="*70)
        print(f"COMPLETE - Found {len(slides_found)} slides")
        print("="*70)

        # Save results
        with open('gamma_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(slides_found, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: gamma_test_results.json")
        print("\nBrowser will close in 5 seconds...")
        time.sleep(5)

        browser.close()

if __name__ == "__main__":
    # Check if playwright is installed
    try:
        from playwright.sync_api import sync_playwright
        test_gamma_reading()
    except ImportError:
        print("\nERROR: Playwright not installed!")
        print("\nPlease run these commands first:")
        print("  pip install playwright")
        print("  playwright install chromium")
        input("\nPress Enter to exit...")
