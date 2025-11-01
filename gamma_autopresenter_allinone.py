#!/usr/bin/env python3
"""
=============================================================================
GAMMA AUTO-PRESENTER - ALL-IN-ONE VERSION
=============================================================================

This single file contains everything needed to:
1. Read all slides from your GAMMA presentation (from HTML)
2. Transcribe your voiceover audio with timestamps
3. Match slide content to audio timing
4. Run the presentation automatically

SETUP (one-time):
  pip install playwright whisper pygame
  playwright install chromium

USAGE:
  python gamma_autopresenter_allinone.py

=============================================================================
"""

import time
import json
import os
from datetime import datetime

# ============================================================================
# PART 1: GAMMA SLIDE READER
# ============================================================================

def read_gamma_slides(gamma_url):
    """
    Read all slides directly from GAMMA HTML
    Returns: List of slides with text content
    """
    from playwright.sync_api import sync_playwright

    print("\n" + "="*70)
    print("STEP 1: READING GAMMA SLIDES")
    print("="*70)
    print(f"\nOpening: {gamma_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        print("Loading presentation...")
        page.goto(gamma_url)

        print("Waiting for page to load (5 seconds)...")
        time.sleep(5)

        print("Reading all slides from HTML...")

        # Extract all slides from DOM
        slides_data = page.evaluate("""() => {
            const sections = document.querySelectorAll('section');
            const slides = [];

            sections.forEach((section, index) => {
                const text = section.innerText.trim();

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

        print(f"\n✅ Found {len(slides_data)} slides!")

        for slide in slides_data:
            preview = slide['preview'].replace('\n', ' ')
            print(f"   Slide {slide['slide_number']:2d}: {preview[:50]}...")

        browser.close()

    return slides_data


# ============================================================================
# PART 2: AUDIO TRANSCRIPTION
# ============================================================================

def transcribe_audio(audio_file):
    """
    Transcribe audio file with word-level timestamps using Whisper
    Returns: Dict with transcription and word timestamps
    """
    import whisper

    print("\n" + "="*70)
    print("STEP 2: TRANSCRIBING AUDIO")
    print("="*70)
    print(f"\nAudio file: {audio_file}")

    if not os.path.exists(audio_file):
        print(f"❌ ERROR: Audio file not found: {audio_file}")
        return None

    print("Loading Whisper model (this may take a minute)...")
    model = whisper.load_model("base")

    print("Transcribing audio (this may take several minutes)...")
    result = model.transcribe(audio_file, word_timestamps=True)

    # Extract word-level timestamps
    words_with_timestamps = []
    for segment in result['segments']:
        if 'words' in segment:
            for word_data in segment['words']:
                words_with_timestamps.append({
                    'word': word_data['word'].strip(),
                    'start': word_data['start'],
                    'end': word_data['end']
                })

    print(f"\n✅ Transcription complete!")
    print(f"   Total words: {len(words_with_timestamps)}")
    print(f"   Duration: {format_timestamp(result['segments'][-1]['end'])}")
    print(f"   Text: {result['text'][:100]}...")

    return {
        'full_text': result['text'],
        'words': words_with_timestamps,
        'duration': result['segments'][-1]['end'] if result['segments'] else 0
    }


# ============================================================================
# PART 3: CONTENT MATCHING
# ============================================================================

def match_slides_to_audio(slides, script_text, audio_data):
    """
    Match each slide to when it should appear in the audio
    Returns: Timeline with timestamps for each slide
    """
    from difflib import SequenceMatcher
    import re

    print("\n" + "="*70)
    print("STEP 3: MATCHING SLIDES TO AUDIO")
    print("="*70)

    timeline = []

    def normalize_text(text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def find_phrase_in_audio(phrase, audio_words):
        phrase_words = normalize_text(phrase).split()
        if len(phrase_words) == 0:
            return None

        best_match = None
        best_ratio = 0

        for i in range(len(audio_words) - len(phrase_words) + 1):
            window_words = [normalize_text(audio_words[j]['word'])
                          for j in range(i, min(i + len(phrase_words), len(audio_words)))]
            window_text = ' '.join(window_words)

            ratio = SequenceMatcher(None, ' '.join(phrase_words), window_text).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_match = {
                    'start_time': audio_words[i]['start'],
                    'similarity': ratio
                }

        return best_match

    for slide in slides:
        slide_num = slide['slide_number']
        slide_text = slide['text_content']

        # Get first meaningful line from slide
        lines = [line.strip() for line in slide_text.split('\n') if line.strip()]
        search_phrase = lines[0] if lines else slide_text[:50]

        print(f"\n📍 Slide {slide_num}: '{search_phrase[:40]}...'")

        # Find in audio
        audio_match = find_phrase_in_audio(search_phrase, audio_data['words'])

        if audio_match and audio_match['similarity'] > 0.5:
            timestamp = audio_match['start_time']
            print(f"   ✅ Found at {format_timestamp(timestamp)} (similarity: {audio_match['similarity']:.2f})")

            timeline.append({
                'slide_number': slide_num,
                'timestamp': timestamp,
                'matched': True,
                'slide_preview': search_phrase[:50]
            })
        else:
            print(f"   ⚠️  Could not match (low confidence)")
            timeline.append({
                'slide_number': slide_num,
                'timestamp': None,
                'matched': False,
                'slide_preview': search_phrase[:50]
            })

    matched_count = sum(1 for item in timeline if item['matched'])
    print(f"\n✅ Matched {matched_count}/{len(timeline)} slides to audio")

    return timeline


# ============================================================================
# PART 4: AUTOMATED PRESENTATION
# ============================================================================

def run_automated_presentation(gamma_url, timeline, audio_file):
    """
    Run the automated presentation with synchronized audio
    """
    from playwright.sync_api import sync_playwright
    import pygame

    print("\n" + "="*70)
    print("STEP 4: RUNNING AUTOMATED PRESENTATION")
    print("="*70)

    # Filter to only matched slides
    valid_timeline = [item for item in timeline if item['matched']]

    if not valid_timeline:
        print("❌ ERROR: No slides were matched to audio!")
        return

    print(f"\n📊 Timeline ready: {len(valid_timeline)} slides")
    for item in valid_timeline[:5]:
        print(f"   Slide {item['slide_number']} at {format_timestamp(item['timestamp'])}")

    print("\nOPENING GAMMA PRESENTATION...")
    print("When the browser opens, you have 5 seconds to get ready.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        # Open GAMMA
        page.goto(gamma_url)
        time.sleep(5)

        # Countdown
        for i in range(5, 0, -1):
            print(f"   Starting in {i}...")
            time.sleep(1)

        print("\n🎬 Entering presentation mode...")
        page.keyboard.down('Control')
        page.keyboard.down('Shift')
        page.keyboard.press('Enter')
        page.keyboard.up('Shift')
        page.keyboard.up('Control')
        time.sleep(5)

        print("💡 Entering spotlight mode...")
        page.keyboard.press('s')
        time.sleep(3)

        print("\n🎵 Starting audio and automated presentation!\n")

        # Initialize audio
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)

        # Start playback
        start_time = time.time()
        pygame.mixer.music.play()

        slide_index = 0
        next_timestamp = valid_timeline[slide_index]['timestamp']

        # Main loop
        while pygame.mixer.music.get_busy() or slide_index < len(valid_timeline):
            current_time = time.time() - start_time

            if slide_index < len(valid_timeline) and next_timestamp is not None:
                if current_time >= next_timestamp:
                    slide_num = valid_timeline[slide_index]['slide_number']
                    print(f"⏭️  [{format_timestamp(current_time)}] Advancing to Slide {slide_num}")

                    page.keyboard.press('Space')

                    slide_index += 1
                    next_timestamp = (valid_timeline[slide_index]['timestamp']
                                    if slide_index < len(valid_timeline) else None)

            time.sleep(0.05)

        print("\n✅ PRESENTATION COMPLETE!")
        print("   Press ESC to exit presentation mode")

        time.sleep(5)
        browser.close()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_timestamp(seconds):
    """Format seconds as MM:SS.mmm"""
    if seconds is None:
        return "??:??.???"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"


def save_results(slides, audio_data, timeline, output_file="gamma_presentation_data.json"):
    """Save all analysis results to a JSON file"""
    data = {
        'analyzed_at': datetime.now().isoformat(),
        'total_slides': len(slides),
        'matched_slides': sum(1 for t in timeline if t['matched']),
        'audio_duration': audio_data['duration'] if audio_data else 0,
        'slides': slides,
        'timeline': timeline
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 All data saved to: {output_file}")


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    print("\n" + "="*70)
    print("GAMMA AUTO-PRESENTER - ALL-IN-ONE")
    print("="*70)

    # Check dependencies
    try:
        from playwright.sync_api import sync_playwright
        import whisper
        import pygame
    except ImportError as e:
        print("\n❌ Missing required packages!")
        print("\nPlease install:")
        print("  pip install playwright openai-whisper pygame")
        print("  playwright install chromium")
        input("\nPress Enter to exit...")
        return

    # Get user inputs
    print("\n📋 CONFIGURATION\n")

    gamma_url = input("Enter GAMMA presentation URL: ").strip()
    if not gamma_url:
        gamma_url = "https://gamma.app/docs/Timing-Is-Everything-rv9g99f3t56viu5?mode=doc"
        print(f"   Using default: {gamma_url}")

    # For now, just test reading slides
    print("\n" + "="*70)
    print("MODE SELECTION")
    print("="*70)
    print("\n1. Test slide reading only (quick test)")
    print("2. Full automation with audio (requires script + audio)")

    mode = input("\nSelect mode (1 or 2): ").strip()

    if mode == "1":
        # Just read slides
        slides = read_gamma_slides(gamma_url)

        # Save results
        with open('gamma_slides_test.json', 'w', encoding='utf-8') as f:
            json.dump(slides, f, indent=2, ensure_ascii=False)

        print("\n💾 Slides saved to: gamma_slides_test.json")
        print("\n✅ Test complete!")

    elif mode == "2":
        # Full automation
        script_file = input("\nEnter path to script file (.txt): ").strip()
        audio_file = input("Enter path to audio file (.wav/.mp3): ").strip()

        if not os.path.exists(script_file):
            print(f"❌ Script file not found: {script_file}")
            input("\nPress Enter to exit...")
            return

        if not os.path.exists(audio_file):
            print(f"❌ Audio file not found: {audio_file}")
            input("\nPress Enter to exit...")
            return

        # Read script
        with open(script_file, 'r', encoding='utf-8') as f:
            script_text = f.read()

        # Execute full workflow
        slides = read_gamma_slides(gamma_url)
        audio_data = transcribe_audio(audio_file)

        if audio_data:
            timeline = match_slides_to_audio(slides, script_text, audio_data)
            save_results(slides, audio_data, timeline)

            # Ask if ready to run
            print("\n" + "="*70)
            choice = input("\nRun automated presentation now? (y/n): ").strip().lower()

            if choice == 'y':
                run_automated_presentation(gamma_url, timeline, audio_file)
            else:
                print("\n✅ Analysis complete!")
                print("   Run presentation later by selecting mode 2 again.")

    else:
        print("Invalid selection.")

    input("\n\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter to exit...")
