#!/usr/bin/env python3
"""
GAMMA Slide Reader - Direct DOM Access
Reads all slides directly from HTML without clicking through!
"""

import time
import json
from playwright.sync_api import sync_playwright

def read_all_gamma_slides():
    GAMMA_URL = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc"

    print("="*70)
    print("GAMMA SLIDE READER - Direct HTML Method")
    print("="*70)
    print(f"\nReading: {GAMMA_URL}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        print("Opening GAMMA presentation...")
        page.goto(GAMMA_URL)

        print("Waiting 5 seconds for page to load...")
        time.sleep(5)

        print("\n" + "="*70)
        print("READING ALL SLIDES FROM HTML")
        print("="*70 + "\n")

        # Extract all slides directly from DOM
        slides_data = page.evaluate("""() => {
            // Find all section elements (these are the slides)
            const sections = document.querySelectorAll('section');
            const slides = [];

            sections.forEach((section, index) => {
                // Get all text content from this section
                const text = section.innerText.trim();

                // Only include sections with meaningful content
                if (text && text.length > 0) {
                    slides.push({
                        slide_number: index + 1,
                        text_content: text,
                        html_preview: section.innerHTML.substring(0, 200),
                        text_length: text.length,
                        preview: text.substring(0, 100)
                    });
                }
            });

            return slides;
        }""")

        print(f"✅ Found {len(slides_data)} slides!\n")

        # Display each slide
        for slide in slides_data:
            print(f"📄 Slide {slide['slide_number']}:")
            print(f"   Length: {slide['text_length']} characters")
            preview = slide['preview'].replace('\n', ' ')
            print(f"   Preview: {preview}...")
            print()

        # Save results
        output_data = {
            'gamma_url': GAMMA_URL,
            'total_slides': len(slides_data),
            'slides': slides_data
        }

        with open('gamma_slides_direct.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print("="*70)
        print(f"✅ SUCCESS - Read {len(slides_data)} slides directly from HTML!")
        print("="*70)
        print("\n💾 Results saved to: gamma_slides_direct.json")
        print("\n📋 SUMMARY:")
        for slide in slides_data:
            lines = slide['text_content'].split('\n')
            first_line = lines[0] if lines else "(empty)"
            print(f"   Slide {slide['slide_number']:2d}: {first_line[:60]}")

        print("\n🎉 No clicking needed - got everything from the HTML!")
        print("\nBrowser will close in 5 seconds...")
        time.sleep(5)

        browser.close()

        return slides_data

if __name__ == "__main__":
    try:
        from playwright.sync_api import sync_playwright
        slides = read_all_gamma_slides()

        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("\nNow that we can read all slides from HTML:")
        print("1. ✅ We know there are exactly", len(slides), "slides")
        print("2. ✅ We have the text content of each slide")
        print("3. ⏭️  Next: Match this content to your audio transcription")
        print("4. ⏭️  Then: Automate the presentation with perfect timing")

        input("\nPress Enter to exit...")

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
