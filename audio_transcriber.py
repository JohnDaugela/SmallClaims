#!/usr/bin/env python3
"""
Audio Transcriber with Timestamps
Uses Whisper AI to transcribe audio and get word-level timestamps
"""

import json
import os
from datetime import datetime
import whisper

class AudioTranscriber:
    def __init__(self, audio_file, output_dir="audio_analysis"):
        self.audio_file = audio_file
        self.output_dir = output_dir
        self.transcription = None

        os.makedirs(output_dir, exist_ok=True)

    def transcribe(self, model_size="base"):
        """
        Transcribe audio file using Whisper
        model_size: tiny, base, small, medium, large
        """
        print("=" * 70)
        print("AUDIO TRANSCRIPTION")
        print("=" * 70)
        print(f"\n🎵 Audio file: {self.audio_file}")
        print(f"🤖 Loading Whisper model ({model_size})...")

        # Load Whisper model
        model = whisper.load_model(model_size)

        print(f"🎙️  Transcribing audio (this may take a few minutes)...")

        # Transcribe with word-level timestamps
        result = model.transcribe(
            self.audio_file,
            word_timestamps=True,
            verbose=False
        )

        self.transcription = result

        print("✅ Transcription complete!\n")

        return result

    def get_word_timestamps(self):
        """Extract word-level timestamps from transcription"""
        if not self.transcription:
            raise ValueError("No transcription available. Run transcribe() first.")

        words_with_timestamps = []

        for segment in self.transcription['segments']:
            if 'words' in segment:
                for word_data in segment['words']:
                    words_with_timestamps.append({
                        'word': word_data['word'].strip(),
                        'start': word_data['start'],
                        'end': word_data['end']
                    })

        return words_with_timestamps

    def save_transcription(self):
        """Save transcription to JSON and text files"""
        if not self.transcription:
            raise ValueError("No transcription available. Run transcribe() first.")

        # Full transcription text
        full_text = self.transcription['text']

        # Word timestamps
        words = self.get_word_timestamps()

        # Save JSON with all data
        json_file = os.path.join(self.output_dir, "transcription.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'audio_file': self.audio_file,
                'transcribed_at': datetime.now().isoformat(),
                'full_text': full_text,
                'total_words': len(words),
                'duration': self.transcription['segments'][-1]['end'] if self.transcription['segments'] else 0,
                'words': words
            }, f, indent=2, ensure_ascii=False)

        # Save readable text file
        text_file = os.path.join(self.output_dir, "transcription.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(full_text)

        # Save timestamped transcript
        timestamped_file = os.path.join(self.output_dir, "transcription_timestamped.txt")
        with open(timestamped_file, 'w', encoding='utf-8') as f:
            for word_data in words:
                timestamp = self.format_timestamp(word_data['start'])
                f.write(f"[{timestamp}] {word_data['word']}\n")

        print("=" * 70)
        print("TRANSCRIPTION SAVED")
        print("=" * 70)
        print(f"\n📄 Full text: {text_file}")
        print(f"⏱️  Timestamped: {timestamped_file}")
        print(f"📊 JSON data: {json_file}")
        print(f"\n🔢 Total words: {len(words)}")
        print(f"⏰ Duration: {self.format_timestamp(self.transcription['segments'][-1]['end'])}")

        return json_file

    @staticmethod
    def format_timestamp(seconds):
        """Format seconds as MM:SS.mmm"""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:06.3f}"

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python audio_transcriber.py <audio_file>")
        print("\nExample: python audio_transcriber.py my_voiceover.wav")
        return

    audio_file = sys.argv[1]

    if not os.path.exists(audio_file):
        print(f"❌ Error: Audio file not found: {audio_file}")
        return

    # Create transcriber
    transcriber = AudioTranscriber(audio_file)

    # Transcribe
    transcriber.transcribe(model_size="base")

    # Save results
    transcriber.save_transcription()

if __name__ == "__main__":
    main()
