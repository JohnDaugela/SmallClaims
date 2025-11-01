#!/usr/bin/env python3
"""
GAMMA COMPLETE AUTOMATION - Presentation + Spotlight + Fullscreen
Uses ?mode=present URL and clicks the actual buttons we found!
"""

import time
import json
from playwright.sync_api import sync_playwright

def run_gamma_automation():
    """Complete GAMMA automation with all modes activated"""

    gamma_url = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=present"

    print("="*70)
    print("GAMMA COMPLETE AUTOMATION")
    print("="*70)
    print(f"\nURL: {gamma_url}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        # Step 1: Open in presentation mode
        print("[1] Opening presentation (mode=present)...")
        page.goto(gamma_url)

        print("    Waiting 10 seconds for full load...")
        time.sleep(10)

        # Step 2: Click Spotlight button
        print("\n[2] Activating Spotlight mode...")
        print("    Looking for 'Spotlight' button...")

        try:
            # Click the button with text "Spotlight"
            spotlight_button = page.locator("button:has-text('Spotlight')").first
            spotlight_button.click()
            print("    ✅ Clicked Spotlight button!")
            time.sleep(3)
        except Exception as e:
            print(f"    ⚠️  Couldn't click Spotlight button: {e}")
            print("    Trying 'S' key as backup...")
            page.keyboard.press('s')
            time.sleep(3)

        # Step 3: Activate Fullscreen
        print("\n[3] Activating Fullscreen...")
        print("    Method 1: Clicking fullscreen button...")

        try:
            # Click button with aria-label "Enter full screen"
            fullscreen_button = page.locator("button[aria-label='Enter full screen']").first
            fullscreen_button.click()
            print("    ✅ Clicked fullscreen button!")
            time.sleep(3)
        except Exception as e:
            print(f"    ⚠️  Button click failed: {e}")
            print("    Method 2: Using JavaScript API...")
            try:
                page.evaluate("document.documentElement.requestFullscreen()")
                print("    ✅ Fullscreen activated via JavaScript!")
                time.sleep(3)
            except Exception as e2:
                print(f"    ⚠️  JavaScript also failed: {e2}")
                print("    (Note: 'F' key doesn't work for GAMMA fullscreen)")
                time.sleep(3)

        # Verify states
        print("\n[4] Verifying modes...")
        states = page.evaluate("""() => {
            return {
                isFullscreen: !!document.fullscreenElement,
                hasSpotlight: document.querySelector('.spotlight-active') !== null,
                bodyClasses: document.body.className
            };
        }""")

        print(f"    Fullscreen: {states['isFullscreen']}")
        print(f"    Spotlight active: {states['hasSpotlight']}")
        print(f"    Body classes: {states['bodyClasses']}")

        # Take screenshot
        page.screenshot(path='gamma_fully_automated.png')
        print("\n📸 Screenshot saved: gamma_fully_automated.png")

        # Step 4: Read slides
        print("\n[5] Reading all slides...")
        slides_data = page.evaluate("""() => {
            const cards = document.querySelectorAll('[data-card-id]');
            const slides = [];

            cards.forEach((card, index) => {
                const text = card.innerText.trim();
                if (text && text.length > 0) {
                    slides.push({
                        slide_number: index + 1,
                        card_id: card.getAttribute('data-card-id'),
                        text_content: text,
                        preview: text.substring(0, 80)
                    });
                }
            });

            return slides;
        }""")

        print(f"    ✅ Found {len(slides_data)} slides!\n")

        # Show first few slides
        for slide in slides_data[:5]:
            lines = slide['text_content'].split('\n')
            title = lines[0] if lines else ""
            print(f"    Slide {slide['slide_number']:2d}: {title[:50]}...")

        if len(slides_data) > 5:
            print(f"    ... and {len(slides_data) - 5} more slides")

        # Save data
        with open('gamma_automation_complete.json', 'w', encoding='utf-8') as f:
            json.dump({
                'url': gamma_url,
                'modes': states,
                'total_slides': len(slides_data),
                'slides': slides_data
            }, f, indent=2, ensure_ascii=False)

        print("\n💾 Data saved to: gamma_automation_complete.json")

        print("\n" + "="*70)
        print("✅ COMPLETE AUTOMATION SUCCESS!")
        print("="*70)
        print("\nModes activated:")
        print(f"  ✅ Presentation mode (?mode=present)")
        print(f"  {'✅' if states['hasSpotlight'] else '⚠️ '} Spotlight mode")
        print(f"  {'✅' if states['isFullscreen'] else '⚠️ '} Fullscreen mode")
        print(f"  ✅ Read {len(slides_data)} slides from HTML")

        print("\n🎯 READY FOR AUDIO AUTOMATION!")
        print("   Next step: Add your audio file and script for full sync")

        print("\nBrowser will stay open for 20 seconds...")
        print("You can manually:")
        print("  - Press SPACEBAR to advance slides")
        print("  - Press ESC to exit fullscreen")
        print("  - Press 'S' to toggle spotlight")

        time.sleep(20)

        browser.close()

        return slides_data


if __name__ == "__main__":
    try:
        from playwright.sync_api import sync_playwright
        slides = run_gamma_automation()

        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("\n✅ Part 1 COMPLETE - We can fully automate GAMMA!")
        print("\nTo add audio synchronization:")
        print("  1. Provide your voiceover script (.txt)")
        print("  2. Provide your audio file (.wav or .mp3)")
        print("  3. We'll match slides to audio timing automatically")
        print("\nReady when you are! 🚀")

    except ImportError:
        print("\nERROR: Playwright not installed")
        print("Run: pip install playwright")
        print("Then: playwright install chromium")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    input("\n\nPress Enter to exit...")
