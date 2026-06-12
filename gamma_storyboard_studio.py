#!/usr/bin/env python3
"""
GAMMA Storyboard Studio
Create storyboards and generate videos from GAMMA presentations
"""

import json
import os
import sys
import time
import threading
import subprocess
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    from PIL import Image, ImageTk
    import pygame
    HAS_GUI = True
except ImportError as e:
    HAS_GUI = False
    _import_error = str(e)


# ============================================================================
# SETTINGS
# ============================================================================

DEFAULT_SETTINGS = {
    'default_transition_type': 'fade',
    'default_transition_time': 0.25,
    'video_resolution': '1920x1080',
    'video_fps': 24,
    'output_folder': ''
}

TRANSITION_TYPES = ['fade', 'crossfade', 'slide', 'wipe']

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'studio_settings.json')


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                saved = json.load(f)
            settings = DEFAULT_SETTINGS.copy()
            settings.update(saved)
            return settings
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class StoryboardStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("GAMMA Storyboard Studio")
        self.root.geometry("1300x850")
        self.root.minsize(1000, 700)

        self.settings = load_settings()
        self.storyboard = None
        self.storyboard_path = None
        self.thumbnails = {}
        self.is_previewing = False
        self.preview_start_time = 0

        self.audio_available = False
        try:
            pygame.mixer.init()
            self.audio_available = True
        except Exception:
            pass

        self.setup_styles()
        self.create_menu_bar()
        self.create_main_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))
        style.configure('Big.TButton', font=('Arial', 12, 'bold'), padding=10)
        style.configure('Scene.TFrame', relief='groove', borderwidth=1)

    def create_menu_bar(self):
        top_bar = ttk.Frame(self.root)
        top_bar.pack(fill='x', padx=5, pady=2)

        ttk.Label(top_bar, text="GAMMA Storyboard Studio",
                  style='Title.TLabel').pack(side='left', padx=10)

        settings_btn = ttk.Button(top_bar, text="⚙ Settings",
                                  command=self.open_settings)
        settings_btn.pack(side='right', padx=10)

    def create_main_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        self.input_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.input_frame, text="  Input  ")
        self.create_input_tab()

        self.storyboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.storyboard_frame, text="  Storyboard  ")
        self.create_storyboard_tab()

        self.preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.preview_frame, text="  Preview  ")
        self.create_preview_tab()

        self.export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.export_frame, text="  Export  ")
        self.create_export_tab()

    # ========================================================================
    # TAB 1: INPUT
    # ========================================================================

    def create_input_tab(self):
        container = ttk.Frame(self.input_frame, padding=20)
        container.pack(fill='both', expand=True)

        # Script file
        ttk.Label(container, text="Voiceover Script:", style='Header.TLabel').pack(anchor='w', pady=(10, 2))
        script_row = ttk.Frame(container)
        script_row.pack(fill='x', pady=2)
        self.script_var = tk.StringVar()
        ttk.Entry(script_row, textvariable=self.script_var, state='readonly').pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(script_row, text="Browse...", command=self.browse_script).pack(side='right')

        # Audio file
        ttk.Label(container, text="Audio File:", style='Header.TLabel').pack(anchor='w', pady=(15, 2))
        audio_row = ttk.Frame(container)
        audio_row.pack(fill='x', pady=2)
        self.audio_var = tk.StringVar()
        ttk.Entry(audio_row, textvariable=self.audio_var, state='readonly').pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(audio_row, text="Browse...", command=self.browse_audio).pack(side='right')

        # GAMMA URL
        ttk.Label(container, text="GAMMA Presentation URL:", style='Header.TLabel').pack(anchor='w', pady=(15, 2))
        self.url_var = tk.StringVar()
        ttk.Entry(container, textvariable=self.url_var, font=('Arial', 10)).pack(fill='x', pady=2)

        # Create button
        ttk.Button(container, text="CREATE STORYBOARD", style='Big.TButton',
                   command=self.create_storyboard).pack(pady=30)

        # Progress
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(container, textvariable=self.progress_var, style='Status.TLabel').pack(anchor='w')
        self.progress_bar = ttk.Progressbar(container, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=5)

    def browse_script(self):
        path = filedialog.askopenfilename(
            title="Select Script File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self.script_var.set(path)

    def browse_audio(self):
        path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio files", "*.wav *.mp3 *.m4a"), ("All files", "*.*")]
        )
        if path:
            self.audio_var.set(path)

    def create_storyboard(self):
        script_file = self.script_var.get()
        audio_file = self.audio_var.get()
        gamma_url = self.url_var.get().strip()

        if not script_file or not os.path.exists(script_file):
            messagebox.showerror("Error", "Please select a valid script file")
            return
        if not audio_file or not os.path.exists(audio_file):
            messagebox.showerror("Error", "Please select a valid audio file")
            return
        if not gamma_url:
            messagebox.showerror("Error", "Please enter a GAMMA URL")
            return

        self.progress_bar.start()

        def run_generation():
            try:
                from storyboard_generator import generate_storyboard
                storyboard, storyboard_path = generate_storyboard(
                    gamma_url=gamma_url,
                    script_file=script_file,
                    audio_file=audio_file,
                    output_dir=self.settings.get('output_folder') or None,
                    settings=self.settings,
                    progress_callback=lambda msg: self.root.after(0, lambda: self.progress_var.set(msg))
                )

                self.storyboard = storyboard
                self.storyboard_path = storyboard_path

                self.root.after(0, self.on_storyboard_created)

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Storyboard generation failed:\n{e}"))
                self.root.after(0, lambda: self.progress_bar.stop())

        threading.Thread(target=run_generation, daemon=True).start()

    def on_storyboard_created(self):
        self.progress_bar.stop()
        self.progress_var.set("Storyboard created!")
        self.load_storyboard_into_editor()
        self.notebook.select(1)

    # ========================================================================
    # TAB 2: STORYBOARD EDITOR
    # ========================================================================

    def create_storyboard_tab(self):
        # Toolbar
        toolbar = ttk.Frame(self.storyboard_frame)
        toolbar.pack(fill='x', padx=5, pady=5)

        ttk.Button(toolbar, text="+ Add Empty Scene", command=self.add_empty_scene).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Delete Scene", command=self.delete_scene).pack(side='left', padx=2)
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
        ttk.Button(toolbar, text="\U0001f4be Save", command=self.save_storyboard).pack(side='left', padx=2)
        ttk.Button(toolbar, text="\U0001f4c2 Load", command=self.load_storyboard).pack(side='left', padx=2)

        # Scrollable storyboard area
        canvas_frame = ttk.Frame(self.storyboard_frame)
        canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.sb_canvas = tk.Canvas(canvas_frame, bg='#F5F5F5')
        sb_scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.sb_canvas.yview)
        self.sb_inner = ttk.Frame(self.sb_canvas)

        self.sb_inner.bind('<Configure>',
                          lambda e: self.sb_canvas.configure(scrollregion=self.sb_canvas.bbox('all')))

        self.sb_canvas.create_window((0, 0), window=self.sb_inner, anchor='nw')
        self.sb_canvas.configure(yscrollcommand=sb_scrollbar.set)

        self.sb_canvas.pack(side='left', fill='both', expand=True)
        sb_scrollbar.pack(side='right', fill='y')

        # Mouse wheel scrolling
        self.sb_canvas.bind('<MouseWheel>', lambda e: self.sb_canvas.yview_scroll(-1*(e.delta//120), 'units'))

        # Header row
        self.scene_widgets = []

    def load_storyboard_into_editor(self):
        if not self.storyboard:
            return

        # Clear existing widgets
        for widget in self.sb_inner.winfo_children():
            widget.destroy()
        self.scene_widgets = []
        self.thumbnails = {}

        # Header
        header = ttk.Frame(self.sb_inner)
        header.pack(fill='x', padx=2, pady=2)
        headers = [('#', 30), ('Image', 120), ('Script', 400), ('Duration', 70),
                   ('Cumul.', 70), ('Transition', 90), ('Trans Time', 90)]
        for text, width in headers:
            lbl = ttk.Label(header, text=text, font=('Arial', 9, 'bold'), width=width//8)
            lbl.pack(side='left', padx=2)

        ttk.Separator(self.sb_inner, orient='horizontal').pack(fill='x', pady=2)

        # Scene rows
        for scene in self.storyboard['scenes']:
            self.add_scene_row(scene)

    def add_scene_row(self, scene):
        row_frame = ttk.Frame(self.sb_inner, style='Scene.TFrame')
        row_frame.pack(fill='x', padx=2, pady=1)

        scene_num = scene['scene_number']

        # Scene number
        ttk.Label(row_frame, text=str(scene_num), font=('Arial', 11, 'bold'),
                  width=3, anchor='center').pack(side='left', padx=5)

        # Thumbnail
        thumb_label = ttk.Label(row_frame, text="[No Image]")
        thumb_label.pack(side='left', padx=5)
        self.load_thumbnail(scene.get('screenshot', ''), thumb_label, scene_num)

        # Script sentences (movable blocks)
        script_frame = ttk.Frame(row_frame, width=400)
        script_frame.pack(side='left', padx=5, fill='y')
        script_frame.pack_propagate(False)
        script_frame.config(width=400, height=max(60, len(scene.get('script_sentences', [])) * 28 + 10))

        sentence_widgets = []
        for j, sentence in enumerate(scene.get('script_sentences', [])):
            sent_row = ttk.Frame(script_frame)
            sent_row.pack(fill='x', pady=1)

            colors = ['#E3F2FD', '#FFF3E0', '#E8F5E9', '#FCE4EC', '#F3E5F5']
            color = colors[j % len(colors)]

            sent_label = tk.Label(sent_row, text=sentence, bg=color,
                                  font=('Arial', 9), anchor='w', wraplength=330, justify='left',
                                  padx=4, pady=2, relief='raised', borderwidth=1)
            sent_label.pack(side='left', fill='x', expand=True)

            btn_frame = ttk.Frame(sent_row)
            btn_frame.pack(side='right')

            up_btn = ttk.Button(btn_frame, text="▲", width=2,
                               command=lambda sn=scene_num, si=j: self.move_sentence_up(sn, si))
            up_btn.pack(side='top')
            down_btn = ttk.Button(btn_frame, text="▼", width=2,
                                 command=lambda sn=scene_num, si=j: self.move_sentence_down(sn, si))
            down_btn.pack(side='top')

            sentence_widgets.append(sent_label)

        # Duration
        dur = scene.get('duration', 0)
        ttk.Label(row_frame, text=self.format_time(dur), font=('Courier', 10),
                  width=8).pack(side='left', padx=5)

        # Cumulative
        cum = scene.get('cumulative_duration', 0)
        ttk.Label(row_frame, text=self.format_time(cum), font=('Courier', 10),
                  width=8).pack(side='left', padx=5)

        # Transition type dropdown
        trans_var = tk.StringVar(value=scene.get('transition_type', 'fade'))
        trans_combo = ttk.Combobox(row_frame, textvariable=trans_var, values=TRANSITION_TYPES,
                                   width=10, state='readonly')
        trans_combo.pack(side='left', padx=5)
        trans_combo.bind('<<ComboboxSelected>>',
                        lambda e, sn=scene_num, tv=trans_var: self.update_transition_type(sn, tv.get()))

        # Transition time spinbox
        time_var = tk.DoubleVar(value=scene.get('transition_time', 0.25))
        time_frame = ttk.Frame(row_frame)
        time_frame.pack(side='left', padx=5)

        time_label = ttk.Label(time_frame, text=f"{time_var.get():.2f}s",
                               font=('Courier', 10), width=6)
        time_label.pack(side='left')

        time_btn_frame = ttk.Frame(time_frame)
        time_btn_frame.pack(side='left')

        ttk.Button(time_btn_frame, text="▲", width=2,
                   command=lambda sn=scene_num, tv=time_var, tl=time_label:
                       self.adjust_transition_time(sn, tv, tl, 0.25)).pack(side='top')
        ttk.Button(time_btn_frame, text="▼", width=2,
                   command=lambda sn=scene_num, tv=time_var, tl=time_label:
                       self.adjust_transition_time(sn, tv, tl, -0.25)).pack(side='top')

        self.scene_widgets.append({
            'frame': row_frame,
            'scene_number': scene_num,
            'sentence_widgets': sentence_widgets
        })

    def load_thumbnail(self, screenshot_path, label, scene_num):
        if not screenshot_path or not os.path.exists(screenshot_path):
            return

        try:
            img = Image.open(screenshot_path)
            img.thumbnail((110, 70))
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo, text='')
            self.thumbnails[scene_num] = photo
        except Exception:
            pass

    def move_sentence_up(self, scene_num, sentence_idx):
        if not self.storyboard:
            return

        scene_idx = scene_num - 1
        scenes = self.storyboard['scenes']

        if scene_idx < 0 or scene_idx >= len(scenes):
            return

        sentences = scenes[scene_idx]['script_sentences']
        if sentence_idx < 0 or sentence_idx >= len(sentences):
            return

        sentence = sentences.pop(sentence_idx)

        # Move to previous scene
        if scene_idx > 0:
            scenes[scene_idx - 1]['script_sentences'].append(sentence)
        else:
            sentences.insert(0, sentence)
            return

        self.recalculate_and_refresh()

    def move_sentence_down(self, scene_num, sentence_idx):
        if not self.storyboard:
            return

        scene_idx = scene_num - 1
        scenes = self.storyboard['scenes']

        if scene_idx < 0 or scene_idx >= len(scenes):
            return

        sentences = scenes[scene_idx]['script_sentences']
        if sentence_idx < 0 or sentence_idx >= len(sentences):
            return

        sentence = sentences.pop(sentence_idx)

        # Move to next scene
        if scene_idx < len(scenes) - 1:
            scenes[scene_idx + 1]['script_sentences'].insert(0, sentence)
        else:
            sentences.append(sentence)
            return

        self.recalculate_and_refresh()

    def update_transition_type(self, scene_num, new_type):
        if not self.storyboard:
            return
        scene_idx = scene_num - 1
        if 0 <= scene_idx < len(self.storyboard['scenes']):
            self.storyboard['scenes'][scene_idx]['transition_type'] = new_type

    def adjust_transition_time(self, scene_num, time_var, time_label, delta):
        new_val = round(time_var.get() + delta, 2)
        new_val = max(0.0, min(new_val, 5.0))
        time_var.set(new_val)
        time_label.config(text=f"{new_val:.2f}s")

        if self.storyboard:
            scene_idx = scene_num - 1
            if 0 <= scene_idx < len(self.storyboard['scenes']):
                self.storyboard['scenes'][scene_idx]['transition_time'] = new_val

    def recalculate_and_refresh(self):
        from storyboard_generator import recalculate_timings
        self.storyboard = recalculate_timings(self.storyboard)
        self.load_storyboard_into_editor()

    def add_empty_scene(self):
        if not self.storyboard:
            return

        scenes = self.storyboard['scenes']
        new_num = len(scenes) + 1
        scenes.append({
            'scene_number': new_num,
            'screenshot': '',
            'script_sentences': [],
            'start_time': 0,
            'end_time': 0,
            'duration': 0,
            'cumulative_duration': 0,
            'transition_type': self.settings['default_transition_type'],
            'transition_time': self.settings['default_transition_time']
        })

        self.recalculate_and_refresh()

    def delete_scene(self):
        if not self.storyboard or not self.storyboard['scenes']:
            return

        # Delete last scene, move its sentences to previous
        scenes = self.storyboard['scenes']
        if len(scenes) <= 1:
            messagebox.showwarning("Warning", "Cannot delete the only scene")
            return

        last = scenes.pop()
        if last['script_sentences'] and scenes:
            scenes[-1]['script_sentences'].extend(last['script_sentences'])

        # Renumber
        for i, s in enumerate(scenes):
            s['scene_number'] = i + 1

        self.recalculate_and_refresh()

    def save_storyboard(self):
        if not self.storyboard:
            messagebox.showwarning("Warning", "No storyboard to save")
            return

        path = filedialog.asksaveasfilename(
            title="Save Storyboard",
            defaultextension=".json",
            initialfile="storyboard.json",
            filetypes=[("JSON files", "*.json")]
        )
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.storyboard, f, indent=2, ensure_ascii=False)
            self.storyboard_path = path
            messagebox.showinfo("Saved", f"Storyboard saved to:\n{path}")

    def load_storyboard(self):
        path = filedialog.askopenfilename(
            title="Load Storyboard",
            filetypes=[("JSON files", "*.json")]
        )
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                self.storyboard = json.load(f)
            self.storyboard_path = path
            self.load_storyboard_into_editor()
            messagebox.showinfo("Loaded", f"Storyboard loaded: {len(self.storyboard['scenes'])} scenes")

    # ========================================================================
    # TAB 3: PREVIEW
    # ========================================================================

    def create_preview_tab(self):
        container = ttk.Frame(self.preview_frame, padding=10)
        container.pack(fill='both', expand=True)

        # Controls
        controls = ttk.Frame(container)
        controls.pack(fill='x', pady=5)

        self.play_btn = ttk.Button(controls, text="▶ Play", command=self.preview_play)
        self.play_btn.pack(side='left', padx=5)
        self.pause_btn = ttk.Button(controls, text="⏸ Pause", command=self.preview_pause, state='disabled')
        self.pause_btn.pack(side='left', padx=5)
        self.stop_btn = ttk.Button(controls, text="⏹ Stop", command=self.preview_stop, state='disabled')
        self.stop_btn.pack(side='left', padx=5)

        self.preview_time_var = tk.StringVar(value="00:00.00 / 00:00.00")
        ttk.Label(controls, textvariable=self.preview_time_var,
                  font=('Courier', 12, 'bold')).pack(side='left', padx=20)

        # Large thumbnail
        self.preview_thumb_label = ttk.Label(container, text="[Scene Preview]",
                                             font=('Arial', 14), anchor='center')
        self.preview_thumb_label.pack(fill='x', pady=10)

        # Scene info
        self.preview_scene_var = tk.StringVar(value="")
        ttk.Label(container, textvariable=self.preview_scene_var,
                  font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)

        # Script text for current scene
        self.preview_script_text = tk.Text(container, height=4, font=('Arial', 11),
                                            wrap='word', state='disabled')
        self.preview_script_text.pack(fill='x', pady=5)

        # Storyboard list
        ttk.Label(container, text="Storyboard Timeline:",
                  style='Header.TLabel').pack(anchor='w', pady=(10, 2))

        list_frame = ttk.Frame(container)
        list_frame.pack(fill='both', expand=True)

        columns = ('scene', 'duration', 'cumulative', 'script')
        self.preview_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.preview_tree.heading('scene', text='Scene #')
        self.preview_tree.heading('duration', text='Duration')
        self.preview_tree.heading('cumulative', text='Cumulative')
        self.preview_tree.heading('script', text='Script Preview')
        self.preview_tree.column('scene', width=60)
        self.preview_tree.column('duration', width=80)
        self.preview_tree.column('cumulative', width=80)
        self.preview_tree.column('script', width=500)

        tree_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=tree_scroll.set)
        self.preview_tree.pack(side='left', fill='both', expand=True)
        tree_scroll.pack(side='right', fill='y')

        self.preview_tree.tag_configure('highlight', background='#FFEB3B')

    def preview_play(self):
        if not self.storyboard:
            messagebox.showwarning("Warning", "No storyboard loaded")
            return

        audio_file = self.storyboard.get('audio_file', '')
        if not audio_file or not os.path.exists(audio_file):
            messagebox.showerror("Error", f"Audio file not found: {audio_file}")
            return

        # Populate tree
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)

        for scene in self.storyboard['scenes']:
            script_preview = ' '.join(scene.get('script_sentences', []))[:80]
            self.preview_tree.insert('', 'end', iid=str(scene['scene_number']),
                                     values=(
                                         f"Scene {scene['scene_number']}",
                                         self.format_time(scene.get('duration', 0)),
                                         self.format_time(scene.get('cumulative_duration', 0)),
                                         script_preview
                                     ))

        if self.audio_available:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()

        self.is_previewing = True
        self.preview_start_time = time.time()

        self.play_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.stop_btn.config(state='normal')

        self.update_preview()

    def preview_pause(self):
        if self.is_previewing:
            if self.audio_available:
                pygame.mixer.music.pause()
            self.is_previewing = False
            self.pause_btn.config(text="▶ Resume")
        else:
            if self.audio_available:
                pygame.mixer.music.unpause()
            self.is_previewing = True
            self.pause_btn.config(text="⏸ Pause")
            self.update_preview()

    def preview_stop(self):
        self.is_previewing = False
        if self.audio_available:
            pygame.mixer.music.stop()
        self.play_btn.config(state='normal')
        self.pause_btn.config(state='disabled', text="⏸ Pause")
        self.stop_btn.config(state='disabled')

        # Clear highlight
        for item in self.preview_tree.get_children():
            self.preview_tree.item(item, tags=())

    def update_preview(self):
        if not self.is_previewing:
            return

        if self.audio_available:
            current_time = pygame.mixer.music.get_pos() / 1000.0
            if current_time < 0:
                current_time = 0
        else:
            current_time = time.time() - self.preview_start_time
        if current_time < 0:
            current_time = 0

        audio_dur = self.storyboard.get('audio_duration', 0)
        self.preview_time_var.set(f"{self.format_time(current_time)} / {self.format_time(audio_dur)}")

        # Find current scene
        current_scene = None
        for scene in self.storyboard['scenes']:
            if scene.get('start_time', 0) <= current_time < scene.get('end_time', 0):
                current_scene = scene
                break

        if not current_scene and self.storyboard['scenes']:
            current_scene = self.storyboard['scenes'][-1]

        if current_scene:
            scene_num = current_scene['scene_number']
            self.preview_scene_var.set(f"Scene {scene_num}")

            # Update script text
            self.preview_script_text.config(state='normal')
            self.preview_script_text.delete('1.0', 'end')
            script = ' '.join(current_scene.get('script_sentences', []))
            self.preview_script_text.insert('1.0', script)
            self.preview_script_text.config(state='disabled')

            # Highlight row
            for item in self.preview_tree.get_children():
                self.preview_tree.item(item, tags=())
            try:
                self.preview_tree.item(str(scene_num), tags=('highlight',))
                self.preview_tree.see(str(scene_num))
            except Exception:
                pass

            # Update thumbnail
            screenshot = current_scene.get('screenshot', '')
            if screenshot and os.path.exists(screenshot):
                try:
                    img = Image.open(screenshot)
                    img.thumbnail((500, 300))
                    photo = ImageTk.PhotoImage(img)
                    self.preview_thumb_label.config(image=photo, text='')
                    self.preview_thumb_label._photo = photo
                except Exception:
                    pass

        # Check if audio finished
        if self.audio_available and not pygame.mixer.music.get_busy():
            self.preview_stop()
            return
        elif not self.audio_available:
            audio_dur = self.storyboard.get('audio_duration', 0)
            if current_time >= audio_dur > 0:
                self.preview_stop()
                return
            return

        self.root.after(100, self.update_preview)

    # ========================================================================
    # TAB 4: EXPORT
    # ========================================================================

    def create_export_tab(self):
        container = ttk.Frame(self.export_frame, padding=20)
        container.pack(fill='both', expand=True)

        ttk.Label(container, text="Generate Video", style='Title.TLabel').pack(pady=(10, 20))

        ttk.Label(container, text="Creates an MP4 video from your storyboard\n"
                  "with transitions and synchronized audio.",
                  font=('Arial', 11), justify='center').pack(pady=10)

        self.generate_btn = ttk.Button(container, text="GENERATE VIDEO",
                                        style='Big.TButton', command=self.generate_video)
        self.generate_btn.pack(pady=20)

        # Progress
        self.export_progress_var = tk.StringVar(value="")
        ttk.Label(container, textvariable=self.export_progress_var,
                  style='Status.TLabel').pack(anchor='w')
        self.export_progress_bar = ttk.Progressbar(container, mode='indeterminate')
        self.export_progress_bar.pack(fill='x', pady=5)

        # Result section (hidden until video is generated)
        self.result_frame = ttk.LabelFrame(container, text="Video Created", padding=15)

        self.video_path_var = tk.StringVar()
        ttk.Label(self.result_frame, text="Saved to:").pack(anchor='w')
        ttk.Entry(self.result_frame, textvariable=self.video_path_var,
                  state='readonly', font=('Courier', 9)).pack(fill='x', pady=5)

        btn_row = ttk.Frame(self.result_frame)
        btn_row.pack(fill='x', pady=10)
        ttk.Button(btn_row, text="\U0001f4c2 Open Folder",
                   command=self.open_video_folder).pack(side='left', padx=5)
        ttk.Button(btn_row, text="▶ Play Video",
                   command=self.play_video).pack(side='left', padx=5)

    def generate_video(self):
        if not self.storyboard:
            messagebox.showwarning("Warning", "No storyboard loaded. Create or load one first.")
            return

        self.generate_btn.config(state='disabled')
        self.export_progress_bar.start()

        def run_export():
            try:
                from video_generator import generate_video

                output_dir = self.storyboard.get('output_dir', os.path.dirname(self.storyboard_path or '.'))
                output_path = os.path.join(output_dir, "video.mp4")

                result_path = generate_video(
                    self.storyboard,
                    output_path=output_path,
                    progress_callback=lambda msg: self.root.after(0, lambda: self.export_progress_var.set(msg))
                )

                self.root.after(0, lambda: self.on_video_created(result_path))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Video generation failed:\n{e}"))
                self.root.after(0, lambda: self.export_progress_bar.stop())
                self.root.after(0, lambda: self.generate_btn.config(state='normal'))

        threading.Thread(target=run_export, daemon=True).start()

    def on_video_created(self, video_path):
        self.export_progress_bar.stop()
        self.export_progress_var.set("Video created successfully!")
        self.generate_btn.config(state='normal')

        self.video_path_var.set(video_path)
        self.result_frame.pack(fill='x', pady=10)

    def open_video_folder(self):
        video_path = self.video_path_var.get()
        if video_path and os.path.exists(video_path):
            folder = os.path.dirname(video_path)
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', folder])
            else:
                subprocess.Popen(['xdg-open', folder])

    def play_video(self):
        video_path = self.video_path_var.get()
        if video_path and os.path.exists(video_path):
            if sys.platform == 'win32':
                os.startfile(video_path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', video_path])
            else:
                subprocess.Popen(['xdg-open', video_path])

    # ========================================================================
    # SETTINGS DIALOG
    # ========================================================================

    def open_settings(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()

        container = ttk.Frame(dialog, padding=20)
        container.pack(fill='both', expand=True)

        # Default transition type
        ttk.Label(container, text="Default Transition Type:").pack(anchor='w', pady=(5, 2))
        trans_var = tk.StringVar(value=self.settings['default_transition_type'])
        ttk.Combobox(container, textvariable=trans_var, values=TRANSITION_TYPES,
                     state='readonly').pack(fill='x')

        # Default transition time
        ttk.Label(container, text="Default Transition Time (seconds):").pack(anchor='w', pady=(10, 2))
        time_frame = ttk.Frame(container)
        time_frame.pack(fill='x')

        time_var = tk.DoubleVar(value=self.settings['default_transition_time'])
        time_label = ttk.Label(time_frame, text=f"{time_var.get():.2f}s", font=('Courier', 11), width=6)
        time_label.pack(side='left', padx=5)

        def adjust(delta):
            val = round(time_var.get() + delta, 2)
            val = max(0.0, min(val, 5.0))
            time_var.set(val)
            time_label.config(text=f"{val:.2f}s")

        ttk.Button(time_frame, text="▲", width=3, command=lambda: adjust(0.25)).pack(side='left', padx=2)
        ttk.Button(time_frame, text="▼", width=3, command=lambda: adjust(-0.25)).pack(side='left', padx=2)

        # Video resolution
        ttk.Label(container, text="Video Resolution:").pack(anchor='w', pady=(10, 2))
        res_var = tk.StringVar(value=self.settings.get('video_resolution', '1920x1080'))
        ttk.Combobox(container, textvariable=res_var,
                     values=['1920x1080', '1280x720', '854x480'],
                     state='readonly').pack(fill='x')

        # Video FPS
        ttk.Label(container, text="Video FPS:").pack(anchor='w', pady=(10, 2))
        fps_var = tk.StringVar(value=str(self.settings.get('video_fps', 24)))
        ttk.Combobox(container, textvariable=fps_var,
                     values=['24', '30', '60'], state='readonly').pack(fill='x')

        # Output folder
        ttk.Label(container, text="Default Output Folder:").pack(anchor='w', pady=(10, 2))
        folder_frame = ttk.Frame(container)
        folder_frame.pack(fill='x')
        folder_var = tk.StringVar(value=self.settings.get('output_folder', ''))
        ttk.Entry(folder_frame, textvariable=folder_var).pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(folder_frame, text="Browse",
                   command=lambda: folder_var.set(
                       filedialog.askdirectory() or folder_var.get()
                   )).pack(side='right')

        # Save / Cancel
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill='x', pady=20)

        def save_and_close():
            self.settings['default_transition_type'] = trans_var.get()
            self.settings['default_transition_time'] = time_var.get()
            self.settings['video_resolution'] = res_var.get()
            self.settings['video_fps'] = int(fps_var.get())
            self.settings['output_folder'] = folder_var.get()
            save_settings(self.settings)
            dialog.destroy()

        ttk.Button(btn_frame, text="Save", command=save_and_close).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)

    # ========================================================================
    # UTILITIES
    # ========================================================================

    @staticmethod
    def format_time(seconds):
        if seconds is None:
            return "00:00.00"
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins:02d}:{secs:05.2f}"


# ============================================================================
# MAIN
# ============================================================================

def main():
    if not HAS_GUI:
        print(f"Error: {_import_error}")
        print("This app requires a graphical environment with tkinter.")
        print("On Windows, tkinter is included with Python by default.")
        input("Press Enter to exit...")
        return
    root = tk.Tk()
    app = StoryboardStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
