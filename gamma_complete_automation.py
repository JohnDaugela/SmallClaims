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

        # Step 3: Activate Fullscreen - Try multiple methods
        print("\n[3] Activating Fullscreen...")

        fullscreen_success = False

        # Method 1: Find and click the fullscreen button
        try:
            print("    Method 1: Looking for fullscreen button...")
            # Try multiple selectors
            selectors = [
                "button[aria-label='Enter full screen']",
                "button[aria-label*='full screen' i]",
                "button[aria-label*='fullscreen' i]"
            ]

            for selector in selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.count() > 0:
                        btn.click(timeout=2000)
                        print(f"    ✅ Clicked button with selector: {selector}")
                        time.sleep(3)
                        fullscreen_success = True
                        break
                except:
                    continue

        except Exception as e:
            print(f"    ⚠️  Button approach failed: {e}")

        # Method 2: JavaScript API on the presentation container
        if not fullscreen_success:
            try:
                print("    Method 2: JavaScript requestFullscreen on body...")
                page.evaluate("""
                    document.body.requestFullscreen()
                        .then(() => console.log('Fullscreen success'))
                        .catch(err => console.log('Fullscreen error:', err));
                """)
                time.sleep(3)
                fullscreen_success = True
                print("    ✅ JavaScript fullscreen requested!")
            except Exception as e:
                print(f"    ⚠️  JavaScript failed: {e}")

        # Method 3: F11 via keyboard (browser fullscreen as fallback)
        if not fullscreen_success:
            try:
                print("    Method 3: F11 key (browser fullscreen)...")
                page.keyboard.press('F11')
                time.sleep(3)
                print("    ✅ F11 pressed (browser fullscreen)")
            except Exception as e:
                print(f"    ⚠️  F11 failed: {e}")

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
        print("✅ SETUP COMPLETE!")
        print("="*70)
        print("\nModes activated:")
        print(f"  ✅ Presentation mode (?mode=present)")
        print(f"  {'✅' if states['hasSpotlight'] else '⚠️ '} Spotlight mode")
        print(f"  {'✅' if states['isFullscreen'] else '⚠️ '} Fullscreen mode")
        print(f"  ✅ Read {len(slides_data)} slides from HTML")

        # Step 5: Automatically click through all slides
        print("\n" + "="*70)
        print("[6] AUTOMATIC PRESENTATION - CLICKING THROUGH SLIDES")
        print("="*70)
        print(f"\nWill advance through {len(slides_data)} slides")
        print("2 seconds between each spacebar press\n")

        time.sleep(3)
        print("🎬 Starting automatic presentation NOW!\n")

        for i in range(len(slides_data)):
            print(f"   [{i+1}/{len(slides_data)}] Pressing SPACEBAR... ", end='', flush=True)
            page.keyboard.press('Space')
            print("✅")

            if i < len(slides_data) - 1:  # Don't wait after last slide
                time.sleep(2)

        print("\n" + "="*70)
        print("✅ PRESENTATION COMPLETE!")
        print("="*70)
        print(f"Advanced through all {len(slides_data)} slides automatically!")

        print("\nBrowser will stay open for 10 seconds...")
        print("Press ESC to exit fullscreen if needed")

        time.sleep(10)

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
