#!/usr/bin/env python3
"""
GAMMA SLIDE READER - DEBUG VERSION
Helps us figure out why slides aren't being found
"""

import time
import json
from playwright.sync_api import sync_playwright

def debug_gamma_page():
    """Debug what's in the GAMMA HTML"""

    gamma_url = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc"

    print("="*70)
    print("GAMMA DEBUG - Finding Slides")
    print("="*70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        print("\n[1] Opening GAMMA...")
        page.goto(gamma_url)

        print("[2] Waiting 5 seconds...")
        time.sleep(5)

        print("\n" + "="*70)
        print("CHECKING HTML STRUCTURE")
        print("="*70 + "\n")

        # Check various things
        debug_info = page.evaluate("""() => {
            const info = {};

            // 1. Check for section elements
            const sections = document.querySelectorAll('section');
            info.sectionCount = sections.length;
            info.sectionDetails = [];

            for (let i = 0; i < Math.min(sections.length, 5); i++) {
                const section = sections[i];
                info.sectionDetails.push({
                    index: i,
                    hasText: section.innerText.length > 0,
                    textLength: section.innerText.length,
                    textPreview: section.innerText.substring(0, 100),
                    className: section.className,
                    hasChildren: section.children.length
                });
            }

            // 2. Try other selectors
            info.otherSelectors = {
                'div[class*="slide"]': document.querySelectorAll('div[class*="slide"]').length,
                'div[class*="card"]': document.querySelectorAll('div[class*="card"]').length,
                '[data-index]': document.querySelectorAll('[data-index]').length,
                'article': document.querySelectorAll('article').length,
                '[role="article"]': document.querySelectorAll('[role="article"]').length
            };

            // 3. Get body text to see if ANYTHING loaded
            info.bodyTextLength = document.body.innerText.length;
            info.bodyTextPreview = document.body.innerText.substring(0, 200);

            // 4. Check if it's still loading
            info.readyState = document.readyState;
            info.title = document.title;

            return info;
        }""")

        # Print findings
        print(f"1. PAGE INFO:")
        print(f"   Title: {debug_info['title']}")
        print(f"   Ready state: {debug_info['readyState']}")
        print(f"   Body text length: {debug_info['bodyTextLength']} chars")
        print(f"   Body preview: {debug_info['bodyTextPreview'][:100]}...")
        print()

        print(f"2. SECTION ELEMENTS:")
        print(f"   Found: {debug_info['sectionCount']} sections")
        if debug_info['sectionDetails']:
            for detail in debug_info['sectionDetails']:
                print(f"\n   Section {detail['index']}:")
                print(f"      Has text: {detail['hasText']}")
                print(f"      Text length: {detail['textLength']}")
                print(f"      Classes: {detail['className']}")
                print(f"      Children: {detail['hasChildren']}")
                if detail['textPreview']:
                    print(f"      Preview: {detail['textPreview'][:60]}...")
        else:
            print("   No section details available")
        print()

        print(f"3. OTHER SELECTORS:")
        for selector, count in debug_info['otherSelectors'].items():
            print(f"   {selector}: {count} elements")
        print()

        # Wait longer and check again
        print("="*70)
        print("WAITING 10 MORE SECONDS AND CHECKING AGAIN")
        print("="*70 + "\n")

        print("Waiting...")
        time.sleep(10)

        # Check again
        debug_info2 = page.evaluate("""() => {
            const sections = document.querySelectorAll('section');
            return {
                sectionCount: sections.length,
                firstSectionText: sections.length > 0 ? sections[0].innerText.substring(0, 100) : 'N/A'
            };
        }""")

        print(f"After 10 more seconds:")
        print(f"   Sections found: {debug_info2['sectionCount']}")
        print(f"   First section text: {debug_info2['firstSectionText']}")

        # Try to scroll the page (sometimes triggers lazy loading)
        print("\n" + "="*70)
        print("TRYING TO SCROLL (might trigger loading)")
        print("="*70 + "\n")

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)

        # Check one more time
        debug_info3 = page.evaluate("""() => {
            const sections = document.querySelectorAll('section');
            const slides = [];

            sections.forEach((section, index) => {
                const text = section.innerText.trim();
                if (text && text.length > 0) {
                    slides.push({
                        number: index + 1,
                        length: text.length,
                        preview: text.substring(0, 80)
                    });
                }
            });

            return {
                totalSections: sections.length,
                slidesWithContent: slides.length,
                slides: slides
            };
        }""")

        print(f"FINAL CHECK:")
        print(f"   Total sections: {debug_info3['totalSections']}")
        print(f"   Sections with content: {debug_info3['slidesWithContent']}")

        if debug_info3['slides']:
            print(f"\n   FOUND SLIDES:")
            for slide in debug_info3['slides'][:5]:
                print(f"      Slide {slide['number']}: {slide['preview'][:60]}...")
        else:
            print(f"\n   ⚠️ NO SLIDES WITH CONTENT FOUND")

        # Save debug info
        with open('gamma_debug.json', 'w') as f:
            json.dump({
                'check1': debug_info,
                'check2': debug_info2,
                'check3': debug_info3
            }, f, indent=2)

        print(f"\n💾 Debug info saved to: gamma_debug.json")

        print("\n" + "="*70)
        print("Browser will stay open for 20 seconds.")
        print("Look at the browser - do you see the presentation?")
        print("Press F12 to open dev tools and inspect the HTML manually.")
        print("="*70)

        time.sleep(20)
        browser.close()

if __name__ == "__main__":
    try:
        from playwright.sync_api import sync_playwright
        debug_gamma_page()
    except ImportError:
        print("ERROR: Playwright not installed")
        print("Run: pip install playwright")
        print("Then: playwright install chromium")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
