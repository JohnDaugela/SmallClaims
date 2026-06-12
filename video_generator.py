#!/usr/bin/env python3
"""
Video Generator - Creates MP4 from storyboard data
Uses moviepy to combine screenshots with transitions and audio
"""

import json
import os
from pathlib import Path


def generate_video(storyboard, output_path=None, progress_callback=None):
    from moviepy import (
        ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
    )

    if output_path is None:
        output_path = os.path.join(storyboard['output_dir'], "video.mp4")

    scenes = storyboard['scenes']
    audio_file = storyboard['audio_file']

    if not scenes:
        raise ValueError("No scenes in storyboard")

    if progress_callback:
        progress_callback("Loading audio...")

    audio_clip = AudioFileClip(audio_file)
    total_scenes = len(scenes)

    clips = []
    for i, scene in enumerate(scenes):
        if progress_callback:
            progress_callback(f"Processing scene {i+1}/{total_scenes}...")

        screenshot = scene.get('screenshot', '')
        if not screenshot or not os.path.exists(screenshot):
            continue

        duration = scene.get('duration', 2.0)
        if duration <= 0:
            duration = 0.5

        clip = ImageClip(screenshot, duration=duration)

        transition_type = scene.get('transition_type', 'fade')
        transition_time = scene.get('transition_time', 0.25)

        if transition_time > 0 and i > 0:
            clip = apply_transition(clip, transition_type, transition_time)

        clips.append(clip)

    if not clips:
        raise ValueError("No valid scenes to render")

    if progress_callback:
        progress_callback("Combining scenes...")

    final_video = concatenate_videoclips(clips, method="compose")

    # Trim video to match audio duration
    if final_video.duration > audio_clip.duration:
        final_video = final_video.with_end(audio_clip.duration)

    final_video = final_video.with_audio(
        audio_clip.with_end(min(audio_clip.duration, final_video.duration))
    )

    if progress_callback:
        progress_callback("Rendering video (this may take a few minutes)...")

    final_video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        logger=None
    )

    # Cleanup
    audio_clip.close()
    final_video.close()
    for clip in clips:
        clip.close()

    if progress_callback:
        progress_callback(f"Video saved to: {output_path}")

    return output_path


def apply_transition(clip, transition_type, transition_time):
    if transition_time <= 0:
        return clip

    try:
        if transition_type in ('fade', 'crossfade', 'wipe'):
            clip = clip.with_effects([
                __import__('moviepy').video.fx.CrossFadeIn(transition_time)
            ])
        elif transition_type == 'slide':
            clip = clip.with_effects([
                __import__('moviepy').video.fx.CrossFadeIn(transition_time)
            ])
    except Exception:
        pass

    return clip


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python video_generator.py <storyboard.json> [output.mp4]")
        return

    storyboard_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    with open(storyboard_path, 'r', encoding='utf-8') as f:
        storyboard = json.load(f)

    def progress(msg):
        print(f"  {msg}")

    output = generate_video(storyboard, output_path, progress_callback=progress)
    print(f"\nVideo created: {output}")


if __name__ == "__main__":
    main()
