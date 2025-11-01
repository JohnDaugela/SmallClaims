#!/usr/bin/env python3
"""
GAMMA SLIDE READER - WORKING VERSION!
Reads all slides using [data-card-id] selector
"""

import time
import json
from playwright.sync_api import sync_playwright

def read_gamma_slides_working():
    """Read slides using the correct selector!"""

    gamma_url = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=present"

    print("="*70)
    print("GAMMA SLIDE READER - Working Version!")
    print("="*70)
    print(f"\nURL: {gamma_url}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        print("Opening GAMMA presentation...")
        page.goto(gamma_url)

        print("Waiting 10 seconds for complete loading...")
        time.sleep(10)

        print("\n" + "="*70)
        print("READING ALL SLIDES")
        print("="*70 + "\n")

        # Read ALL slides using [data-card-id]
        slides_data = page.evaluate("""() => {
            // Use [data-card-id] - that's where the content is!
            const cards = document.querySelectorAll('[data-card-id]');
            const slides = [];

            cards.forEach((card, index) => {
                const text = card.innerText.trim();

                if (text && text.length > 0) {
                    slides.push({
                        slide_number: index + 1,
                        card_id: card.getAttribute('data-card-id'),
                        text_content: text,
                        text_length: text.length,
                        preview: text.substring(0, 100)
                    });
                }
            });

            return slides;
        }""")

        print(f"✅ SUCCESS! Found {len(slides_data)} slides with content!\n")

        print("="*70)
        print("SLIDE CONTENTS")
        print("="*70 + "\n")

        for slide in slides_data:
            print(f"📄 SLIDE {slide['slide_number']}")
            print(f"   Card ID: {slide['card_id']}")
            print(f"   Length: {slide['text_length']} characters")

            # Get first line as title
            lines = slide['text_content'].split('\n')
            title = lines[0] if lines else ""
            print(f"   Title: {title}")

            # Show preview
            preview = slide['preview'].replace('\n', ' ')
            if len(slide['text_content']) > 100:
                print(f"   Preview: {preview}...")
            print()

        # Save results
        output_file = 'gamma_slides_WORKING.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'gamma_url': gamma_url,
                'total_slides': len(slides_data),
                'slides': slides_data
            }, f, indent=2, ensure_ascii=False)

        print("="*70)
        print(f"💾 Results saved to: {output_file}")
        print("="*70)

        print("\n🎉 WE DID IT! Successfully read all slides from HTML!")
        print("\nNext step: Match these slides to your audio timing")

        print("\nBrowser will close in 5 seconds...")
        time.sleep(5)

        browser.close()

        return slides_data


if __name__ == "__main__":
    try:
        from playwright.sync_api import sync_playwright
        slides = read_gamma_slides_working()

        print("\n" + "="*70)
        print("SUCCESS SUMMARY")
        print("="*70)
        print(f"\n✅ Read {len(slides)} slides from GAMMA!")
        print("✅ Used ?mode=present URL parameter")
        print("✅ Found slides using [data-card-id] selector")
        print("\n📋 All slide data saved to gamma_slides_WORKING.json")

    except ImportError:
        print("\nERROR: Playwright not installed")
        print("Run: pip install playwright")
        print("Then: playwright install chromium")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    input("\n\nPress Enter to exit...")
