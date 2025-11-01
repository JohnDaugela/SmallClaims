#!/usr/bin/env python3
"""
GAMMA Content Deep Dive
Finds where the actual slide text is hiding inside sections
"""

import time
import json
from playwright.sync_api import sync_playwright

def find_slide_content():
    """Dig into section structure to find the actual content"""

    # Use present mode since it works!
    gamma_url = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=present"

    print("="*70)
    print("GAMMA CONTENT DEEP DIVE - Finding the Text!")
    print("="*70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        print(f"\nOpening: {gamma_url}")
        page.goto(gamma_url)

        print("Waiting 10 seconds for FULL page load...")
        time.sleep(10)

        print("\n" + "="*70)
        print("ANALYZING SECTION STRUCTURE")
        print("="*70 + "\n")

        # Deep dive into sections
        analysis = page.evaluate("""() => {
            const sections = document.querySelectorAll('section');
            const results = {
                totalSections: sections.length,
                sectionsAnalyzed: [],
                alternativeSelectors: {}
            };

            // Analyze first 5 sections in detail
            for (let i = 0; i < Math.min(5, sections.length); i++) {
                const section = sections[i];
                const sectionData = {
                    index: i,
                    directText: section.innerText.trim(),
                    directTextLength: section.innerText.trim().length,
                    childCount: section.children.length,
                    childElements: []
                };

                // Check each child element
                for (let j = 0; j < Math.min(10, section.children.length); j++) {
                    const child = section.children[j];
                    sectionData.childElements.push({
                        tagName: child.tagName,
                        className: child.className,
                        text: child.innerText ? child.innerText.substring(0, 100) : '',
                        textLength: child.innerText ? child.innerText.length : 0
                    });
                }

                results.sectionsAnalyzed.push(sectionData);
            }

            // Try alternative selectors that might have content
            const alternativeSelectors = [
                'div[class*="card"]',
                'div[class*="Card"]',
                'div[class*="slide"]',
                'div[class*="Slide"]',
                'div[class*="content"]',
                'div[class*="Content"]',
                '[data-card-id]',
                '[id*="card"]',
                'h1, h2, h3',
                'p'
            ];

            alternativeSelectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                    const firstText = elements[0].innerText ? elements[0].innerText.substring(0, 80) : '';
                    results.alternativeSelectors[selector] = {
                        count: elements.length,
                        firstElementText: firstText,
                        hasText: firstText.length > 0
                    };
                }
            });

            // Get visible card/slide
            const visibleCard = document.querySelector('[class*="visible"], [class*="active"], [class*="current"]');
            results.visibleCard = {
                found: !!visibleCard,
                text: visibleCard ? visibleCard.innerText.substring(0, 100) : 'N/A'
            };

            return results;
        }""")

        # Print findings
        print(f"Total sections: {analysis['totalSections']}")
        print()

        print("SECTION DETAILS:")
        for section in analysis['sectionsAnalyzed']:
            print(f"\n  Section {section['index']}:")
            print(f"    Direct text length: {section['directTextLength']}")
            print(f"    Children: {section['childCount']}")

            if section['directText']:
                print(f"    Direct text: {section['directText'][:60]}...")

            if section['childElements']:
                print(f"    Child elements:")
                for i, child in enumerate(section['childElements'][:3]):
                    if child['textLength'] > 0:
                        print(f"      [{i}] <{child['tagName']}> ({child['textLength']} chars)")
                        print(f"          {child['text'][:60]}...")

        print("\n" + "="*70)
        print("ALTERNATIVE SELECTORS WITH TEXT:")
        print("="*70 + "\n")

        for selector, data in analysis['alternativeSelectors'].items():
            if data['hasText']:
                print(f"✅ {selector}")
                print(f"   Count: {data['count']}")
                print(f"   Sample: {data['firstElementText'][:60]}...")
                print()

        print("="*70)
        print("VISIBLE CARD:")
        print("="*70)
        print(f"Found: {analysis['visibleCard']['found']}")
        print(f"Text: {analysis['visibleCard']['text']}")

        # Try pressing spacebar and checking again
        print("\n" + "="*70)
        print("TESTING SPACEBAR - Does content change?")
        print("="*70 + "\n")

        # Get current visible text
        text1 = page.evaluate("() => document.body.innerText")
        print(f"Before spacebar: {len(text1)} chars")
        print(f"Preview: {text1[:100]}...")

        print("\nPressing SPACEBAR...")
        page.keyboard.press('Space')
        time.sleep(2)

        # Get new text
        text2 = page.evaluate("() => document.body.innerText")
        print(f"\nAfter spacebar: {len(text2)} chars")
        print(f"Preview: {text2[:100]}...")

        if text1 != text2:
            print("\n✅ TEXT CHANGED! Spacebar works in present mode!")
        else:
            print("\n⚠️  Text didn't change")

        # Save full analysis
        with open('gamma_content_analysis.json', 'w') as f:
            json.dump(analysis, f, indent=2)

        print("\n💾 Analysis saved to: gamma_content_analysis.json")

        print("\nBrowser will stay open for 15 seconds...")
        print("Look at the browser - can you see slide content?")
        time.sleep(15)

        browser.close()

if __name__ == "__main__":
    try:
        from playwright.sync_api import sync_playwright
        find_slide_content()
    except ImportError:
        print("ERROR: Playwright not installed")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
