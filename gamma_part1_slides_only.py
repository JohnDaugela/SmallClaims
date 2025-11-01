#!/usr/bin/env python3
"""
=============================================================================
GAMMA SLIDE READER - PART 1 ONLY
=============================================================================

Reads all slides from your GAMMA presentation directly from HTML.
No clicking, no screenshots, no OCR - just pure HTML reading!

SETUP (one-time):
  pip install playwright
  playwright install chromium

USAGE:
  Just double-click this file!

=============================================================================
"""

import time
import json
from playwright.sync_api import sync_playwright

def read_gamma_slides():
    """Read all slides from GAMMA presentation"""

    print("="*70)
    print("GAMMA SLIDE READER - Part 1")
    print("="*70)

    # Get GAMMA URL
    print("\nEnter your GAMMA presentation URL")
    print("(or press Enter for default test presentation):\n")
    gamma_url = input().strip()

    if not gamma_url:
        gamma_url = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc"
        print(f"\nUsing default: {gamma_url}")

    print("\n" + "="*70)
    print("OPENING GAMMA PRESENTATION")
    print("="*70)

    with sync_playwright() as p:
        # Launch browser
        print("\nLaunching browser...")
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        # Open GAMMA
        print("Loading presentation...")
        page.goto(gamma_url)

        print("Waiting 5 seconds for page to fully load...")
        time.sleep(5)

        print("\n" + "="*70)
        print("READING SLIDES FROM HTML")
        print("="*70 + "\n")

        # Extract all slides directly from DOM
        slides_data = page.evaluate("""() => {
            // GAMMA uses <section> elements for slides
            const sections = document.querySelectorAll('section');
            const slides = [];

            sections.forEach((section, index) => {
                // Get text content from this slide
                const text = section.innerText.trim();

                // Only include sections with content
                if (text && text.length > 0) {
                    slides.push({
                        slide_number: index + 1,
                        text_content: text,
                        text_length: text.length,
                        preview: text.substring(0, 100)
                    });
                }
            });

            return slides;
        }""")

        # Show results
        print(f"✅ SUCCESS! Found {len(slides_data)} slides\n")

        print("="*70)
        print("SLIDE CONTENTS")
        print("="*70 + "\n")

        for slide in slides_data:
            print(f"📄 SLIDE {slide['slide_number']}")
            print(f"   Length: {slide['text_length']} characters")

            # Show first line as title
            lines = slide['text_content'].split('\n')
            first_line = lines[0] if lines else "(empty)"
            print(f"   Title: {first_line}")

            # Show preview
            preview = slide['preview'].replace('\n', ' ')
            if len(slide['text_content']) > 100:
                print(f"   Preview: {preview}...")
            else:
                print(f"   Content: {preview}")
            print()

        # Save to JSON file
        output_file = 'gamma_slides.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'gamma_url': gamma_url,
                'total_slides': len(slides_data),
                'slides': slides_data
            }, f, indent=2, ensure_ascii=False)

        print("="*70)
        print(f"💾 Results saved to: {output_file}")
        print("="*70)

        print("\nYou can open this JSON file to see all the slide data.")
        print("\nBrowser will close in 5 seconds...")
        time.sleep(5)

        browser.close()

        return slides_data


def main():
    print("\n" + "="*70)
    print("         GAMMA SLIDE READER - Part 1 Only")
    print("="*70)
    print("\nThis reads all slides from your GAMMA presentation.")
    print("No clicking through needed - reads directly from HTML!\n")

    # Check if Playwright is installed
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ ERROR: Playwright not installed!\n")
        print("Please run these commands:")
        print("  pip install playwright")
        print("  playwright install chromium\n")
        input("Press Enter to exit...")
        return

    try:
        # Read slides
        slides = read_gamma_slides()

        print("\n" + "="*70)
        print("WHAT'S NEXT?")
        print("="*70)
        print("\n✅ Part 1 COMPLETE - We can read all your slides!")
        print("\nNext steps:")
        print("  Part 2: Transcribe your voiceover audio")
        print("  Part 3: Match slides to audio timing")
        print("  Part 4: Run automated presentation")
        print("\nLet me know when you're ready for Part 2!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    input("\n\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    finally:
        input("\nPress Enter to exit...")
