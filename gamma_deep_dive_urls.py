#!/usr/bin/env python3
"""
GAMMA URL & HTML DEEP DIVE
Explores presentation mode URL parameters and HTML structure
to find spotlight mode and other hidden features
"""

import time
import json
from playwright.sync_api import sync_playwright

def deep_dive_gamma():
    """Comprehensive exploration of GAMMA presentation mode"""

    # Test different URLs
    base_url = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5"

    url_variations = [
        ("Normal mode", f"{base_url}?mode=doc"),
        ("Present mode", f"{base_url}?mode=present"),
        ("Present + spotlight", f"{base_url}?mode=present&spotlight=true"),
        ("Present + spotlight2", f"{base_url}?mode=present&spotlight=1"),
        ("Present + fullscreen", f"{base_url}?mode=present&fullscreen=true"),
        ("Present + autoplay", f"{base_url}?mode=present&autoplay=true"),
    ]

    print("="*70)
    print("GAMMA DEEP DIVE - URL Parameters & HTML Exploration")
    print("="*70)

    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(no_viewport=True)

        for name, url in url_variations:
            print(f"\n" + "="*70)
            print(f"TESTING: {name}")
            print(f"URL: {url}")
            print("="*70)

            page = context.new_page()
            page.goto(url)

            print("Waiting 5 seconds for page to load...")
            time.sleep(5)

            # Analyze the page
            analysis = page.evaluate("""() => {
                const data = {};

                // 1. Check current URL (might have changed)
                data.currentURL = window.location.href;
                data.urlParams = window.location.search;
                data.urlHash = window.location.hash;

                // 2. Check for spotlight mode indicators
                data.spotlightActive = false;
                data.spotlightClasses = [];

                // Look for spotlight-related classes
                const bodyClasses = document.body.className;
                data.bodyClasses = bodyClasses;
                if (bodyClasses.includes('spotlight') || bodyClasses.includes('Spotlight')) {
                    data.spotlightActive = true;
                }

                // Check for spotlight in various elements
                const spotlightElements = document.querySelectorAll('[class*="spotlight"], [class*="Spotlight"]');
                data.spotlightElementCount = spotlightElements.length;

                // 3. Check presentation mode
                data.presentationModeActive = false;
                if (bodyClasses.includes('presentation') || bodyClasses.includes('present')) {
                    data.presentationModeActive = true;
                }

                // 4. Look for JavaScript globals/configs
                data.windowProps = [];
                for (const key in window) {
                    if (key.toLowerCase().includes('gamma') ||
                        key.toLowerCase().includes('spotlight') ||
                        key.toLowerCase().includes('present')) {
                        data.windowProps.push(key);
                    }
                }

                // 5. Find all data attributes
                data.dataAttributes = {};
                const elementsWithData = document.querySelectorAll('[data-mode], [data-spotlight], [data-present]');
                elementsWithData.forEach(elem => {
                    for (const attr of elem.attributes) {
                        if (attr.name.startsWith('data-')) {
                            data.dataAttributes[attr.name] = attr.value;
                        }
                    }
                });

                // 6. Check for keyboard event listeners
                data.hasKeyboardListeners = {
                    keydown: window.onkeydown !== null,
                    keyup: window.onkeyup !== null,
                    keypress: window.onkeypress !== null
                };

                // 7. Look for buttons/controls
                data.controls = {
                    spotlightButton: !!document.querySelector('[aria-label*="spotlight"], [title*="spotlight"], button[class*="spotlight"]'),
                    fullscreenButton: !!document.querySelector('[aria-label*="fullscreen"], [title*="fullscreen"]'),
                    nextButton: !!document.querySelector('[aria-label*="next"], [title*="next"]')
                };

                // 8. Check sections
                const sections = document.querySelectorAll('section');
                data.sectionCount = sections.length;
                data.sectionsWithText = 0;
                sections.forEach(section => {
                    if (section.innerText.trim().length > 0) {
                        data.sectionsWithText++;
                    }
                });

                // 9. Try to find spotlight toggle function
                data.spotlightFunctionExists = typeof window.toggleSpotlight === 'function' ||
                                               typeof window.enableSpotlight === 'function';

                return data;
            }""")

            # Print findings
            print(f"\n📊 ANALYSIS:")
            print(f"   Current URL: {analysis['currentURL']}")
            print(f"   URL Params: {analysis['urlParams']}")
            print(f"   URL Hash: {analysis['urlHash']}")
            print(f"\n   Presentation Mode Active: {analysis['presentationModeActive']}")
            print(f"   Spotlight Active: {analysis['spotlightActive']}")
            print(f"   Spotlight Elements: {analysis['spotlightElementCount']}")
            print(f"\n   Body Classes: {analysis['bodyClasses'][:100]}...")
            print(f"   Window Props: {', '.join(analysis['windowProps']) if analysis['windowProps'] else 'None'}")
            print(f"   Data Attributes: {analysis['dataAttributes']}")
            print(f"\n   Sections Found: {analysis['sectionCount']}")
            print(f"   Sections with Text: {analysis['sectionsWithText']}")
            print(f"\n   Controls:")
            print(f"      Spotlight button: {analysis['controls']['spotlightButton']}")
            print(f"      Fullscreen button: {analysis['controls']['fullscreenButton']}")
            print(f"      Next button: {analysis['controls']['nextButton']}")

            # Try pressing 'S' to see if it toggles spotlight
            print(f"\n   🔍 Testing: Pressing 'S' key...")
            page.keyboard.press('s')
            time.sleep(2)

            # Check if spotlight activated
            spotlight_check = page.evaluate("""() => {
                const bodyClasses = document.body.className;
                return bodyClasses.includes('spotlight') || bodyClasses.includes('Spotlight');
            }""")

            print(f"   Spotlight active after 'S': {spotlight_check}")

            # Take screenshot
            screenshot_file = f"gamma_test_{name.replace(' ', '_')}.png"
            page.screenshot(path=screenshot_file)
            print(f"   📸 Screenshot: {screenshot_file}")

            results[name] = analysis
            results[name]['spotlightAfterS'] = spotlight_check

            page.close()
            print(f"\n   Waiting 3 seconds before next test...")
            time.sleep(3)

        browser.close()

    # Save results
    with open('gamma_deep_dive_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*70)
    print("DEEP DIVE COMPLETE")
    print("="*70)
    print("\n💾 Results saved to: gamma_deep_dive_results.json")
    print("📸 Screenshots saved for each test")

    print("\n" + "="*70)
    print("FINDINGS & RECOMMENDATIONS")
    print("="*70)

    # Analyze results
    present_mode = results.get("Present mode", {})

    if present_mode.get('presentationModeActive'):
        print("\n✅ ?mode=present WORKS - enters presentation mode automatically!")

    if present_mode.get('spotlightAfterS'):
        print("✅ Pressing 'S' activates spotlight mode")

    if present_mode.get('sectionsWithText', 0) > 0:
        print(f"✅ Can read {present_mode['sectionsWithText']} slides in presentation mode")

    # Check if any URL params activated spotlight
    for name, data in results.items():
        if 'spotlight' in name.lower() and data.get('spotlightActive'):
            print(f"\n🎉 BREAKTHROUGH: {name} activated spotlight automatically!")

    print("\n" + "="*70)


if __name__ == "__main__":
    try:
        from playwright.sync_api import sync_playwright
        deep_dive_gamma()
    except ImportError:
        print("ERROR: Playwright not installed")
        print("Run: pip install playwright")
        print("Then: playwright install chromium")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
