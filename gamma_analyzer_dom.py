#!/usr/bin/env python3
"""
GAMMA Presentation Analyzer - DOM Version
Uses browser automation to inspect HTML directly instead of OCR
Much more accurate and reliable!
"""

import time
import json
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

class GammaAnalyzerDOM:
    def __init__(self, gamma_url, output_dir="gamma_analysis"):
        self.gamma_url = gamma_url
        self.output_dir = output_dir
        self.slides = []

        os.makedirs(output_dir, exist_ok=True)

    def get_slide_content(self, page):
        """Extract slide content directly from DOM"""
        try:
            # Get all visible text content from the main presentation area
            # GAMMA typically uses specific containers for slides
            content = page.evaluate("""() => {
                // Try to find the main slide container
                const selectors = [
                    '[class*="slide"]',
                    '[class*="Slide"]',
                    '[class*="content"]',
                    '[role="main"]',
                    'main',
                    '[class*="presentation"]'
                ];

                for (const selector of selectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        return {
                            text: element.innerText,
                            html: element.innerHTML.substring(0, 500)
                        };
                    }
                }

                // Fallback: get body text
                return {
                    text: document.body.innerText,
                    html: document.body.innerHTML.substring(0, 500)
                };
            }""")
            return content
        except Exception as e:
            print(f"   ⚠️  Error extracting content: {e}")
            return {"text": "", "html": ""}

    def get_slide_number(self, page):
        """Try to find current slide number from DOM"""
        try:
            slide_info = page.evaluate("""() => {
                // Look for slide counter/indicator
                const counterSelectors = [
                    '[class*="slide-number"]',
                    '[class*="slideNumber"]',
                    '[class*="counter"]',
                    '[class*="page"]'
                ];

                for (const selector of counterSelectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        return element.innerText;
                    }
                }

                return null;
            }""")
            return slide_info
        except:
            return None

    def analyze_presentation(self, max_slides=50):
        """
        Use Playwright to analyze presentation by inspecting DOM
        """
        print("=" * 70)
        print("GAMMA PRESENTATION ANALYZER (DOM-based)")
        print("=" * 70)
        print(f"\n📋 Analyzing: {self.gamma_url}")
        print(f"📁 Output directory: {self.output_dir}\n")

        with sync_playwright() as p:
            # Launch browser
            print("🚀 Launching browser...")
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # Navigate to GAMMA
            print(f"📂 Opening GAMMA presentation...")
            page.goto(self.gamma_url)
            time.sleep(3)

            print("\nINSTRUCTIONS:")
            print("The browser window is now open.")
            print("We'll automatically enter presentation mode in 5 seconds...")
            print()

            for i in range(5, 0, -1):
                print(f"   {i}...")
                time.sleep(1)

            # Enter presentation mode
            print("\n🎬 Entering presentation mode (Ctrl+Shift+Enter)...")
            page.keyboard.press('Control+Shift+Enter')
            time.sleep(3)

            # Enter spotlight mode
            print("💡 Entering spotlight mode (S)...")
            page.keyboard.press('s')
            time.sleep(2)

            print("\n" + "=" * 70)
            print("ANALYZING SLIDES...")
            print("=" * 70 + "\n")

            previous_content = None
            slide_num = 0

            for i in range(max_slides):
                slide_num = i + 1

                # Get current slide content from DOM
                content = self.get_slide_content(page)
                slide_number_indicator = self.get_slide_number(page)

                print(f"📄 Slide {slide_num}:")
                if slide_number_indicator:
                    print(f"   📊 Slide indicator: {slide_number_indicator}")

                # Take screenshot for reference
                screenshot_path = os.path.join(self.output_dir, f"slide_{slide_num:02d}.png")
                page.screenshot(path=screenshot_path)

                # Store slide data
                slide_data = {
                    "slide_number": slide_num,
                    "screenshot": screenshot_path,
                    "text_content": content['text'],
                    "html_preview": content['html'][:200],
                    "slide_indicator": slide_number_indicator,
                    "preview": content['text'][:100] + "..." if len(content['text']) > 100 else content['text']
                }
                self.slides.append(slide_data)

                # Show preview
                preview_text = content['text'][:80].replace('\n', ' ')
                print(f"   📝 Content: {preview_text}...")

                # Press spacebar to advance
                print(f"   ⏭️  Pressing spacebar...\n")
                page.keyboard.press('Space')
                time.sleep(1)

                # Get new content after pressing spacebar
                new_content = self.get_slide_content(page)

                # Compare text content (much more reliable than image comparison!)
                if new_content['text'] == content['text']:
                    print("✅ No change detected in DOM - reached end of presentation!")
                    print(f"   Total slides found: {slide_num}")
                    break

                previous_content = content

            print(f"\n🎉 Analysis complete! Found {len(self.slides)} slides.")

            print("\nBrowser will stay open for 5 seconds so you can see the result...")
            time.sleep(5)

            browser.close()

        return self.slides

    def save_analysis(self):
        """Save analysis results to JSON file"""
        output_file = os.path.join(self.output_dir, "presentation_analysis.json")

        analysis_data = {
            "gamma_url": self.gamma_url,
            "analyzed_at": datetime.now().isoformat(),
            "total_slides": len(self.slides),
            "slides": self.slides
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"\n📊 Total slides found: {len(self.slides)}")
        print(f"💾 Analysis saved to: {output_file}")
        print(f"📸 Screenshots saved to: {self.output_dir}/")

        # Show summary
        print("\n📋 SLIDE SUMMARY:")
        print("-" * 70)
        for slide in self.slides:
            preview = slide['preview'][:50].replace('\n', ' ')
            print(f"   Slide {slide['slide_number']:2d}: {preview}...")

        return output_file

def main():
    # Configuration
    GAMMA_URL = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc"

    # Check dependencies
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n⚠️  Missing Playwright!")
        print("\nPlease install:")
        print("  pip install playwright")
        print("  playwright install chromium")
        input("\nPress Enter to exit...")
        return

    # Create analyzer
    analyzer = GammaAnalyzerDOM(GAMMA_URL)

    # Analyze presentation
    analyzer.analyze_presentation()

    # Save results
    analyzer.save_analysis()

    print("\n✨ Next step: Provide your script and audio file for synchronization!\n")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
