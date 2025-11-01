#!/usr/bin/env python3
"""
GAMMA DOM Explorer
Inspects the HTML structure to see if we can read all slides directly
without clicking through
"""

import time
import json
from playwright.sync_api import sync_playwright

def explore_gamma_structure():
    GAMMA_URL = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc"

    print("="*70)
    print("GAMMA DOM STRUCTURE EXPLORER")
    print("="*70)
    print(f"\nAnalyzing: {GAMMA_URL}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        print("Opening GAMMA presentation...")
        page.goto(GAMMA_URL)

        print("Waiting 5 seconds for page to load...")
        time.sleep(5)

        print("\n" + "="*70)
        print("EXPLORING DOM STRUCTURE")
        print("="*70 + "\n")

        # Explore the DOM structure
        dom_info = page.evaluate("""() => {
            const info = {};

            // 1. Look for slide containers
            info.slideContainers = [];
            const slideSelectors = [
                '[class*="slide"]',
                '[class*="Slide"]',
                '[data-slide]',
                '[role="article"]',
                'article',
                'section'
            ];

            for (const selector of slideSelectors) {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                    info.slideContainers.push({
                        selector: selector,
                        count: elements.length,
                        firstElementClasses: elements[0].className,
                        firstElementHTML: elements[0].innerHTML.substring(0, 200)
                    });
                }
            }

            // 2. Look for navigation/counter elements
            info.navigation = [];
            const navSelectors = [
                '[class*="nav"]',
                '[class*="counter"]',
                '[class*="page"]',
                '[class*="progress"]',
                '[aria-label*="slide"]',
                '[aria-label*="page"]'
            ];

            for (const selector of navSelectors) {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                    info.navigation.push({
                        selector: selector,
                        count: elements.length,
                        text: Array.from(elements).slice(0, 3).map(e => e.innerText).join(' | ')
                    });
                }
            }

            // 3. Look for all divs/sections with substantial content
            info.contentBlocks = [];
            const allDivs = document.querySelectorAll('div, section, article');
            let contentBlocks = [];

            for (const div of allDivs) {
                const text = div.innerText;
                if (text && text.length > 20 && text.length < 1000) {
                    // Check if this is a leaf node (doesn't contain other content blocks)
                    const hasNestedContent = Array.from(div.children).some(child =>
                        child.innerText && child.innerText.length > 20
                    );

                    if (!hasNestedContent) {
                        contentBlocks.push({
                            classes: div.className,
                            text: text.substring(0, 100),
                            length: text.length
                        });
                    }
                }
            }
            info.contentBlocks = contentBlocks.slice(0, 20); // First 20

            // 4. Check for hidden elements (future slides?)
            info.hiddenElements = [];
            const hiddenDivs = document.querySelectorAll('[style*="display: none"], [hidden], [class*="hidden"]');
            info.hiddenElementCount = hiddenDivs.length;

            // 5. Look for data attributes that might indicate structure
            info.dataAttributes = [];
            const allElements = document.querySelectorAll('[data-slide], [data-index], [data-page], [data-card]');
            for (const elem of allElements) {
                const attrs = {};
                for (const attr of elem.attributes) {
                    if (attr.name.startsWith('data-')) {
                        attrs[attr.name] = attr.value;
                    }
                }
                if (Object.keys(attrs).length > 0) {
                    info.dataAttributes.push({
                        tag: elem.tagName,
                        attributes: attrs,
                        text: elem.innerText.substring(0, 50)
                    });
                }
            }

            // 6. Check the page title and any meta information
            info.pageTitle = document.title;
            info.bodyClasses = document.body.className;

            // 7. Look for React/Vue component roots
            info.frameworks = {
                hasReact: !!document.querySelector('[data-reactroot], [data-reactid]'),
                hasVue: !!document.querySelector('[data-v-]'),
                hasAngular: !!document.querySelector('[ng-app], [ng-controller]')
            };

            return info;
        }""")

        # Print findings
        print("📊 DOM ANALYSIS RESULTS:\n")

        print("1. SLIDE CONTAINERS FOUND:")
        if dom_info['slideContainers']:
            for container in dom_info['slideContainers']:
                print(f"   Selector: {container['selector']}")
                print(f"   Count: {container['count']}")
                print(f"   Classes: {container['firstElementClasses']}")
                print(f"   HTML preview: {container['firstElementHTML'][:100]}...")
                print()
        else:
            print("   None found\n")

        print("2. NAVIGATION ELEMENTS:")
        if dom_info['navigation']:
            for nav in dom_info['navigation']:
                print(f"   Selector: {nav['selector']}")
                print(f"   Count: {nav['count']}")
                print(f"   Text: {nav['text']}")
                print()
        else:
            print("   None found\n")

        print(f"3. CONTENT BLOCKS: Found {len(dom_info['contentBlocks'])} blocks")
        for i, block in enumerate(dom_info['contentBlocks'][:5], 1):
            print(f"   Block {i}: {block['text'][:60]}...")
        print()

        print(f"4. HIDDEN ELEMENTS: {dom_info['hiddenElementCount']} elements")
        print()

        print("5. DATA ATTRIBUTES:")
        if dom_info['dataAttributes']:
            for i, elem in enumerate(dom_info['dataAttributes'][:10], 1):
                print(f"   Element {i}: <{elem['tag']}> {elem['attributes']}")
                print(f"      Text: {elem['text'][:50]}...")
        else:
            print("   None found")
        print()

        print(f"6. PAGE INFO:")
        print(f"   Title: {dom_info['pageTitle']}")
        print(f"   Body classes: {dom_info['bodyClasses']}")
        print()

        print(f"7. FRAMEWORKS:")
        print(f"   React: {dom_info['frameworks']['hasReact']}")
        print(f"   Vue: {dom_info['frameworks']['hasVue']}")
        print(f"   Angular: {dom_info['frameworks']['hasAngular']}")
        print()

        # Save raw data
        with open('gamma_dom_structure.json', 'w', encoding='utf-8') as f:
            json.dump(dom_info, f, indent=2, ensure_ascii=False)

        print("💾 Full DOM analysis saved to: gamma_dom_structure.json")

        print("\n" + "="*70)
        print("CONCLUSION:")
        print("="*70)

        if dom_info['slideContainers']:
            print(f"\n✅ Found potential slide containers!")
            print(f"   We might be able to read all {dom_info['slideContainers'][0]['count']} slides directly from HTML")
        else:
            print("\n⚠️  No obvious slide containers found in DOM")
            print("   GAMMA might load slides dynamically/lazily")

        if dom_info['hiddenElementCount'] > 10:
            print(f"\n📦 Found {dom_info['hiddenElementCount']} hidden elements")
            print("   These might be future slides not yet visible")

        print("\nBrowser will stay open for 15 seconds so you can inspect it...")
        print("You can also open browser dev tools (F12) to explore manually.")
        time.sleep(15)

        browser.close()

if __name__ == "__main__":
    try:
        from playwright.sync_api import sync_playwright
        explore_gamma_structure()
    except ImportError:
        print("\nERROR: Playwright not installed!")
        print("Run: pip install playwright")
        print("Then: playwright install chromium")
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
