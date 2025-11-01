#!/usr/bin/env python3
"""
GAMMA Fullscreen Explorer
Tries different methods to trigger fullscreen mode
"""

import time
from playwright.sync_api import sync_playwright

def explore_fullscreen_options():
    """Try multiple approaches to activate fullscreen"""

    gamma_url = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=present"

    print("="*70)
    print("GAMMA FULLSCREEN EXPLORER")
    print("="*70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        print(f"\nOpening: {gamma_url}")
        page.goto(gamma_url)

        print("Waiting 10 seconds for page to load...")
        time.sleep(10)

        print("\n" + "="*70)
        print("METHOD 1: JavaScript Fullscreen API")
        print("="*70)

        try:
            result = page.evaluate("""() => {
                // Try to trigger fullscreen using JavaScript API
                const elem = document.documentElement;
                if (elem.requestFullscreen) {
                    elem.requestFullscreen();
                    return 'requestFullscreen() called';
                } else if (elem.webkitRequestFullscreen) {
                    elem.webkitRequestFullscreen();
                    return 'webkitRequestFullscreen() called';
                } else if (elem.msRequestFullscreen) {
                    elem.msRequestFullscreen();
                    return 'msRequestFullscreen() called';
                } else {
                    return 'No fullscreen API available';
                }
            }""")
            print(f"   Result: {result}")
            time.sleep(3)

            # Check if it worked
            is_fullscreen = page.evaluate("() => !!document.fullscreenElement")
            print(f"   Is fullscreen: {is_fullscreen}")

            if is_fullscreen:
                print("   ✅ SUCCESS! Fullscreen activated via JavaScript API")
                page.screenshot(path='gamma_fullscreen_jsapi.png')
                print("   📸 Screenshot saved: gamma_fullscreen_jsapi.png")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print("\n" + "="*70)
        print("METHOD 2: Looking for Fullscreen Button")
        print("="*70)

        try:
            # Look for fullscreen button
            button_info = page.evaluate("""() => {
                // Search for fullscreen buttons
                const selectors = [
                    'button[aria-label*="fullscreen"]',
                    'button[aria-label*="Fullscreen"]',
                    'button[title*="fullscreen"]',
                    'button[title*="Fullscreen"]',
                    '[class*="fullscreen"]',
                    '[class*="Fullscreen"]'
                ];

                for (const selector of selectors) {
                    const button = document.querySelector(selector);
                    if (button) {
                        return {
                            found: true,
                            selector: selector,
                            ariaLabel: button.getAttribute('aria-label'),
                            title: button.getAttribute('title'),
                            className: button.className
                        };
                    }
                }

                return { found: false };
            }""")

            if button_info['found']:
                print(f"   ✅ Found fullscreen button!")
                print(f"      Selector: {button_info['selector']}")
                print(f"      Aria-label: {button_info.get('ariaLabel', 'N/A')}")
                print(f"      Title: {button_info.get('title', 'N/A')}")
                print(f"      Class: {button_info.get('className', 'N/A')}")

                # Try clicking it
                print(f"   Clicking fullscreen button...")
                page.click(button_info['selector'])
                time.sleep(3)

                page.screenshot(path='gamma_fullscreen_button.png')
                print("   📸 Screenshot saved: gamma_fullscreen_button.png")
            else:
                print("   ⚠️  No fullscreen button found")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print("\n" + "="*70)
        print("METHOD 3: F11 Key (Browser Fullscreen)")
        print("="*70)

        try:
            print("   Pressing F11...")
            page.keyboard.press('F11')
            time.sleep(3)

            page.screenshot(path='gamma_fullscreen_f11.png')
            print("   📸 Screenshot saved: gamma_fullscreen_f11.png")
            print("   Note: F11 is browser fullscreen, not GAMMA fullscreen")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print("\n" + "="*70)
        print("METHOD 4: Looking for GAMMA-specific Fullscreen")
        print("="*70)

        try:
            # Look for GAMMA's internal fullscreen mechanism
            gamma_fullscreen = page.evaluate("""() => {
                // Check for GAMMA-specific fullscreen
                const info = {
                    windowProps: []
                };

                // Look for fullscreen-related properties
                for (const key in window) {
                    if (key.toLowerCase().includes('fullscreen') ||
                        key.toLowerCase().includes('full') ||
                        key.toLowerCase().includes('maximize')) {
                        info.windowProps.push(key);
                    }
                }

                // Check for React/Vue components with fullscreen
                const buttons = document.querySelectorAll('button');
                info.buttonCount = buttons.length;
                info.buttonsWithFullscreen = [];

                buttons.forEach((button, idx) => {
                    const text = button.innerText.toLowerCase();
                    const aria = (button.getAttribute('aria-label') || '').toLowerCase();

                    if (text.includes('full') || aria.includes('full') ||
                        text.includes('expand') || aria.includes('expand')) {
                        info.buttonsWithFullscreen.push({
                            index: idx,
                            text: button.innerText,
                            ariaLabel: button.getAttribute('aria-label'),
                            className: button.className
                        });
                    }
                });

                return info;
            }""")

            print(f"   Window properties: {gamma_fullscreen['windowProps']}")
            print(f"   Total buttons: {gamma_fullscreen['buttonCount']}")

            if gamma_fullscreen['buttonsWithFullscreen']:
                print(f"   Found {len(gamma_fullscreen['buttonsWithFullscreen'])} buttons with 'full' or 'expand':")
                for btn in gamma_fullscreen['buttonsWithFullscreen'][:5]:
                    print(f"      Button {btn['index']}: '{btn['text']}' (aria: {btn['ariaLabel']})")
            else:
                print("   No obvious fullscreen buttons found")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        print("\n" + "="*70)
        print("METHOD 5: Pressing 'F' Key")
        print("="*70)

        try:
            print("   Many presentation tools use 'F' for fullscreen...")
            print("   Pressing 'f'...")
            page.keyboard.press('f')
            time.sleep(3)

            is_fullscreen = page.evaluate("() => !!document.fullscreenElement")
            print(f"   Is fullscreen after 'f': {is_fullscreen}")

            if is_fullscreen:
                print("   ✅ SUCCESS! 'F' key triggered fullscreen!")

            page.screenshot(path='gamma_fullscreen_fkey.png')
            print("   📸 Screenshot saved: gamma_fullscreen_fkey.png")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print("\n" + "="*70)
        print("FINAL CHECK")
        print("="*70)

        final_state = page.evaluate("""() => {
            return {
                isFullscreen: !!document.fullscreenElement,
                fullscreenElement: document.fullscreenElement ? document.fullscreenElement.tagName : 'none',
                documentTitle: document.title,
                bodyClasses: document.body.className
            };
        }""")

        print(f"   Fullscreen active: {final_state['isFullscreen']}")
        print(f"   Fullscreen element: {final_state['fullscreenElement']}")
        print(f"   Body classes: {final_state['bodyClasses'][:100]}")

        print("\n" + "="*70)
        print("RESULTS")
        print("="*70)
        print("\nCheck the screenshots to see which method worked:")
        print("  - gamma_fullscreen_jsapi.png")
        print("  - gamma_fullscreen_button.png")
        print("  - gamma_fullscreen_f11.png")
        print("  - gamma_fullscreen_fkey.png")

        print("\nBrowser will stay open for 20 seconds...")
        print("Check if any method activated fullscreen!")
        time.sleep(20)

        browser.close()


if __name__ == "__main__":
    try:
        from playwright.sync_api import sync_playwright
        explore_fullscreen_options()
    except ImportError:
        print("ERROR: Playwright not installed")
        print("Run: pip install playwright")
        print("Then: playwright install chromium")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
