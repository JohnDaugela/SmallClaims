#!/usr/bin/env python3
"""
Automated GAMMA Presenter
Plays audio and automatically advances slides at the correct times
"""

import json
import time
import pyautogui
import pygame
import threading
import os

class AutomatedPresenter:
    def __init__(self, timeline_file, audio_file):
        self.timeline_file = timeline_file
        self.audio_file = audio_file
        self.timeline = None
        self.audio_length = 0

    def load_timeline(self):
        """Load the presentation timeline"""
        print("=" * 70)
        print("AUTOMATED GAMMA PRESENTER")
        print("=" * 70 + "\n")

        print(f"📊 Loading timeline: {self.timeline_file}")
        with open(self.timeline_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.timeline = data['timeline']
        print(f"   ✅ Loaded {len(self.timeline)} slide timings")
        print(f"   ✅ {data['matched_slides']}/{data['total_slides']} slides matched\n")

        # Filter out unmatched slides
        self.timeline = [item for item in self.timeline if item['matched']]

        return self.timeline

    def initialize_audio(self):
        """Initialize pygame mixer for audio playback"""
        pygame.mixer.init()
        pygame.mixer.music.load(self.audio_file)

        # Get audio length
        sound = pygame.mixer.Sound(self.audio_file)
        self.audio_length = sound.get_length()

        print(f"🎵 Audio loaded: {self.audio_file}")
        print(f"   Duration: {self.format_timestamp(self.audio_length)}\n")

    def countdown(self, seconds=5):
        """Give user time to focus on browser window"""
        print(f"\n⏰ You have {seconds} seconds to focus on your GAMMA browser window...")
        for i in range(seconds, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        print("   🚀 Starting presentation!\n")

    def setup_presentation(self):
        """Enter presentation mode and spotlight mode"""
        print("🎬 Entering presentation mode (Ctrl+Shift+Enter)...")
        pyautogui.hotkey('ctrl', 'shift', 'enter')
        time.sleep(3)

        print("💡 Entering spotlight mode (S)...")
        pyautogui.press('s')
        time.sleep(2)

    def run_presentation(self):
        """Execute the automated presentation"""
        print("=" * 70)
        print("STARTING AUTOMATED PRESENTATION")
        print("=" * 70 + "\n")

        print("INSTRUCTIONS:")
        print("1. Open your GAMMA presentation in a browser")
        print("2. Make sure the browser window is visible")
        print("3. Press Enter when ready...")
        input()

        self.countdown(5)

        # Setup presentation
        self.setup_presentation()

        print("\n" + "=" * 70)
        print("PRESENTATION RUNNING")
        print("=" * 70 + "\n")

        # Start audio playback
        print("🎵 Starting audio playback...\n")
        start_time = time.time()
        pygame.mixer.music.play()

        # Track which slides we've advanced
        slide_index = 0
        next_timestamp = self.timeline[slide_index]['timestamp'] if slide_index < len(self.timeline) else None

        # Main presentation loop
        while pygame.mixer.music.get_busy() or slide_index < len(self.timeline):
            current_time = time.time() - start_time

            # Check if it's time to advance to the next slide
            if slide_index < len(self.timeline) and next_timestamp is not None:
                if current_time >= next_timestamp:
                    slide_num = self.timeline[slide_index]['slide_number']
                    print(f"⏭️  [{self.format_timestamp(current_time)}] Advancing to Slide {slide_num}")
                    print(f"   Preview: {self.timeline[slide_index]['slide_text_preview'][:50]}...")

                    pyautogui.press('space')

                    slide_index += 1
                    next_timestamp = self.timeline[slide_index]['timestamp'] if slide_index < len(self.timeline) else None

            # Small sleep to prevent busy waiting
            time.sleep(0.05)

        print("\n✅ PRESENTATION COMPLETE!")
        print("   Press ESC to exit presentation mode")

    @staticmethod
    def format_timestamp(seconds):
        """Format seconds as MM:SS.mmm"""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:06.3f}"

def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python automated_presenter.py <timeline.json> <audio_file>")
        print("\nExample: python automated_presenter.py presentation_timeline.json voiceover.wav")
        return

    timeline_file = sys.argv[1]
    audio_file = sys.argv[2]

    # Check files exist
    if not os.path.exists(timeline_file):
        print(f"❌ Error: Timeline file not found: {timeline_file}")
        return

    if not os.path.exists(audio_file):
        print(f"❌ Error: Audio file not found: {audio_file}")
        return

    # Create presenter
    presenter = AutomatedPresenter(timeline_file, audio_file)

    # Load timeline
    presenter.load_timeline()

    # Initialize audio
    presenter.initialize_audio()

    # Run presentation
    presenter.run_presentation()

if __name__ == "__main__":
    main()
