#!/usr/bin/env python3
"""
GAMMA Rehearse Timings - Record and playback presentation timings
Like PowerPoint's Rehearse Timings feature, but for GAMMA presentations
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import json
import time
import threading
from pathlib import Path
import whisper
from pynput import keyboard
import pyautogui

class GammaRehearseTimings:
    def __init__(self, root):
        self.root = root
        self.root.title("GAMMA Rehearse Timings")
        self.root.geometry("1200x800")

        # Data storage
        self.script_text = ""
        self.audio_file = None
        self.words_with_timestamps = []
        self.spacebar_timestamps = []
        self.current_time = 0
        self.is_playing = False
        self.is_recording = False
        self.audio_duration = 0

        # Whisper model
        self.whisper_model = None

        # Initialize pygame for audio
        pygame.mixer.init()

        # Create UI
        self.create_widgets()

        # Keyboard listener for spacebar
        self.keyboard_listener = None

    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab 1: Setup & Recording
        self.recording_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recording_frame, text="1. Record Timings")
        self.create_recording_tab()

        # Tab 2: Review & Edit
        self.review_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.review_frame, text="2. Review & Edit")
        self.create_review_tab()

        # Tab 3: Playback
        self.playback_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.playback_frame, text="3. Playback")
        self.create_playback_tab()

    def create_recording_tab(self):
        # File selection section
        file_frame = ttk.LabelFrame(self.recording_frame, text="Files", padding=10)
        file_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(file_frame, text="Load Script (.txt)",
                   command=self.load_script).pack(side='left', padx=5)
        ttk.Button(file_frame, text="Load Audio (.wav/.mp3)",
                   command=self.load_audio).pack(side='left', padx=5)
        ttk.Button(file_frame, text="Transcribe Audio",
                   command=self.transcribe_audio).pack(side='left', padx=5)

        self.status_label = ttk.Label(file_frame, text="No files loaded")
        self.status_label.pack(side='left', padx=20)

        # Script display with highlighting
        script_frame = ttk.LabelFrame(self.recording_frame, text="Script (Highlighted as Playing)", padding=10)
        script_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create text widget with scrollbar
        scroll = ttk.Scrollbar(script_frame)
        scroll.pack(side='right', fill='y')

        self.script_text_widget = tk.Text(script_frame, wrap='word',
                                          yscrollcommand=scroll.set,
                                          font=('Arial', 14))
        self.script_text_widget.pack(fill='both', expand=True)
        scroll.config(command=self.script_text_widget.yview)

        # Configure text tags for highlighting
        self.script_text_widget.tag_config('highlight', background='yellow',
                                           foreground='black', font=('Arial', 14, 'bold'))
        self.script_text_widget.tag_config('normal', font=('Arial', 14))

        # Audio controls
        control_frame = ttk.LabelFrame(self.recording_frame, text="Recording Controls", padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)

        self.play_button = ttk.Button(control_frame, text="▶ Start Recording",
                                       command=self.start_recording, state='disabled')
        self.play_button.pack(side='left', padx=5)

        self.pause_button = ttk.Button(control_frame, text="⏸ Pause",
                                        command=self.pause_recording, state='disabled')
        self.pause_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(control_frame, text="⏹ Stop",
                                       command=self.stop_recording, state='disabled')
        self.stop_button.pack(side='left', padx=5)

        # Time display
        self.time_label = ttk.Label(control_frame, text="00:00.0 / 00:00.0",
                                     font=('Arial', 12))
        self.time_label.pack(side='left', padx=20)

        # Spacebar counter
        self.spacebar_label = ttk.Label(control_frame, text="Spacebar presses: 0",
                                        font=('Arial', 12, 'bold'))
        self.spacebar_label.pack(side='left', padx=20)

        # Instructions
        instructions = ttk.Label(control_frame,
                                text="Press SPACEBAR to mark slide changes while audio plays",
                                foreground='blue')
        instructions.pack(side='left', padx=20)

        # Timeline visualization
        timeline_frame = ttk.LabelFrame(self.recording_frame, text="Timeline", padding=10)
        timeline_frame.pack(fill='x', padx=10, pady=5)

        self.timeline_canvas = tk.Canvas(timeline_frame, height=60, bg='white')
        self.timeline_canvas.pack(fill='x')

    def create_review_tab(self):
        # Timeline editor
        timeline_frame = ttk.LabelFrame(self.review_frame, text="Timeline - Click markers to adjust", padding=10)
        timeline_frame.pack(fill='x', padx=10, pady=5)

        self.review_timeline_canvas = tk.Canvas(timeline_frame, height=100, bg='white')
        self.review_timeline_canvas.pack(fill='x')
        self.review_timeline_canvas.bind('<Button-1>', self.timeline_click)
        self.review_timeline_canvas.bind('<B1-Motion>', self.timeline_drag)

        # Selected marker info
        info_frame = ttk.LabelFrame(self.review_frame, text="Selected Marker", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(info_frame, text="Spacebar #:").grid(row=0, column=0, sticky='w', padx=5)
        self.marker_num_label = ttk.Label(info_frame, text="N/A", font=('Arial', 11, 'bold'))
        self.marker_num_label.grid(row=0, column=1, sticky='w', padx=5)

        ttk.Label(info_frame, text="Timestamp:").grid(row=1, column=0, sticky='w', padx=5)
        self.marker_time_label = ttk.Label(info_frame, text="N/A", font=('Arial', 11, 'bold'))
        self.marker_time_label.grid(row=1, column=1, sticky='w', padx=5)

        ttk.Button(info_frame, text="Delete Marker",
                   command=self.delete_selected_marker).grid(row=0, column=2, padx=20)
        ttk.Button(info_frame, text="Refresh Timeline",
                   command=self.draw_review_timeline).grid(row=1, column=2, padx=20)

        # Next words preview
        preview_frame = ttk.LabelFrame(self.review_frame,
                                       text="Words After This Spacebar Press", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=5)

        scroll = ttk.Scrollbar(preview_frame)
        scroll.pack(side='right', fill='y')

        self.preview_text_widget = tk.Text(preview_frame, wrap='word',
                                           yscrollcommand=scroll.set,
                                           font=('Arial', 12), height=10)
        self.preview_text_widget.pack(fill='both', expand=True)
        scroll.config(command=self.preview_text_widget.yview)

        # Save/Load timeline
        save_frame = ttk.Frame(self.review_frame)
        save_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(save_frame, text="💾 Save Timeline",
                   command=self.save_timeline).pack(side='left', padx=5)
        ttk.Button(save_frame, text="📂 Load Timeline",
                   command=self.load_timeline).pack(side='left', padx=5)

        self.selected_marker = None

    def create_playback_tab(self):
        # Instructions
        instructions = ttk.Label(self.playback_frame,
                                text="1. Open GAMMA in presentation mode on your other monitor\n"
                                     "2. Click in the GAMMA window to give it focus\n"
                                     "3. Click 'Start Playback' below\n"
                                     "4. Audio will play and spacebar will auto-press at your recorded times",
                                font=('Arial', 11), justify='left', padding=20)
        instructions.pack(fill='x')

        # Countdown frame
        countdown_frame = ttk.LabelFrame(self.playback_frame, text="Countdown", padding=20)
        countdown_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(countdown_frame, text="Countdown before starting:").pack(side='left', padx=5)
        self.countdown_var = tk.StringVar(value="5")
        countdown_spinbox = ttk.Spinbox(countdown_frame, from_=0, to=10,
                                        textvariable=self.countdown_var, width=5)
        countdown_spinbox.pack(side='left', padx=5)
        ttk.Label(countdown_frame, text="seconds").pack(side='left', padx=5)

        # Control buttons
        control_frame = ttk.LabelFrame(self.playback_frame, text="Playback Controls", padding=20)
        control_frame.pack(fill='x', padx=10, pady=5)

        self.playback_button = ttk.Button(control_frame, text="▶ Start Playback",
                                          command=self.start_playback,
                                          state='disabled')
        self.playback_button.pack(pady=10)

        # Status display
        status_frame = ttk.LabelFrame(self.playback_frame, text="Status", padding=20)
        status_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.playback_status = tk.Text(status_frame, height=15, font=('Courier', 10))
        self.playback_status.pack(fill='both', expand=True)

    def load_script(self):
        filepath = filedialog.askopenfilename(
            title="Select Script File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.script_text = f.read()

            self.script_text_widget.delete('1.0', 'end')
            self.script_text_widget.insert('1.0', self.script_text)

            self.status_label.config(text=f"Script loaded: {Path(filepath).name}")
            self.check_ready_to_record()

    def load_audio(self):
        filepath = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio files", "*.wav *.mp3"), ("All files", "*.*")]
        )
        if filepath:
            self.audio_file = filepath

            # Load audio to get duration
            try:
                pygame.mixer.music.load(self.audio_file)
                # Get duration using pygame
                sound = pygame.mixer.Sound(self.audio_file)
                self.audio_duration = sound.get_length()

                self.status_label.config(
                    text=f"Audio loaded: {Path(filepath).name} ({self.format_time(self.audio_duration)})"
                )
                self.check_ready_to_record()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load audio: {e}")

    def transcribe_audio(self):
        if not self.audio_file:
            messagebox.showwarning("No Audio", "Please load an audio file first")
            return

        self.status_label.config(text="Transcribing audio... (this may take a minute)")
        self.root.update()

        # Run transcription in thread to avoid freezing UI
        def transcribe():
            try:
                if not self.whisper_model:
                    self.whisper_model = whisper.load_model("base")

                result = self.whisper_model.transcribe(
                    self.audio_file,
                    word_timestamps=True
                )

                # Extract word-level timestamps
                self.words_with_timestamps = []
                for segment in result['segments']:
                    if 'words' in segment:
                        for word_data in segment['words']:
                            self.words_with_timestamps.append({
                                'word': word_data['word'].strip(),
                                'start': word_data['start'],
                                'end': word_data['end']
                            })

                self.root.after(0, lambda: self.status_label.config(
                    text=f"Transcription complete! {len(self.words_with_timestamps)} words"
                ))
                self.root.after(0, self.check_ready_to_record)

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Transcription failed: {e}"))

        threading.Thread(target=transcribe, daemon=True).start()

    def check_ready_to_record(self):
        if self.script_text and self.audio_file and self.words_with_timestamps:
            self.play_button.config(state='normal')
            self.playback_button.config(state='normal')

    def start_recording(self):
        self.is_recording = True
        self.is_playing = True
        self.spacebar_timestamps = []
        self.current_time = 0

        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

        # Update UI
        self.play_button.config(state='disabled')
        self.pause_button.config(state='normal')
        self.stop_button.config(state='normal')

        # Start audio
        pygame.mixer.music.load(self.audio_file)
        pygame.mixer.music.play()

        # Start update loop
        self.update_recording()

    def pause_recording(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.pause_button.config(text="▶ Resume")
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.pause_button.config(text="⏸ Pause")
            self.update_recording()

    def stop_recording(self):
        self.is_recording = False
        self.is_playing = False

        pygame.mixer.music.stop()

        if self.keyboard_listener:
            self.keyboard_listener.stop()

        # Update UI
        self.play_button.config(state='normal', text="▶ Start Recording")
        self.pause_button.config(state='disabled', text="⏸ Pause")
        self.stop_button.config(state='disabled')

        # Clear highlighting
        self.script_text_widget.tag_remove('highlight', '1.0', 'end')

        messagebox.showinfo("Recording Complete",
                           f"Recorded {len(self.spacebar_timestamps)} spacebar presses!\n"
                           f"Go to 'Review & Edit' tab to adjust timings.")

        # Switch to review tab and draw timeline
        self.notebook.select(1)
        self.draw_review_timeline()

    def update_recording(self):
        if not self.is_playing:
            return

        # Update current time
        self.current_time = pygame.mixer.music.get_pos() / 1000.0

        # Update time label
        self.time_label.config(
            text=f"{self.format_time(self.current_time)} / {self.format_time(self.audio_duration)}"
        )

        # Highlight current word
        self.highlight_current_word()

        # Draw timeline
        self.draw_timeline()

        # Check if audio finished
        if not pygame.mixer.music.get_busy():
            self.stop_recording()
            return

        # Continue updating
        self.root.after(50, self.update_recording)

    def highlight_current_word(self):
        # Find current word based on timestamp
        current_word_idx = -1
        for i, word_data in enumerate(self.words_with_timestamps):
            if word_data['start'] <= self.current_time <= word_data['end']:
                current_word_idx = i
                break

        if current_word_idx >= 0:
            # Remove previous highlighting
            self.script_text_widget.tag_remove('highlight', '1.0', 'end')

            # Find word position in text and highlight
            word = self.words_with_timestamps[current_word_idx]['word']

            # Search for word in text (approximate matching)
            content = self.script_text_widget.get('1.0', 'end')
            # This is a simple implementation - could be improved
            # For now, just highlight the region based on word index
            start_char = sum(len(w['word']) + 1 for w in self.words_with_timestamps[:current_word_idx])
            end_char = start_char + len(word)

            try:
                self.script_text_widget.tag_add('highlight',
                                               f'1.0+{start_char}c',
                                               f'1.0+{end_char}c')
                # Auto-scroll to current word
                self.script_text_widget.see(f'1.0+{start_char}c')
            except:
                pass  # If positioning fails, just skip highlighting

    def on_key_press(self, key):
        if self.is_recording and key == keyboard.Key.space:
            # Record timestamp
            timestamp = self.current_time
            self.spacebar_timestamps.append(timestamp)

            # Update label
            self.root.after(0, lambda: self.spacebar_label.config(
                text=f"Spacebar presses: {len(self.spacebar_timestamps)}"
            ))

            # Flash the timeline
            self.root.after(0, self.draw_timeline)

    def draw_timeline(self):
        self.timeline_canvas.delete('all')

        if self.audio_duration == 0:
            return

        width = self.timeline_canvas.winfo_width()
        if width <= 1:
            width = 1000  # Default width

        height = 60

        # Draw progress bar
        progress_x = (self.current_time / self.audio_duration) * width
        self.timeline_canvas.create_rectangle(0, 20, progress_x, 40, fill='lightblue', outline='')
        self.timeline_canvas.create_rectangle(progress_x, 20, width, 40, fill='lightgray', outline='')

        # Draw spacebar markers
        for i, timestamp in enumerate(self.spacebar_timestamps):
            x = (timestamp / self.audio_duration) * width
            self.timeline_canvas.create_line(x, 0, x, height, fill='red', width=3)
            self.timeline_canvas.create_text(x, height - 10, text=str(i+1), fill='red', font=('Arial', 9, 'bold'))

        # Draw current position marker
        self.timeline_canvas.create_line(progress_x, 0, progress_x, height, fill='blue', width=2)

    def draw_review_timeline(self):
        self.review_timeline_canvas.delete('all')

        if self.audio_duration == 0:
            return

        width = self.review_timeline_canvas.winfo_width()
        if width <= 1:
            width = 1000

        height = 100

        # Draw background
        self.review_timeline_canvas.create_rectangle(0, 40, width, 60, fill='lightgray', outline='black')

        # Draw time markers
        for i in range(0, int(self.audio_duration) + 1, 10):
            x = (i / self.audio_duration) * width
            self.review_timeline_canvas.create_line(x, 35, x, 65, fill='gray')
            self.review_timeline_canvas.create_text(x, 25, text=self.format_time(i), font=('Arial', 8))

        # Draw spacebar markers (draggable)
        for i, timestamp in enumerate(self.spacebar_timestamps):
            x = (timestamp / self.audio_duration) * width

            # Draw marker
            marker_id = self.review_timeline_canvas.create_oval(
                x-8, 42, x+8, 58,
                fill='red', outline='darkred', width=2,
                tags=f'marker_{i}'
            )
            text_id = self.review_timeline_canvas.create_text(
                x, 50, text=str(i+1),
                fill='white', font=('Arial', 10, 'bold'),
                tags=f'marker_{i}'
            )

            # Add timestamp label
            self.review_timeline_canvas.create_text(
                x, 75, text=self.format_time(timestamp),
                font=('Arial', 8), tags=f'marker_{i}'
            )

    def timeline_click(self, event):
        # Find clicked marker
        items = self.review_timeline_canvas.find_overlapping(event.x-10, event.y-10, event.x+10, event.y+10)

        for item in items:
            tags = self.review_timeline_canvas.gettags(item)
            for tag in tags:
                if tag.startswith('marker_'):
                    marker_num = int(tag.split('_')[1])
                    self.selected_marker = marker_num
                    self.show_marker_info(marker_num)
                    return

    def timeline_drag(self, event):
        if self.selected_marker is not None:
            # Update timestamp based on drag position
            width = self.review_timeline_canvas.winfo_width()
            new_time = (event.x / width) * self.audio_duration
            new_time = max(0, min(new_time, self.audio_duration))

            self.spacebar_timestamps[self.selected_marker] = new_time
            self.draw_review_timeline()
            self.show_marker_info(self.selected_marker)

    def show_marker_info(self, marker_num):
        timestamp = self.spacebar_timestamps[marker_num]

        self.marker_num_label.config(text=f"#{marker_num + 1}")
        self.marker_time_label.config(text=self.format_time(timestamp))

        # Show next words
        next_words = self.get_words_after_timestamp(timestamp, num_words=30)
        self.preview_text_widget.delete('1.0', 'end')
        self.preview_text_widget.insert('1.0', next_words)

    def get_words_after_timestamp(self, timestamp, num_words=30):
        words_after = []
        for word_data in self.words_with_timestamps:
            if word_data['start'] >= timestamp:
                words_after.append(word_data['word'])
                if len(words_after) >= num_words:
                    break

        return ' '.join(words_after) if words_after else "No words found after this timestamp"

    def delete_selected_marker(self):
        if self.selected_marker is not None:
            del self.spacebar_timestamps[self.selected_marker]
            self.selected_marker = None
            self.draw_review_timeline()
            self.marker_num_label.config(text="N/A")
            self.marker_time_label.config(text="N/A")
            self.preview_text_widget.delete('1.0', 'end')

    def save_timeline(self):
        if not self.spacebar_timestamps:
            messagebox.showwarning("No Timeline", "No spacebar timestamps to save")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save Timeline",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            data = {
                'audio_file': self.audio_file,
                'audio_duration': self.audio_duration,
                'spacebar_timestamps': self.spacebar_timestamps,
                'total_presses': len(self.spacebar_timestamps)
            }

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            messagebox.showinfo("Saved", f"Timeline saved to {Path(filepath).name}")

    def load_timeline(self):
        filepath = filedialog.askopenfilename(
            title="Load Timeline",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            with open(filepath, 'r') as f:
                data = json.load(f)

            self.spacebar_timestamps = data['spacebar_timestamps']
            self.audio_duration = data.get('audio_duration', 0)

            # If audio file is in the data, load it
            if 'audio_file' in data and Path(data['audio_file']).exists():
                self.audio_file = data['audio_file']
                pygame.mixer.music.load(self.audio_file)

            self.draw_review_timeline()
            messagebox.showinfo("Loaded", f"Timeline loaded with {len(self.spacebar_timestamps)} markers")
            self.playback_button.config(state='normal')

    def start_playback(self):
        if not self.audio_file or not self.spacebar_timestamps:
            messagebox.showwarning("Not Ready",
                                  "Please load audio and have spacebar timestamps recorded")
            return

        # Get countdown time
        countdown = int(self.countdown_var.get())

        self.playback_status.delete('1.0', 'end')
        self.playback_status.insert('end', f"Starting playback in {countdown} seconds...\n")
        self.playback_status.insert('end', "Make sure GAMMA window has focus!\n\n")

        # Disable button
        self.playback_button.config(state='disabled')

        def countdown_and_play():
            # Countdown
            for i in range(countdown, 0, -1):
                self.root.after(0, lambda i=i: self.playback_status.insert('end', f"{i}...\n"))
                time.sleep(1)

            self.root.after(0, lambda: self.playback_status.insert('end', "\n▶ PLAYBACK STARTED!\n\n"))

            # Start audio
            pygame.mixer.music.load(self.audio_file)
            pygame.mixer.music.play()

            start_time = time.time()
            marker_index = 0

            # Playback loop
            while pygame.mixer.music.get_busy() or marker_index < len(self.spacebar_timestamps):
                current_time = time.time() - start_time

                # Check if we need to press spacebar
                if marker_index < len(self.spacebar_timestamps):
                    next_marker_time = self.spacebar_timestamps[marker_index]

                    if current_time >= next_marker_time:
                        # Press spacebar
                        pyautogui.press('space')

                        marker_index += 1
                        self.root.after(0, lambda m=marker_index, t=next_marker_time:
                                       self.playback_status.insert('end',
                                                                  f"[{self.format_time(t)}] Pressed spacebar #{m}\n"))
                        self.root.after(0, lambda: self.playback_status.see('end'))

                time.sleep(0.05)  # Check every 50ms

            self.root.after(0, lambda: self.playback_status.insert('end', "\n✅ PLAYBACK COMPLETE!\n"))
            self.root.after(0, lambda: self.playback_button.config(state='normal'))

        # Run in thread
        threading.Thread(target=countdown_and_play, daemon=True).start()

    @staticmethod
    def format_time(seconds):
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins:02d}:{secs:05.2f}"

def main():
    root = tk.Tk()
    app = GammaRehearseTimings(root)
    root.mainloop()

if __name__ == "__main__":
    main()
