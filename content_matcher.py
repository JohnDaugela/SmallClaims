#!/usr/bin/env python3
"""
Content Matcher
Matches GAMMA slides → Script → Audio timestamps
"""

import json
import os
from difflib import SequenceMatcher
import re

class ContentMatcher:
    def __init__(self, gamma_analysis_file, script_file, audio_transcription_file):
        self.gamma_analysis_file = gamma_analysis_file
        self.script_file = script_file
        self.audio_transcription_file = audio_transcription_file

        self.gamma_data = None
        self.script_text = None
        self.audio_data = None
        self.timeline = []

    def load_data(self):
        """Load all input files"""
        print("=" * 70)
        print("CONTENT MATCHER - Loading Data")
        print("=" * 70 + "\n")

        # Load GAMMA analysis
        print(f"📊 Loading GAMMA analysis: {self.gamma_analysis_file}")
        with open(self.gamma_analysis_file, 'r', encoding='utf-8') as f:
            self.gamma_data = json.load(f)
        print(f"   ✅ Found {self.gamma_data['total_slides']} slides\n")

        # Load script
        print(f"📄 Loading script: {self.script_file}")
        with open(self.script_file, 'r', encoding='utf-8') as f:
            self.script_text = f.read()
        print(f"   ✅ Script loaded ({len(self.script_text)} characters)\n")

        # Load audio transcription
        print(f"🎙️  Loading audio transcription: {self.audio_transcription_file}")
        with open(self.audio_transcription_file, 'r', encoding='utf-8') as f:
            self.audio_data = json.load(f)
        print(f"   ✅ Transcription loaded ({self.audio_data['total_words']} words)\n")

    def normalize_text(self, text):
        """Normalize text for matching (lowercase, remove extra whitespace, punctuation)"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        return text.strip()

    def find_text_in_script(self, slide_text, min_similarity=0.6):
        """Find where slide text appears in the script"""
        if not slide_text:
            return None

        normalized_slide = self.normalize_text(slide_text)

        # Extract key phrases from slide (first few words, typically titles/headers)
        words = normalized_slide.split()
        if len(words) == 0:
            return None

        # Try different phrase lengths
        for phrase_len in [min(len(words), 10), min(len(words), 5), min(len(words), 3)]:
            search_phrase = ' '.join(words[:phrase_len])

            # Search in script
            normalized_script = self.normalize_text(self.script_text)
            if search_phrase in normalized_script:
                position = normalized_script.index(search_phrase)
                return {
                    'phrase': search_phrase,
                    'position': position,
                    'similarity': 1.0
                }

        # If exact match not found, try fuzzy matching
        best_match = None
        best_ratio = 0

        normalized_script = self.normalize_text(self.script_text)
        script_words = normalized_script.split()

        # Search for best matching window
        for i in range(len(script_words) - len(words) + 1):
            window = ' '.join(script_words[i:i+len(words)])
            ratio = SequenceMatcher(None, normalized_slide[:100], window[:100]).ratio()

            if ratio > best_ratio and ratio >= min_similarity:
                best_ratio = ratio
                best_match = {
                    'phrase': window[:50],
                    'position': len(' '.join(script_words[:i])),
                    'similarity': ratio
                }

        return best_match

    def find_phrase_in_audio(self, phrase):
        """Find when a phrase is spoken in the audio"""
        if not phrase:
            return None

        phrase_words = self.normalize_text(phrase).split()
        if len(phrase_words) == 0:
            return None

        # Search for phrase in transcribed words
        audio_words = self.audio_data['words']

        best_match = None
        best_ratio = 0

        for i in range(len(audio_words) - len(phrase_words) + 1):
            window_words = [self.normalize_text(audio_words[j]['word']) for j in range(i, i + len(phrase_words))]
            window_text = ' '.join(window_words)

            ratio = SequenceMatcher(None, ' '.join(phrase_words), window_text).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_match = {
                    'start_time': audio_words[i]['start'],
                    'end_time': audio_words[i + len(phrase_words) - 1]['end'],
                    'matched_text': window_text,
                    'similarity': ratio
                }

        return best_match

    def generate_timeline(self):
        """Generate the complete timeline for spacebar presses"""
        print("=" * 70)
        print("GENERATING TIMELINE")
        print("=" * 70 + "\n")

        self.timeline = []

        for slide in self.gamma_data['slides']:
            slide_num = slide['slide_number']
            slide_text = slide['text_content']

            print(f"📍 Slide {slide_num}:")

            # Find in script
            script_match = self.find_text_in_script(slide_text)

            if not script_match:
                print(f"   ⚠️  Could not match to script")
                self.timeline.append({
                    'slide_number': slide_num,
                    'timestamp': None,
                    'matched': False,
                    'slide_text_preview': slide_text[:50]
                })
                continue

            print(f"   ✅ Found in script: '{script_match['phrase'][:40]}...' (similarity: {script_match['similarity']:.2f})")

            # Find in audio
            audio_match = self.find_phrase_in_audio(script_match['phrase'])

            if not audio_match:
                print(f"   ⚠️  Could not match to audio")
                self.timeline.append({
                    'slide_number': slide_num,
                    'timestamp': None,
                    'matched': False,
                    'script_phrase': script_match['phrase'],
                    'slide_text_preview': slide_text[:50]
                })
                continue

            timestamp = audio_match['start_time']
            print(f"   ⏱️  Audio timestamp: {self.format_timestamp(timestamp)}")
            print(f"   🎯 Matched: '{audio_match['matched_text'][:40]}...' (similarity: {audio_match['similarity']:.2f})")

            self.timeline.append({
                'slide_number': slide_num,
                'timestamp': timestamp,
                'matched': True,
                'script_phrase': script_match['phrase'],
                'audio_match': audio_match['matched_text'],
                'slide_text_preview': slide_text[:50],
                'script_similarity': script_match['similarity'],
                'audio_similarity': audio_match['similarity']
            })

            print()

        return self.timeline

    def save_timeline(self, output_file="presentation_timeline.json"):
        """Save the timeline to a JSON file"""
        output_data = {
            'gamma_presentation': self.gamma_data['gamma_url'],
            'script_file': self.script_file,
            'audio_file': self.audio_data['audio_file'],
            'total_slides': len(self.timeline),
            'matched_slides': sum(1 for item in self.timeline if item['matched']),
            'timeline': self.timeline
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print("=" * 70)
        print("TIMELINE GENERATED")
        print("=" * 70)
        print(f"\n✅ Matched {output_data['matched_slides']}/{output_data['total_slides']} slides")
        print(f"💾 Timeline saved to: {output_file}\n")

        # Show summary
        print("⏱️  TIMELINE SUMMARY:")
        print("-" * 70)
        for item in self.timeline:
            if item['matched']:
                print(f"   Slide {item['slide_number']:2d} at {self.format_timestamp(item['timestamp'])}: {item['slide_text_preview'][:40]}...")
            else:
                print(f"   Slide {item['slide_number']:2d} at ??????? (not matched): {item['slide_text_preview'][:40]}...")

        return output_file

    @staticmethod
    def format_timestamp(seconds):
        """Format seconds as MM:SS.mmm"""
        if seconds is None:
            return "??:??.???"
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:06.3f}"

def main():
    import sys

    if len(sys.argv) < 4:
        print("Usage: python content_matcher.py <gamma_analysis.json> <script.txt> <audio_transcription.json>")
        return

    gamma_file = sys.argv[1]
    script_file = sys.argv[2]
    audio_file = sys.argv[3]

    # Check files exist
    for f in [gamma_file, script_file, audio_file]:
        if not os.path.exists(f):
            print(f"❌ Error: File not found: {f}")
            return

    # Create matcher
    matcher = ContentMatcher(gamma_file, script_file, audio_file)

    # Load data
    matcher.load_data()

    # Generate timeline
    matcher.generate_timeline()

    # Save timeline
    matcher.save_timeline()

if __name__ == "__main__":
    main()
