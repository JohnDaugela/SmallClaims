#!/usr/bin/env python3
"""
GAMMA Presentation Analyzer
Automatically discovers slide structure and content
"""

import time
import json
import pyautogui
from PIL import Image, ImageChops
import pytesseract
import os
from datetime import datetime

class GammaAnalyzer:
    def __init__(self, gamma_url, output_dir="gamma_analysis"):
        self.gamma_url = gamma_url
        self.output_dir = output_dir
        self.slides = []

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

    def compare_images(self, img1_path, img2_path, threshold=0.99):
        """
        Compare two screenshots to see if they're identical
        Returns True if images are the same (no change detected)
        """
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)

        # Calculate difference
        diff = ImageChops.difference(img1, img2)

        # Get histogram to see if images are similar
        histogram = diff.histogram()

        # Calculate similarity (simple approach)
        total_pixels = sum(histogram)
        if total_pixels == 0:
            return True  # Images are identical

        # Count pixels that are the same (value 0 in histogram)
        same_pixels = histogram[0]
        similarity = same_pixels / total_pixels

        return similarity > threshold

    def extract_text_from_screenshot(self, screenshot_path):
        """Extract text from screenshot using OCR"""
        try:
            img = Image.open(screenshot_path)
            text = pytesseract.image_to_string(img)
            return text.strip()
        except Exception as e:
            print(f"   ⚠️  OCR failed: {e}")
            return ""

    def countdown(self, seconds=5):
        """Give user time to focus on browser window"""
        print(f"\n⏰ You have {seconds} seconds to focus on your GAMMA browser window...")
        for i in range(seconds, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        print("   🚀 Starting analysis!\n")

    def analyze_presentation(self, max_slides=50):
        """
        Automatically click through presentation and capture content
        Returns: List of slide data
        """
        print("=" * 70)
        print("GAMMA PRESENTATION ANALYZER")
        print("=" * 70)
        print(f"\n📋 Analyzing: {self.gamma_url}")
        print(f"📁 Output directory: {self.output_dir}\n")

        print("INSTRUCTIONS:")
        print("1. Open your GAMMA presentation in a browser")
        print("2. Make sure it's visible on screen")
        print("3. Press Enter when ready...")
        input()

        self.countdown(5)

        # Enter presentation mode
        print("🎬 Entering presentation mode (Ctrl+Shift+Enter)...")
        pyautogui.hotkey('ctrl', 'shift', 'enter')
        time.sleep(3)

        # Enter spotlight mode
        print("💡 Entering spotlight mode (S)...")
        pyautogui.press('s')
        time.sleep(2)

        print("\n" + "=" * 70)
        print("ANALYZING SLIDES...")
        print("=" * 70 + "\n")

        slide_num = 0
        previous_screenshot = None

        for i in range(max_slides):
            slide_num = i + 1

            # Take screenshot
            screenshot_path = os.path.join(self.output_dir, f"slide_{slide_num:02d}.png")
            pyautogui.screenshot(screenshot_path)

            # Extract text from screenshot
            print(f"📸 Slide {slide_num}: Captured screenshot...")
            text = self.extract_text_from_screenshot(screenshot_path)

            # Store slide data
            slide_data = {
                "slide_number": slide_num,
                "screenshot": screenshot_path,
                "text_content": text,
                "preview": text[:100] + "..." if len(text) > 100 else text
            }
            self.slides.append(slide_data)

            print(f"   📝 Text preview: {slide_data['preview'][:60]}...")

            # Press spacebar to advance
            print(f"   ⏭️  Pressing spacebar...\n")
            pyautogui.press('space')
            time.sleep(1)

            # Take another screenshot to check if anything changed
            next_screenshot_path = os.path.join(self.output_dir, f"slide_{slide_num:02d}_check.png")
            pyautogui.screenshot(next_screenshot_path)

            # Compare with previous screenshot
            if self.compare_images(screenshot_path, next_screenshot_path, threshold=0.98):
                print("✅ No change detected - reached end of presentation!")
                print(f"   Total slides found: {slide_num}")
                os.remove(next_screenshot_path)  # Clean up check screenshot
                break
            else:
                os.remove(next_screenshot_path)  # Clean up check screenshot

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

        return output_file

def main():
    # Configuration
    GAMMA_URL = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc"

    # Check dependencies
    try:
        import pytesseract
        import PIL
    except ImportError:
        print("\n⚠️  Missing dependencies!")
        print("\nPlease install:")
        print("  pip install pytesseract pillow")
        print("\nAlso install Tesseract OCR:")
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("  Add Tesseract to your PATH")
        return

    # Create analyzer
    analyzer = GammaAnalyzer(GAMMA_URL)

    # Analyze presentation
    analyzer.analyze_presentation()

    # Save results
    analyzer.save_analysis()

    print("\n✨ Next step: Provide your script and audio file for synchronization!\n")

if __name__ == "__main__":
    main()
