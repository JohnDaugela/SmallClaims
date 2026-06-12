#!/usr/bin/env python3
"""
Storyboard Generator - Backend for GAMMA Storyboard Studio
Opens GAMMA, captures screenshots, transcribes audio, matches script to scenes
"""

import os
import re
import json
import time
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher


def create_output_directory(base_dir=None):
    if not base_dir:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_dir, timestamp)
    screenshots_dir = os.path.join(output_dir, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    return output_dir, screenshots_dir


def capture_gamma_screenshots(gamma_url, screenshots_dir, progress_callback=None):
    from playwright.sync_api import sync_playwright

    if '?mode=present' not in gamma_url:
        if '?mode=' in gamma_url:
            gamma_url = re.sub(r'\?mode=\w+', '?mode=present', gamma_url)
        elif '?' in gamma_url:
            gamma_url += '&mode=present'
        else:
            gamma_url += '?mode=present'

    screenshots = []
    slides_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        if progress_callback:
            progress_callback("Opening GAMMA presentation...")
        page.goto(gamma_url)
        time.sleep(10)

        # Activate spotlight mode
        if progress_callback:
            progress_callback("Activating spotlight mode...")
        try:
            spotlight_button = page.locator("button:has-text('Spotlight')").first
            spotlight_button.click()
            time.sleep(3)
        except Exception:
            page.keyboard.press('s')
            time.sleep(3)

        # Activate fullscreen
        if progress_callback:
            progress_callback("Activating fullscreen...")
        try:
            selectors = [
                "button[aria-label='Enter full screen']",
                "button[aria-label*='full screen' i]",
                "button[aria-label*='fullscreen' i]"
            ]
            for selector in selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.count() > 0:
                        btn.click(timeout=2000)
                        time.sleep(3)
                        break
                except:
                    continue
        except Exception:
            try:
                page.evaluate("document.body.requestFullscreen()")
                time.sleep(3)
            except Exception:
                page.keyboard.press('F11')
                time.sleep(3)

        # Read all slides to know total count
        slides_data = page.evaluate("""() => {
            const cards = document.querySelectorAll('[data-card-id]');
            const slides = [];
            cards.forEach((card, index) => {
                const text = card.innerText.trim();
                if (text && text.length > 0) {
                    slides.push({
                        slide_number: index + 1,
                        card_id: card.getAttribute('data-card-id'),
                        text_content: text,
                        preview: text.substring(0, 100)
                    });
                }
            });
            return slides;
        }""")

        total_slides = len(slides_data)
        if progress_callback:
            progress_callback(f"Found {total_slides} slides. Capturing screenshots...")

        # Capture screenshot of first slide (already visible)
        screenshot_path = os.path.join(screenshots_dir, "scene_001.png")
        page.screenshot(path=screenshot_path)
        screenshots.append(screenshot_path)
        if progress_callback:
            progress_callback(f"Captured screenshot 1/{total_slides}")

        # Click through and capture each subsequent slide
        for i in range(1, total_slides):
            page.keyboard.press('Space')
            time.sleep(1.5)

            screenshot_path = os.path.join(screenshots_dir, f"scene_{i+1:03d}.png")
            page.screenshot(path=screenshot_path)
            screenshots.append(screenshot_path)

            if progress_callback:
                progress_callback(f"Captured screenshot {i+1}/{total_slides}")

        browser.close()

    return screenshots, slides_data


def transcribe_audio(audio_file, progress_callback=None):
    import whisper

    if progress_callback:
        progress_callback("Loading Whisper model...")

    model = whisper.load_model("base")

    if progress_callback:
        progress_callback("Transcribing audio (this may take a minute)...")

    result = model.transcribe(audio_file, word_timestamps=True, verbose=False)

    words = []
    for segment in result['segments']:
        if 'words' in segment:
            for word_data in segment['words']:
                words.append({
                    'word': word_data['word'].strip(),
                    'start': word_data['start'],
                    'end': word_data['end']
                })

    duration = result['segments'][-1]['end'] if result['segments'] else 0

    if progress_callback:
        progress_callback(f"Transcription complete! {len(words)} words, {duration:.1f}s")

    return words, duration, result['text']


def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def find_sentence_timestamp(sentence, word_timestamps):
    sentence_words = normalize_text(sentence).split()
    if not sentence_words:
        return None, None

    search_len = min(len(sentence_words), 8)
    search_phrase = ' '.join(sentence_words[:search_len])

    best_match_start = None
    best_match_end = None
    best_ratio = 0

    for i in range(len(word_timestamps) - search_len + 1):
        window = ' '.join(normalize_text(word_timestamps[j]['word'])
                         for j in range(i, i + search_len))
        ratio = SequenceMatcher(None, search_phrase, window).ratio()

        if ratio > best_ratio:
            best_ratio = ratio
            best_match_start = word_timestamps[i]['start']
            end_idx = min(i + len(sentence_words) - 1, len(word_timestamps) - 1)
            best_match_end = word_timestamps[end_idx]['end']

    if best_ratio >= 0.5:
        return best_match_start, best_match_end
    return None, None


def match_script_to_scenes(script_text, slides_data, word_timestamps, audio_duration):
    sentences = split_into_sentences(script_text)

    # Get timestamps for each sentence
    sentence_timings = []
    for sentence in sentences:
        start, end = find_sentence_timestamp(sentence, word_timestamps)
        sentence_timings.append({
            'sentence': sentence,
            'start': start,
            'end': end
        })

    # Sort sentences by start time (keep originals for unmatched)
    timed_sentences = sorted(
        [s for s in sentence_timings if s['start'] is not None],
        key=lambda x: x['start']
    )
    untimed_sentences = [s for s in sentence_timings if s['start'] is None]

    num_scenes = len(slides_data)
    if num_scenes == 0:
        return []

    # Divide audio duration into equal segments for scene boundaries
    scene_duration = audio_duration / num_scenes
    scenes = []

    for i in range(num_scenes):
        scene_start = i * scene_duration
        scene_end = (i + 1) * scene_duration

        # Find sentences that fall within this scene's time range
        scene_sentences = []
        for st in timed_sentences:
            if scene_start <= st['start'] < scene_end:
                scene_sentences.append(st['sentence'])

        scenes.append({
            'scene_number': i + 1,
            'script_sentences': scene_sentences,
            'start_time': round(scene_start, 3),
            'end_time': round(scene_end, 3),
            'duration': round(scene_end - scene_start, 3),
        })

    # Distribute any untimed sentences to the first empty scene or append to last
    for ut in untimed_sentences:
        placed = False
        for scene in scenes:
            if not scene['script_sentences']:
                scene['script_sentences'].append(ut['sentence'])
                placed = True
                break
        if not placed and scenes:
            scenes[-1]['script_sentences'].append(ut['sentence'])

    return scenes


def generate_storyboard(gamma_url, script_file, audio_file,
                        output_dir=None, settings=None, progress_callback=None):
    if settings is None:
        settings = {
            'default_transition_type': 'fade',
            'default_transition_time': 0.25
        }

    # Create output directory
    output_dir, screenshots_dir = create_output_directory(output_dir)

    if progress_callback:
        progress_callback("Starting storyboard generation...")

    # Read script
    with open(script_file, 'r', encoding='utf-8') as f:
        script_text = f.read()

    # Capture GAMMA screenshots
    screenshots, slides_data = capture_gamma_screenshots(
        gamma_url, screenshots_dir, progress_callback
    )

    # Transcribe audio
    word_timestamps, audio_duration, full_transcript = transcribe_audio(
        audio_file, progress_callback
    )

    # Match script to scenes
    if progress_callback:
        progress_callback("Matching script to scenes...")
    scenes = match_script_to_scenes(script_text, slides_data, word_timestamps, audio_duration)

    # Build storyboard
    cumulative = 0
    for i, scene in enumerate(scenes):
        scene['screenshot'] = screenshots[i] if i < len(screenshots) else ""
        scene['transition_type'] = settings['default_transition_type']
        scene['transition_time'] = settings['default_transition_time']
        cumulative += scene['duration']
        scene['cumulative_duration'] = round(cumulative, 3)

    storyboard = {
        'project_name': Path(script_file).stem,
        'created_at': datetime.now().isoformat(),
        'gamma_url': gamma_url,
        'script_file': os.path.abspath(script_file),
        'audio_file': os.path.abspath(audio_file),
        'audio_duration': audio_duration,
        'output_dir': output_dir,
        'settings': settings,
        'scenes': scenes
    }

    # Save storyboard
    storyboard_path = os.path.join(output_dir, "storyboard.json")
    with open(storyboard_path, 'w', encoding='utf-8') as f:
        json.dump(storyboard, f, indent=2, ensure_ascii=False)

    if progress_callback:
        progress_callback(f"Storyboard complete! {len(scenes)} scenes saved.")

    return storyboard, storyboard_path


def recalculate_timings(storyboard):
    word_timestamps_needed = False
    total_sentences = sum(len(s['script_sentences']) for s in storyboard['scenes'])

    if total_sentences == 0:
        # Even distribution
        num_scenes = len(storyboard['scenes'])
        if num_scenes == 0:
            return storyboard
        scene_dur = storyboard['audio_duration'] / num_scenes
        cumulative = 0
        for i, scene in enumerate(storyboard['scenes']):
            scene['start_time'] = round(i * scene_dur, 3)
            scene['end_time'] = round((i + 1) * scene_dur, 3)
            scene['duration'] = round(scene_dur, 3)
            cumulative += scene['duration']
            scene['cumulative_duration'] = round(cumulative, 3)
        return storyboard

    # Distribute duration proportionally to number of sentences
    total_dur = storyboard['audio_duration']
    cumulative = 0
    for scene in storyboard['scenes']:
        n = max(len(scene['script_sentences']), 1)
        proportion = n / max(total_sentences, 1)
        scene['duration'] = round(total_dur * proportion, 3)
        scene['start_time'] = round(cumulative, 3)
        cumulative += scene['duration']
        scene['end_time'] = round(cumulative, 3)
        scene['cumulative_duration'] = round(cumulative, 3)

    return storyboard
