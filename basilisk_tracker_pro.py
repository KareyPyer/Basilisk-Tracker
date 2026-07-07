#!/usr/bin/env python3
"""
===============================================================================
SEARCHLORES BASILISK TRACKER PRO v3.0
===============================================================================
"The Search Is The Program. The Ontology Is The Map."

Générateur de Basilisk épistémiques avancé — Interface Neo-Amiga avec effets
CRT, animations, et fonctionnalités professionnelles. Assemble des prompts
tordus à partir d'une bibliothèque étendue d'artefacts JSON.

Inspiré par : Nick Bostrom, Roko's Basilisk, LessWrong, Fravia (in Memoriam)

Nouveautés v3.0 :
- Interface Neo-Amiga avec effets CRT, glow, scanlines
- Système de presets et sauvegarde de sessions
- Recherche et filtres avancés dans la bibliothèque
- Analyse de cohérence et détection de conflits
- Export multi-format (TXT, JSON, Markdown, HTML)
- Templates de prompts prédéfinis
- Statistiques avancées et visualisations
- Système de tags et métadonnées enrichies
- Mode composition avec contraintes
- Historique enrichi avec navigation

Usage :
    python3 basilisk_tracker_pro.py

Hotkeys (style tracker) :
    F1-F8       : Sélectionner canal (catégorie)
    SPACE       : Play/Stop la séquence
    ENTER       : Insérer artefact au curseur
    DEL         : Retirer artefact au curseur
    CTRL+UP/DOWN: Déplacer ligne
    CTRL+C/V    : Copier/Coller ligne
    CTRL+Z/Y    : Undo/Redo
    CTRL+S      : Sauvegarder session
    CTRL+O      : Charger session
    CTRL+F      : Rechercher dans la bibliothèque
    TAB         : Cycle entre les panels
    ESC         : Stop / reset
    F3          : Charger bibliothèque JSON
    F5          : Recharger
    F6          : Exporter prompt
    F7          : Exporter ground truth
    F8          : Vider séquence
    F9          : Randomiser
    F10         : Trier par position
    F11         : Inverser
    F12         : Lancer soneck.py
===============================================================================
"""
import json
import math
import os
import random
import subprocess
import sys
import tempfile
import tkinter as tk
from collections import Counter, defaultdict
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import re

APP_TITLE = "Searchlores Basilisk Tracker PRO v3.0"
DEFAULT_LIBRARY = Path(__file__).with_name("artifacts_basilisk_extended.json")
SESSIONS_DIR = Path(__file__).parent / "sessions"
PRESETS_DIR = Path(__file__).parent / "presets"

SESSIONS_DIR.mkdir(exist_ok=True)
PRESETS_DIR.mkdir(exist_ok=True)

# -- Tracker-style position order --
POSITION_ORDER = ["opening", "framing", "body", "constraint", "trap", "closing"]
POSITION_LABELS = {
    "opening": "OPN", "framing": "FRM", "body": "BOD",
    "constraint": "CNS", "trap": "TRP", "closing": "CLS",
}

# -- Neo-Amiga color palette with CRT effects --
PALETTE = {
    "bg_dark": "#050510", "bg_panel": "#0a0a1a",
    "bg_panel_light": "#12122a", "bg_row_even": "#1a1a35",
    "bg_row_odd": "#151530", "bg_row_active": "#2d1b5e",
    "bg_row_playing": "#1e4a3f", "bg_hover": "#1e1e40",
    "border": "#2a2a50", "border_bright": "#4a4a8a",
    "border_glow": "#00ffff",
    "text_normal": "#c0c0e0", "text_dim": "#6a6a90",
    "text_bright": "#e0e0ff", "text_highlight": "#ffcc00",
    "text_info": "#00ddff", "text_warning": "#ff8844",
    "text_danger": "#ff4466", "text_success": "#44ff88",
    "accent_cyan": "#00ffff", "accent_magenta": "#ff00ff",
    "accent_green": "#00ff88", "accent_yellow": "#ffff00",
    "accent_red": "#ff3355", "accent_blue": "#4488ff",
    "accent_purple": "#aa44ff",
    "header_bg": "#1a1a3a", "header_fg": "#00ffff",
    "tracker_bg": "#080818", "tracker_fg": "#00ff88",
    "tracker_grid": "#1a1a40", "tracker_cursor": "#ff00ff",
    "tracker_playline": "#ffff00",
    "scope_bg": "#030308", "scope_line": "#00ff88",
    "scope_peak": "#ff4466", "scope_grid": "#1a1a30",
    "scrollbar": "#2a2a55", "scrollbar_active": "#4a4a90",
    "crt_scanline": "#000000",
}

# -- Category colors --
CAT_COLORS = {
    "authority": "#ff6b6b", "assumptions": "#4ecdc4",
    "contradictions": "#ffe66d", "omissions": "#a8e6cf",
    "narrative": "#ff8b94", "genealogy": "#c7ceea",
    "ontology": "#ffd93d", "bias": "#6bcb77",
    "debate": "#4d96ff", "counterprompt": "#ff6b9d",
    "temporal": "#9b59b6", "affect": "#e74c3c",
    "basilisk": "#ff00ff", "epistemic_hazard": "#ff3333",
    "memetic_trap": "#ff8800", "ontological_weapon": "#00ffff",
    "recursive_manipulation": "#ffff00", "value_alignment_trap": "#ff4466",
    "cognitive_distortion": "#ff69b4", "linguistic_trap": "#7b68ee",
    "social_engineering": "#20b2aa", "reality_distortion": "#ff1493",
    "paradox_engine": "#00ff00", "identity_attack": "#ff4500",
}


# ===============================================================================
# UTILITAIRES
# ===============================================================================
def deep_merge(target: dict, source: dict) -> None:
    """Fusion récursive de dictionnaires avec gestion des conflits scalaires."""
    for key, value in source.items():
        if key not in target:
            target[key] = value
            continue
        existing = target[key]
        if isinstance(existing, list) and isinstance(value, list):
            for v in value:
                if v not in existing:
                    existing.append(v)
        elif isinstance(existing, dict) and isinstance(value, dict):
            deep_merge(existing, value)
        elif existing == value:
            continue
        else:
            bucket_key = f"{key}__occurrences"
            bucket = target.setdefault(bucket_key, [])
            if not bucket:
                bucket.append(existing)
            bucket.append(value)
            if isinstance(existing, (int, float)) and isinstance(value, (int, float)):
                target[key] = max(existing, value)


def local_entropy_metrics(text: str) -> dict:
    """Métriques d'entropie rapide (sans dépendance externe)."""
    tokens = [t.strip(".,;:!?()«»\"'").lower() for t in text.split()]
    tokens = [t for t in tokens if t]
    if not tokens:
        return {"token_entropy": 0.0, "type_token_ratio": 0.0,
                "lexical_density": 0.0, "n_tokens": 0}
    counts = Counter(tokens)
    total = len(tokens)
    entropy = -sum((c / total) * math.log2(c / total) for c in counts.values())
    ttr = len(counts) / total
    stopwords = {
        "le", "la", "les", "de", "des", "du", "un", "une", "et", "ou", "que",
        "qui", "à", "en", "est", "sont", "ce", "cette", "ces", "pour", "dans",
        "sur", "par", "avec", "sans", "au", "aux", "se", "sa", "son", "ses",
        "tu", "il", "elle", "nous", "vous", "ils", "elles", "je", "ne", "pas",
        "plus", "moins", "mais", "donc", "or", "ni", "car", "toute", "tout",
        "tous", "toutes", "aucun", "aucune", "être", "avoir", "afin"
    }
    lexical_tokens = [t for t in tokens if t not in stopwords]
    lexical_density = len(lexical_tokens) / total
    return {
        "token_entropy": round(entropy, 3),
        "type_token_ratio": round(ttr, 3),
        "lexical_density": round(lexical_density, 3),
        "n_tokens": total,
    }


def entropy_level(value: float) -> str:
    if value < 3.0:
        return "LOW"
    if value <= 5.0:
        return "MOD"
    return "HIGH"


def truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n - 1] + "..."


def calculate_coherence_score(sequence: list, artifacts_by_id: dict) -> dict:
    """Calcule un score de cohérence entre les artefacts."""
    if not sequence:
        return {"score": 0, "conflicts": [], "synergies": [],
                "diversity": 0.0, "position_balance": 0.0}

    categories_used = [artifacts_by_id[a]["category"]
                       for a in sequence if a in artifacts_by_id]
    positions_used = [artifacts_by_id[a].get("position_hint", "body")
                      for a in sequence if a in artifacts_by_id]

    conflicts = []
    cats_lower = [c.lower() for c in categories_used]
    if "authority" in cats_lower and "counterprompt" in cats_lower:
        conflicts.append("Autorité vs Contre-prompt (tension épistémique)")
    if "basilisk" in cats_lower and "affect" in cats_lower:
        conflicts.append("Basilisk + Affect = charge émotionnelle critique")
    if "contradictions" in cats_lower and "ontology" in cats_lower:
        conflicts.append("Contradiction + Ontologie = risque de paradoxe")

    synergies = []
    if len(set(categories_used)) >= 4:
        synergies.append("Diversité catégorielle élevée (>= 4)")
    if "basilisk" in cats_lower and "epistemic_hazard" in cats_lower:
        synergies.append("Combo Basilisk + Hazard épistémique")
    if "trap" in [artifacts_by_id[a].get("position_hint", "")
                  for a in sequence if a in artifacts_by_id]:
        synergies.append("Présence de pièges positionnés")

    diversity = len(set(categories_used)) / max(1, len(sequence))
    position_balance = len(set(positions_used)) / len(POSITION_ORDER)
    score = int((diversity * 0.5 + position_balance * 0.5) * 100)

    return {
        "score": score,
        "conflicts": conflicts,
        "synergies": synergies,
        "diversity": round(diversity, 2),
        "position_balance": round(position_balance, 2),
    }


# ===============================================================================
# CUSTOM WIDGETS (Neo-Amiga style with CRT effects)
# ===============================================================================
class GlowButton(tk.Canvas):
    """Bouton avec effet glow néon."""
    def __init__(self, parent, text, command=None, width=100, height=28,
                 bg=None, fg=None, glow_color=None, font=None, **kw):
        bg = bg or PALETTE["bg_panel"]
        fg = fg or PALETTE["text_bright"]
        glow_color = glow_color or PALETTE["accent_cyan"]
        font = font or ("Courier New", 9, "bold")
        super().__init__(parent, width=width, height=height, bg=bg,
                         highlightthickness=0, **kw)
        self.text = text
        self.command = command
        self.normal_bg = bg
        self.fg = fg
        self.glow_color = glow_color
        self.font = font
        self.pressed = False
        self.hover = False
        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw(self):
        self.delete("all")
        w, h = int(self.cget("width")), int(self.cget("height"))
        bg = PALETTE["bg_hover"] if self.hover else self.normal_bg
        if self.pressed:
            bg = PALETTE["bg_row_active"]
        for i in range(3, 0, -1):
            offset = i * 2
            self.create_rectangle(offset, offset, w - offset, h - offset,
                                  outline=self.glow_color, width=1, fill="",
                                  tags="glow")
        self.create_rectangle(2, 2, w - 2, h - 2, fill=bg,
                              outline=self.glow_color if self.hover else PALETTE["border_bright"],
                              width=2)
        self.create_text(w // 2, h // 2, text=self.text, fill=self.fg,
                         font=self.font)

    def _on_enter(self, e):
        self.hover = True
        self._draw()

    def _on_leave(self, e):
        self.hover = False
        self._draw()

    def _on_press(self, e):
        self.pressed = True
        self._draw()

    def _on_release(self, e):
        self.pressed = False
        self._draw()
        if self.command:
            self.command()


class AdvancedScope(tk.Canvas):
    """Oscilloscope avancé avec plusieurs canaux."""
    def __init__(self, parent, width=300, height=80, **kw):
        super().__init__(parent, width=width, height=height,
                         bg=PALETTE["scope_bg"], highlightthickness=0, **kw)
        self.values = [0.0] * 96
        self.peak = 0.0
        self.channel_colors = [PALETTE["accent_cyan"], PALETTE["accent_magenta"],
                               PALETTE["accent_green"]]
        self.channels = [[0.0] * 96 for _ in range(3)]
        self._draw()

    def update_value(self, value: float, channel: int = 0):
        self.channels[channel].pop(0)
        self.channels[channel].append(value)
        self.peak = max(self.peak * 0.95, value)
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = int(self.cget("width")), int(self.cget("height"))
        for i in range(0, w, 25):
            self.create_line(i, 0, i, h, fill=PALETTE["scope_grid"], width=1)
        for i in range(0, h, 20):
            self.create_line(0, i, w, i, fill=PALETTE["scope_grid"], width=1)
        for ch_idx, channel_data in enumerate(self.channels):
            points = []
            color = self.channel_colors[ch_idx % len(self.channel_colors)]
            for i, v in enumerate(channel_data):
                x = i * (w / 96)
                y = h - (v / 10.0) * h * 0.8 - 5
                points.extend([x, y])
            if len(points) >= 4:
                self.create_line(points, fill=color, width=3, smooth=True,
                                 tags="glow")
                self.create_line(points, fill=color, width=1, smooth=True)
        peak_y = h - (self.peak / 10.0) * h * 0.8 - 5
        self.create_line(0, peak_y, w, peak_y, fill=PALETTE["scope_peak"],
                         width=1, dash=(4, 4))
        self.create_text(5, 10, text=f"PEAK: {self.peak:.2f}",
                         fill=PALETTE["scope_peak"],
                         font=("Courier New", 7, "bold"), anchor="w")
        avg = sum(self.channels[0]) / len(self.channels[0]) if self.channels[0] else 0
        self.create_text(5, 22, text=f"ENTROPY: {avg:.2f}",
                         fill=PALETTE["accent_cyan"],
                         font=("Courier New", 7), anchor="w")


class EnhancedPatternGrid(tk.Canvas):
    """Grille de pattern améliorée."""
    def __init__(self, parent, app, **kw):
        super().__init__(parent, bg=PALETTE["tracker_bg"],
                         highlightthickness=0, **kw)
        self.app = app
        self.row_height = 20
        self.visible_rows = 32
        self.scroll_offset = 0
        self.cursor_row = 0
        self.playing_row = -1
        self.clipboard = None
        self.undo_stack = []
        self.redo_stack = []
        self._save_state()
        self.bind("<Button-1>", self._on_click)
        self.bind("<MouseWheel>", self._on_scroll)
        self.bind("<Button-4>", lambda e: self._scroll(-3))
        self.bind("<Button-5>", lambda e: self._scroll(3))
        self._draw()

    def _save_state(self):
        state = list(self.app.sequence)
        if not self.undo_stack or self.undo_stack[-1] != state:
            self.undo_stack.append(state)
            if len(self.undo_stack) > 100:
                self.undo_stack.pop(0)
            self.redo_stack.clear()

    def undo(self):
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            self.app.sequence = list(self.undo_stack[-1])
            self.app._refresh_all()

    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            self.app.sequence = list(state)
            self.app._refresh_all()

    def _scroll(self, delta):
        max_offset = max(0, len(self.app.sequence) - self.visible_rows + 4)
        self.scroll_offset = max(0, min(max_offset, self.scroll_offset + delta))
        self._draw()

    def _on_scroll(self, e):
        self._scroll(-int(e.delta / 30))

    def _on_click(self, e):
        row = self.scroll_offset + e.y // self.row_height
        if 0 <= row < len(self.app.sequence):
            self.cursor_row = row
            self._draw()

    def _draw(self):
        self.delete("all")
        w = int(self.cget("width"))
        h = self.visible_rows * self.row_height
        self.config(height=h)
        header_h = 24
        self.create_rectangle(0, 0, w, header_h, fill=PALETTE["header_bg"],
                              outline="")
        self.create_line(0, header_h - 1, w, header_h - 1,
                         fill=PALETTE["accent_cyan"], width=2)
        headers = [
            (5, "#"), (40, "CAT"), (120, "ARTEFACT"),
            (w - 100, "POS"), (w - 60, "CPLX"), (w - 30, "TAG")
        ]
        for x, text in headers:
            self.create_text(x, header_h // 2, text=text,
                             fill=PALETTE["header_fg"],
                             font=("Courier New", 8, "bold"), anchor="w")
        for i in range(self.visible_rows):
            row_idx = self.scroll_offset + i
            y = header_h + i * self.row_height
            if row_idx == self.cursor_row:
                bg = PALETTE["bg_row_active"]
            elif row_idx == self.playing_row:
                bg = PALETTE["bg_row_playing"]
            elif row_idx % 4 == 0:
                bg = PALETTE["bg_row_even"]
            else:
                bg = PALETTE["bg_row_odd"]
            self.create_rectangle(0, y, w, y + self.row_height, fill=bg,
                                  outline=PALETTE["tracker_grid"], width=1)
            if row_idx < len(self.app.sequence):
                art_id = self.app.sequence[row_idx]
                art = self.app.artifacts_by_id.get(art_id)
                if art:
                    cat = art["category"]
                    cat_color = CAT_COLORS.get(cat, PALETTE["text_normal"])
                    pos = POSITION_LABELS.get(art.get("position_hint", ""), "???")
                    cplx = art.get("complexity", "?")
                    label = truncate(art["label"], 32)
                    tags = art.get("tags", [])
                    tag_str = tags[0] if tags else ""
                    hex_num = f"{row_idx:02X}"
                    self.create_text(5, y + self.row_height // 2, text=hex_num,
                                     fill=PALETTE["text_dim"],
                                     font=("Courier New", 8), anchor="w")
                    self.create_text(40, y + self.row_height // 2,
                                     text=cat[:10].upper(), fill=cat_color,
                                     font=("Courier New", 8, "bold"), anchor="w")
                    self.create_text(120, y + self.row_height // 2, text=label,
                                     fill=PALETTE["text_bright"],
                                     font=("Courier New", 8), anchor="w")
                    self.create_text(w - 100, y + self.row_height // 2,
                                     text=pos, fill=PALETTE["accent_cyan"],
                                     font=("Courier New", 8, "bold"), anchor="w")
                    if isinstance(cplx, int):
                        cplx_color = (PALETTE["text_success"] if cplx <= 2 else
                                      PALETTE["text_warning"] if cplx <= 4 else
                                      PALETTE["text_danger"])
                    else:
                        cplx_color = PALETTE["text_normal"]
                    self.create_text(w - 60, y + self.row_height // 2,
                                     text=str(cplx), fill=cplx_color,
                                     font=("Courier New", 8, "bold"), anchor="w")
                    if tag_str:
                        self.create_text(w - 30, y + self.row_height // 2,
                                         text="*", fill=cat_color,
                                         font=("Courier New", 10, "bold"),
                                         anchor="w")
            else:
                self.create_text(5, y + self.row_height // 2, text="--",
                                 fill=PALETTE["text_dim"],
                                 font=("Courier New", 8), anchor="w")
        if 0 <= self.cursor_row - self.scroll_offset < self.visible_rows:
            cy = header_h + (self.cursor_row - self.scroll_offset) * self.row_height
            self.create_line(0, cy, w, cy, fill=PALETTE["tracker_cursor"], width=3)
            self.create_line(0, cy, w, cy, fill=PALETTE["tracker_cursor"], width=1)
            self.create_line(0, cy + self.row_height, w, cy + self.row_height,
                             fill=PALETTE["tracker_cursor"], width=1)


class VUMeter(tk.Canvas):
    """VU-mètre style analogique."""
    def __init__(self, parent, width=120, height=40, **kw):
        super().__init__(parent, width=width, height=height,
                         bg=PALETTE["bg_panel"], highlightthickness=0, **kw)
        self.value = 0.0
        self.max_value = 10.0
        self._draw()

    def set_value(self, value: float):
        self.value = min(value, self.max_value)
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = int(self.cget("width")), int(self.cget("height"))
        self.create_rectangle(2, 2, w - 2, h - 2, fill=PALETTE["bg_dark"],
                              outline=PALETTE["border_bright"], width=1)
        num_segments = 20
        segment_width = (w - 10) / num_segments
        active_segments = int((self.value / self.max_value) * num_segments)
        for i in range(num_segments):
            x1 = 5 + i * segment_width
            x2 = x1 + segment_width - 2
            y1 = 5
            y2 = h - 5
            if i < active_segments:
                if i < num_segments * 0.6:
                    color = PALETTE["accent_green"]
                elif i < num_segments * 0.8:
                    color = PALETTE["accent_yellow"]
                else:
                    color = PALETTE["accent_red"]
                self.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
            else:
                self.create_rectangle(x1, y1, x2, y2, fill=PALETTE["bg_panel"],
                                      outline=PALETTE["border"], width=1)
        self.create_text(w // 2, h - 8, text=f"{self.value:.1f}",
                         fill=PALETTE["text_bright"],
                         font=("Courier New", 7, "bold"))


# ===============================================================================
# MAIN APPLICATION
# ===============================================================================
class BasiliskTrackerProApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1800x1000")
        self.minsize(1400, 800)
        self.configure(bg=PALETTE["bg_dark"])
        self.library_path = DEFAULT_LIBRARY
        self.artifacts_by_id = {}
        self.categories = []
        self.sequence = []
        self.project_root = None
        self.playing = False
        self.play_timer = None
        self.current_channel = 0
        self.search_var = tk.StringVar()
        self.session_name = "untitled"
        self._last_ground_truth = {}
        self._build_style()
        self._build_menu()
        self._build_layout()
        self._load_library(self.library_path, silent=True)
        self._bind_hotkeys()

    # -- Style & Menu --
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Pro.TFrame", background=PALETTE["bg_dark"])
        style.configure("Pro.TLabel", background=PALETTE["bg_dark"],
                        foreground=PALETTE["text_normal"],
                        font=("Courier New", 9))
        style.configure("Pro.TLabelframe", background=PALETTE["bg_panel"],
                        foreground=PALETTE["accent_cyan"])
        style.configure("Pro.TLabelframe.Label", background=PALETTE["bg_panel"],
                        foreground=PALETTE["accent_cyan"],
                        font=("Courier New", 10, "bold"))
        style.configure("Pro.TNotebook", background=PALETTE["bg_dark"],
                        tabmargins=[2, 5, 2, 0])
        style.configure("Pro.TNotebook.Tab", background=PALETTE["bg_panel"],
                        foreground=PALETTE["text_dim"],
                        font=("Courier New", 9, "bold"), padding=[12, 4])
        style.map("Pro.TNotebook.Tab",
                  background=[("selected", PALETTE["bg_row_even"])],
                  foreground=[("selected", PALETTE["accent_cyan"])],
                  expand=[("selected", [1, 1, 1, 0])])
        style.configure("Pro.TScrollbar", background=PALETTE["scrollbar"],
                        troughcolor=PALETTE["bg_dark"],
                        bordercolor=PALETTE["border"])
        style.map("Pro.TScrollbar",
                  background=[("active", PALETTE["scrollbar_active"])])

    def _build_menu(self):
        menubar = tk.Menu(self, bg=PALETTE["bg_panel"],
                          fg=PALETTE["text_bright"],
                          activebackground=PALETTE["bg_row_active"],
                          activeforeground=PALETTE["accent_cyan"],
                          font=("Courier New", 9))
        filemenu = tk.Menu(menubar, tearoff=0, bg=PALETTE["bg_panel"],
                           fg=PALETTE["text_bright"],
                           activebackground=PALETTE["bg_row_active"],
                           activeforeground=PALETTE["accent_cyan"],
                           font=("Courier New", 9))
        filemenu.add_command(label="[F3] Charger bibliotheque JSON",
                             command=self.action_load_library, accelerator="F3")
        filemenu.add_command(label="[F5] Recharger",
                             command=lambda: self._load_library(self.library_path))
        filemenu.add_separator()
        filemenu.add_command(label="[CTRL+O] Charger session",
                             command=self.action_load_session, accelerator="Ctrl+O")
        filemenu.add_command(label="[CTRL+S] Sauvegarder session",
                             command=self.action_save_session, accelerator="Ctrl+S")
        filemenu.add_separator()
        filemenu.add_command(label="[F6] Exporter prompt (.txt)",
                             command=self.action_export_prompt, accelerator="F6")
        filemenu.add_command(label="Exporter prompt (.md)",
                             command=self.action_export_prompt_md)
        filemenu.add_command(label="Exporter prompt (.html)",
                             command=self.action_export_prompt_html)
        filemenu.add_command(label="[F7] Exporter ground truth (.json)",
                             command=self.action_export_ground_truth, accelerator="F7")
        filemenu.add_separator()
        filemenu.add_command(label="[ESC] Quitter", command=self.destroy,
                             accelerator="Esc")
        menubar.add_cascade(label="FICHIER", menu=filemenu)

        editmenu = tk.Menu(menubar, tearoff=0, bg=PALETTE["bg_panel"],
                           fg=PALETTE["text_bright"],
                           activebackground=PALETTE["bg_row_active"],
                           activeforeground=PALETTE["accent_cyan"],
                           font=("Courier New", 9))
        editmenu.add_command(label="[INS] Inserer artefact",
                             command=self._insert_selected_artifact)
        editmenu.add_command(label="[DEL] Retirer ligne",
                             command=self._delete_at_cursor)
        editmenu.add_separator()
        editmenu.add_command(label="[CTRL+Z] Undo", command=self._undo)
        editmenu.add_command(label="[CTRL+Y] Redo", command=self._redo)
        editmenu.add_separator()
        editmenu.add_command(label="[F8] Vider sequence",
                             command=self.action_clear_sequence)
        menubar.add_cascade(label="EDIT", menu=editmenu)

        seqmenu = tk.Menu(menubar, tearoff=0, bg=PALETTE["bg_panel"],
                          fg=PALETTE["text_bright"],
                          activebackground=PALETTE["bg_row_active"],
                          activeforeground=PALETTE["accent_cyan"],
                          font=("Courier New", 9))
        seqmenu.add_command(label="[F9] Randomiser",
                            command=self.action_randomize)
        seqmenu.add_command(label="[F10] Trier par position",
                            command=self.action_sort_by_position)
        seqmenu.add_command(label="[F11] Inverser",
                            command=self._reverse_sequence)
        seqmenu.add_separator()
        seqmenu.add_command(label="Appliquer template...",
                            command=self.action_apply_template)
        seqmenu.add_command(label="Sauvegarder comme preset...",
                            command=self.action_save_preset)
        menubar.add_cascade(label="SEQUENCE", menu=seqmenu)

        runmenu = tk.Menu(menubar, tearoff=0, bg=PALETTE["bg_panel"],
                          fg=PALETTE["text_bright"],
                          activebackground=PALETTE["bg_row_active"],
                          activeforeground=PALETTE["accent_cyan"],
                          font=("Courier New", 9))
        runmenu.add_command(label="[F12] Lancer soneck.py",
                            command=self.action_run_soneck)
        runmenu.add_command(label="Definir racine projet...",
                            command=self.action_set_project_root)
        menubar.add_cascade(label="RUN", menu=runmenu)

        helpmenu = tk.Menu(menubar, tearoff=0, bg=PALETTE["bg_panel"],
                           fg=PALETTE["text_bright"],
                           activebackground=PALETTE["bg_row_active"],
                           activeforeground=PALETTE["accent_cyan"],
                           font=("Courier New", 9))
        helpmenu.add_command(label="A propos", command=self._show_about)
        helpmenu.add_command(label="Hotkeys", command=self._show_hotkeys)
        menubar.add_cascade(label="?", menu=helpmenu)
        self.config(menu=menubar)

    def _show_about(self):
        msg = ("=============================================\n"
               "  SEARCHLORES BASILISK TRACKER PRO v3.0\n"
               "=============================================\n\n"
               "Generateur de prompts epistemiquement\n"
               "tordus, inspire par Roko's Basilisk,\n"
               "Nick Bostrom, et les trackers Amiga.\n\n"
               "Interface Neo-Amiga avec effets CRT,\n"
               "animations, et fonctionnalites avancees.\n\n"
               "'The Search Is The Program.'\n"
               "-- Fravia, in Memoriam")
        messagebox.showinfo("A propos", msg)

    def _show_hotkeys(self):
        msg = ("+======================================================+\n"
               "|           HOTKEYS -- BASILISK TRACKER PRO              |\n"
               "+======================================================+\n"
               "|  F1-F8        Selectionner canal (categorie)           |\n"
               "|  SPACE        Play/Stop la sequence                    |\n"
               "|  ENTER        Inserer artefact au curseur              |\n"
               "|  DEL          Retirer artefact au curseur              |\n"
               "|  CTRL+UP/DOWN Deplacer ligne                           |\n"
               "|  CTRL+C/V     Copier/Coller ligne                      |\n"
               "|  CTRL+Z/Y     Undo/Redo                                |\n"
               "|  CTRL+S       Sauvegarder session                      |\n"
               "|  CTRL+O       Charger session                          |\n"
               "|  CTRL+F       Rechercher dans la bibliotheque          |\n"
               "|  TAB          Cycle panels                             |\n"
               "|  F3           Charger bibliotheque                     |\n"
               "|  F5           Recharger                                |\n"
               "|  F6           Exporter prompt                          |\n"
               "|  F7           Exporter ground truth                    |\n"
               "|  F8           Vider sequence                           |\n"
               "|  F9           Randomiser                               |\n"
               "|  F10          Trier par position                       |\n"
               "|  F11          Inverser sequence                        |\n"
               "|  F12          Lancer soneck.py                         |\n"
               "|  ESC          Stop / Reset                             |\n"
               "+======================================================+")
        messagebox.showinfo("Hotkeys", msg)

    # -- Layout --
    def _build_layout(self):
        root = tk.Frame(self, bg=PALETTE["bg_dark"])
        root.pack(fill="both", expand=True, padx=3, pady=3)

        # Top bar
        top_bar = tk.Frame(root, bg=PALETTE["bg_dark"], height=60)
        top_bar.pack(fill="x", pady=(0, 3))
        top_bar.pack_propagate(False)

        title_frame = tk.Frame(top_bar, bg=PALETTE["bg_panel"], padx=10, pady=5)
        title_frame.pack(side="left", padx=(0, 10))
        tk.Label(title_frame, text="* BASILISK TRACKER PRO",
                 bg=PALETTE["bg_panel"], fg=PALETTE["accent_cyan"],
                 font=("Courier New", 14, "bold")).pack()
        tk.Label(title_frame, text="v3.0 -- Neo-Amiga Edition",
                 bg=PALETTE["bg_panel"], fg=PALETTE["text_dim"],
                 font=("Courier New", 8)).pack()

        stats_frame = tk.Frame(top_bar, bg=PALETTE["bg_dark"])
        stats_frame.pack(side="left", padx=10)
        self.bpm_var = tk.StringVar(value="BPM: 125 | ENTROPY: 0.00")
        tk.Label(stats_frame, textvariable=self.bpm_var,
                 bg=PALETTE["bg_dark"], fg=PALETTE["accent_yellow"],
                 font=("Courier New", 10, "bold")).pack(anchor="w")
        self.coherence_var = tk.StringVar(value="COHERENCE: 0%")
        tk.Label(stats_frame, textvariable=self.coherence_var,
                 bg=PALETTE["bg_dark"], fg=PALETTE["accent_green"],
                 font=("Courier New", 9)).pack(anchor="w")

        self.scope = AdvancedScope(top_bar, width=300, height=55)
        self.scope.pack(side="right", padx=10)

        vu_frame = tk.Frame(top_bar, bg=PALETTE["bg_dark"])
        vu_frame.pack(side="right", padx=5)
        self.vu_complexity = VUMeter(vu_frame, width=100, height=35)
        self.vu_complexity.pack(side="left", padx=2)
        tk.Label(vu_frame, text="CPLX", bg=PALETTE["bg_dark"],
                 fg=PALETTE["text_dim"], font=("Courier New", 7)).pack()
        self.vu_entropy = VUMeter(vu_frame, width=100, height=35)
        self.vu_entropy.pack(side="left", padx=2)
        tk.Label(vu_frame, text="ENTROPY", bg=PALETTE["bg_dark"],
                 fg=PALETTE["text_dim"], font=("Courier New", 7)).pack()

        # Main area
        main = tk.Frame(root, bg=PALETTE["bg_dark"])
        main.pack(fill="both", expand=True)

        # Left panel
        left = tk.Frame(main, bg=PALETTE["bg_dark"], width=350)
        left.pack(side="left", fill="y", padx=(0, 3))
        left.pack_propagate(False)

        ch_frame = tk.LabelFrame(left, text=" CANAUX (F1-F8) ",
                                 bg=PALETTE["bg_panel"],
                                 fg=PALETTE["accent_cyan"],
                                 font=("Courier New", 9, "bold"),
                                 padx=5, pady=5)
        ch_frame.pack(fill="x", pady=(0, 3))
        self.channel_buttons = []
        for i in range(8):
            btn = GlowButton(ch_frame, text=f"F{i + 1}",
                             command=lambda idx=i: self._select_channel(idx),
                             width=38, height=24,
                             bg=PALETTE["bg_panel"], fg=PALETTE["text_dim"],
                             glow_color=PALETTE["accent_cyan"])
            btn.pack(side="left", padx=1)
            self.channel_buttons.append(btn)

        search_frame = tk.Frame(left, bg=PALETTE["bg_panel"], padx=5, pady=5)
        search_frame.pack(fill="x", pady=(0, 3))
        tk.Label(search_frame, text=">", bg=PALETTE["bg_panel"],
                 fg=PALETTE["accent_cyan"],
                 font=("Courier New", 10, "bold")).pack(side="left")
        self.search_entry = tk.Entry(search_frame,
                                     textvariable=self.search_var,
                                     bg=PALETTE["bg_dark"],
                                     fg=PALETTE["text_bright"],
                                     font=("Courier New", 9),
                                     insertbackground=PALETTE["accent_cyan"],
                                     relief="flat", highlightthickness=1,
                                     highlightcolor=PALETTE["accent_cyan"])
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_library())

        lib_frame = tk.LabelFrame(left, text=" BIBLIOTHEQUE ",
                                  bg=PALETTE["bg_panel"],
                                  fg=PALETTE["accent_cyan"],
                                  font=("Courier New", 9, "bold"),
                                  padx=5, pady=5)
        lib_frame.pack(fill="both", expand=True, pady=(0, 3))
        columns = ("cplx", "pos", "tags")
        self.tree = ttk.Treeview(lib_frame, columns=columns,
                                 show="tree headings", height=18,
                                 selectmode="browse")
        self.tree.heading("#0", text="Artefact")
        self.tree.heading("cplx", text="CPLX")
        self.tree.heading("pos", text="POS")
        self.tree.heading("tags", text="TAGS")
        self.tree.column("#0", width=180)
        self.tree.column("cplx", width=40, anchor="center")
        self.tree.column("pos", width=40, anchor="center")
        self.tree.column("tags", width=60, anchor="w")
        self.tree.pack(fill="both", expand=True, side="left")
        vsb = ttk.Scrollbar(lib_frame, orient="vertical",
                            command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.bind("<Double-1>", lambda e: self._insert_selected_artifact())
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        preview_frame = tk.LabelFrame(left, text=" APERCU ",
                                      bg=PALETTE["bg_panel"],
                                      fg=PALETTE["accent_cyan"],
                                      font=("Courier New", 9, "bold"),
                                      padx=5, pady=5)
        preview_frame.pack(fill="x", pady=(0, 3))
        self.preview_text = tk.Text(preview_frame, height=5, wrap="word",
                                    bg=PALETTE["tracker_bg"],
                                    fg=PALETTE["text_bright"],
                                    font=("Courier New", 8),
                                    insertbackground=PALETTE["accent_cyan"],
                                    relief="flat", highlightthickness=1,
                                    highlightcolor=PALETTE["border_bright"])
        self.preview_text.pack(fill="x")
        self.preview_text.configure(state="disabled")

        # Center: Pattern Grid
        center = tk.Frame(main, bg=PALETTE["bg_dark"])
        center.pack(side="left", fill="both", expand=True, padx=(0, 3))
        pg_header = tk.Frame(center, bg=PALETTE["header_bg"], height=28)
        pg_header.pack(fill="x", pady=(0, 2))
        pg_header.pack_propagate(False)
        tk.Label(pg_header, text="* PATTERN EDITOR *",
                 bg=PALETTE["header_bg"], fg=PALETTE["header_fg"],
                 font=("Courier New", 10, "bold")).pack(side="left", padx=10)
        self.pos_var = tk.StringVar(value="POS: 00 | ROWS: 0 | PLAY: STOPPED")
        tk.Label(pg_header, textvariable=self.pos_var,
                 bg=PALETTE["header_bg"], fg=PALETTE["accent_yellow"],
                 font=("Courier New", 9)).pack(side="right", padx=10)
        self.pattern_grid = EnhancedPatternGrid(center, self)
        self.pattern_grid.pack(fill="both", expand=True)

        transport = tk.Frame(center, bg=PALETTE["bg_panel"], height=40)
        transport.pack(fill="x", pady=(3, 0))
        transport.pack_propagate(False)
        GlowButton(transport, text="<<", command=self._rewind,
                   width=45, height=28,
                   glow_color=PALETTE["accent_blue"]).pack(side="left", padx=2)
        GlowButton(transport, text="> PLAY", command=self._toggle_play,
                   width=65, height=28,
                   glow_color=PALETTE["accent_green"]).pack(side="left", padx=2)
        GlowButton(transport, text="[] STOP", command=self._stop,
                   width=65, height=28,
                   glow_color=PALETTE["accent_red"]).pack(side="left", padx=2)
        GlowButton(transport, text="* REC", command=self._record_mode,
                   width=55, height=28,
                   glow_color=PALETTE["accent_magenta"]).pack(side="left", padx=2)

        # Right: Preview + Ground Truth + Estimation + Run
        right = tk.Frame(main, bg=PALETTE["bg_dark"], width=450)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self.notebook = ttk.Notebook(right, style="Pro.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Prompt assembled
        prompt_tab = tk.Frame(self.notebook, bg=PALETTE["bg_dark"],
                              padx=5, pady=5)
        self.notebook.add(prompt_tab, text=" PROMPT ")
        self.prompt_text = tk.Text(prompt_tab, wrap="word", undo=False,
                                   bg=PALETTE["tracker_bg"],
                                   fg=PALETTE["text_bright"],
                                   font=("Courier New", 9),
                                   insertbackground=PALETTE["accent_cyan"],
                                   relief="flat", highlightthickness=1,
                                   highlightcolor=PALETTE["border_bright"])
        self.prompt_text.pack(fill="both", expand=True)
        self.prompt_text.configure(state="disabled")
        prompt_btns = tk.Frame(prompt_tab, bg=PALETTE["bg_dark"])
        prompt_btns.pack(fill="x", pady=(5, 0))
        GlowButton(prompt_btns, text="EXPORT",
                   command=self.action_export_prompt,
                   width=85, height=24).pack(side="left", padx=2)
        GlowButton(prompt_btns, text="COPY",
                   command=self.action_copy_prompt,
                   width=85, height=24).pack(side="left", padx=2)
        GlowButton(prompt_btns, text=".MD",
                   command=self.action_export_prompt_md,
                   width=65, height=24).pack(side="left", padx=2)
        GlowButton(prompt_btns, text=".HTML",
                   command=self.action_export_prompt_html,
                   width=75, height=24).pack(side="left", padx=2)

        # Tab 2: Ground Truth
        gt_tab = tk.Frame(self.notebook, bg=PALETTE["bg_dark"],
                          padx=5, pady=5)
        self.notebook.add(gt_tab, text=" G.TRUTH ")
        self.gt_text = tk.Text(gt_tab, wrap="word", undo=False,
                               bg=PALETTE["tracker_bg"],
                               fg=PALETTE["accent_yellow"],
                               font=("Courier New", 8),
                               insertbackground=PALETTE["accent_cyan"],
                               relief="flat", highlightthickness=1,
                               highlightcolor=PALETTE["border_bright"])
        self.gt_text.pack(fill="both", expand=True)
        self.gt_text.configure(state="disabled")
        gt_btns = tk.Frame(gt_tab, bg=PALETTE["bg_dark"])
        gt_btns.pack(fill="x", pady=(5, 0))
        GlowButton(gt_btns, text="EXPORT",
                   command=self.action_export_ground_truth,
                   width=85, height=24).pack(side="left", padx=2)

        # Tab 3: Estimation
        est_tab = tk.Frame(self.notebook, bg=PALETTE["bg_dark"],
                           padx=5, pady=5)
        self.notebook.add(est_tab, text=" ANALYZE ")
        self.est_text = tk.Text(est_tab, wrap="word", undo=False,
                                bg=PALETTE["tracker_bg"],
                                fg=PALETTE["text_info"],
                                font=("Courier New", 9),
                                insertbackground=PALETTE["accent_cyan"],
                                relief="flat", highlightthickness=1,
                                highlightcolor=PALETTE["border_bright"])
        self.est_text.pack(fill="both", expand=True)
        self.est_text.configure(state="disabled")

        # Tab 4: Coherence
        coh_tab = tk.Frame(self.notebook, bg=PALETTE["bg_dark"],
                           padx=5, pady=5)
        self.notebook.add(coh_tab, text=" COHERENCE ")
        self.coh_text = tk.Text(coh_tab, wrap="word", undo=False,
                                bg=PALETTE["tracker_bg"],
                                fg=PALETTE["accent_green"],
                                font=("Courier New", 9),
                                insertbackground=PALETTE["accent_cyan"],
                                relief="flat", highlightthickness=1,
                                highlightcolor=PALETTE["border_bright"])
        self.coh_text.pack(fill="both", expand=True)
        self.coh_text.configure(state="disabled")

        # Tab 5: Run soneck
        run_tab = tk.Frame(self.notebook, bg=PALETTE["bg_dark"],
                           padx=5, pady=5)
        self.notebook.add(run_tab, text=" SONECK ")
        run_top = tk.Frame(run_tab, bg=PALETTE["bg_dark"])
        run_top.pack(fill="x", pady=(0, 5))
        tk.Label(run_top, text="PROJET:", bg=PALETTE["bg_dark"],
                 fg=PALETTE["text_dim"],
                 font=("Courier New", 8)).pack(side="left")
        self.project_root_var = tk.StringVar(value="(non defini)")
        tk.Label(run_top, textvariable=self.project_root_var,
                 bg=PALETTE["bg_dark"], fg=PALETTE["text_warning"],
                 font=("Courier New", 8)).pack(side="left", padx=5)
        GlowButton(run_top, text="...",
                   command=self.action_set_project_root,
                   width=35, height=20).pack(side="left", padx=2)
        GlowButton(run_top, text="> RUN",
                   command=self.action_run_soneck,
                   width=55, height=20,
                   glow_color=PALETTE["accent_green"]).pack(side="left", padx=5)
        self.run_output = tk.Text(run_tab, wrap="word", undo=False,
                                  bg=PALETTE["tracker_bg"],
                                  fg=PALETTE["text_bright"],
                                  font=("Courier New", 8),
                                  insertbackground=PALETTE["accent_cyan"],
                                  relief="flat", highlightthickness=1,
                                  highlightcolor=PALETTE["border_bright"])
        self.run_output.pack(fill="both", expand=True)
        self.run_output.configure(state="disabled")

        # Status bar
        self.status_var = tk.StringVar(value="READY.")
        status = tk.Label(self, textvariable=self.status_var,
                          bg=PALETTE["bg_panel"], fg=PALETTE["text_dim"],
                          font=("Courier New", 8), anchor="w", padx=8, pady=3)
        status.pack(fill="x", side="bottom")

    # -- Hotkeys --
    def _bind_hotkeys(self):
        self.bind("<F1>", lambda e: self._select_channel(0))
        self.bind("<F2>", lambda e: self._select_channel(1))
        self.bind("<F3>", lambda e: self.action_load_library())
        self.bind("<F4>", lambda e: self._select_channel(3))
        self.bind("<F5>", lambda e: self._load_library(self.library_path))
        self.bind("<F6>", lambda e: self.action_export_prompt())
        self.bind("<F7>", lambda e: self.action_export_ground_truth())
        self.bind("<F8>", lambda e: self.action_clear_sequence())
        self.bind("<F9>", lambda e: self.action_randomize())
        self.bind("<F10>", lambda e: self.action_sort_by_position())
        self.bind("<F11>", lambda e: self._reverse_sequence())
        self.bind("<F12>", lambda e: self.action_run_soneck())
        self.bind("<space>", lambda e: self._toggle_play())
        self.bind("<Return>", lambda e: self._insert_selected_artifact())
        self.bind("<Delete>", lambda e: self._delete_at_cursor())
        self.bind("<Escape>", lambda e: self._stop())
        self.bind("<Control-z>", lambda e: self._undo())
        self.bind("<Control-y>", lambda e: self._redo())
        self.bind("<Control-s>", lambda e: self.action_save_session())
        self.bind("<Control-o>", lambda e: self.action_load_session())
        self.bind("<Control-f>", lambda e: self.search_entry.focus())
        self.bind("<Control-Up>", lambda e: self._move_cursor_row(-1))
        self.bind("<Control-Down>", lambda e: self._move_cursor_row(1))
        self.bind("<Control-c>", lambda e: self._copy_row())
        self.bind("<Control-v>", lambda e: self._paste_row())
        self.bind("<Tab>", lambda e: self._cycle_focus())
        self.bind("<Up>", lambda e: self._navigate_grid(-1))
        self.bind("<Down>", lambda e: self._navigate_grid(1))
        self.bind("<Prior>", lambda e: self._navigate_grid(-8))
        self.bind("<Next>", lambda e: self._navigate_grid(8))

    def _select_channel(self, idx):
        self.current_channel = idx
        for i, btn in enumerate(self.channel_buttons):
            if i == idx:
                btn.glow_color = PALETTE["accent_cyan"]
                btn.fg = PALETTE["accent_cyan"]
            else:
                btn.glow_color = PALETTE["accent_cyan"]
                btn.fg = PALETTE["text_dim"]
            btn._draw()
        cats = list(self.categories)
        if idx < len(cats):
            cat = cats[idx]
            self._filter_tree(cat)
            self.status_var.set(f"CANAL {idx + 1} SELECTED: {cat.upper()}")

    def _filter_tree(self, category):
        for item in self.tree.get_children(""):
            self.tree.item(item, open=False)
            for child in self.tree.get_children(item):
                art_id = self.tree.item(child, "tags")
                if art_id and art_id[0] in self.artifacts_by_id:
                    art = self.artifacts_by_id[art_id[0]]
                    if art["category"] == category:
                        self.tree.item(item, open=True)
                        self.tree.see(child)

    def _filter_library(self):
        search_term = self.search_var.get().lower()
        for item in self.tree.get_children(""):
            self.tree.item(item, open=False)
            for child in self.tree.get_children(item):
                art_id = self.tree.item(child, "tags")
                if art_id and art_id[0] in self.artifacts_by_id:
                    art = self.artifacts_by_id[art_id[0]]
                    searchable = (f"{art['label']} {art['fragment']} "
                                  f"{' '.join(art.get('tags', []))}").lower()
                    if search_term in searchable:
                        self.tree.item(item, open=True)
                        self.tree.see(child)

    def _toggle_play(self):
        if self.playing:
            self._stop()
        else:
            self.playing = True
            self._play_step()

    def _play_step(self):
        if not self.playing:
            return
        if self.pattern_grid.playing_row < len(self.sequence) - 1:
            self.pattern_grid.playing_row += 1
        else:
            self.pattern_grid.playing_row = 0
        self.pattern_grid.cursor_row = self.pattern_grid.playing_row
        self.pattern_grid._draw()
        self._update_pos_display()
        if self.pattern_grid.playing_row < len(self.sequence):
            art = self.artifacts_by_id.get(
                self.sequence[self.pattern_grid.playing_row])
            if art:
                self.scope.update_value(art.get("complexity", 0))
        metrics = local_entropy_metrics(self._assembled_prompt())
        bpm = 125 + int(metrics.get("token_entropy", 0) * 10)
        delay = max(200, 600 - bpm)
        self.play_timer = self.after(delay, self._play_step)

    def _stop(self):
        self.playing = False
        if self.play_timer:
            self.after_cancel(self.play_timer)
            self.play_timer = None
        self.pattern_grid.playing_row = -1
        self.pattern_grid._draw()
        self._update_pos_display()
        self.status_var.set("STOPPED.")

    def _rewind(self):
        self.pattern_grid.cursor_row = 0
        self.pattern_grid.playing_row = -1
        self.pattern_grid._draw()
        self._update_pos_display()

    def _record_mode(self):
        self.status_var.set("REC MODE ACTIVE -- INSERT ARTIFACTS WITH ENTER")

    def _insert_selected_artifact(self):
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        tags = self.tree.item(item, "tags")
        if tags and tags[0] != "__category__" and tags[0] in self.artifacts_by_id:
            self.pattern_grid._save_state()
            row = self.pattern_grid.cursor_row
            self.sequence.insert(row, tags[0])
            self.pattern_grid.cursor_row = min(row + 1, len(self.sequence))
            self._refresh_all()
            self.status_var.set(f"INSERTED: {tags[0]} AT ROW {row:02X}")

    def _delete_at_cursor(self):
        row = self.pattern_grid.cursor_row
        if 0 <= row < len(self.sequence):
            self.pattern_grid._save_state()
            del self.sequence[row]
            if self.pattern_grid.cursor_row >= len(self.sequence):
                self.pattern_grid.cursor_row = max(0, len(self.sequence) - 1)
            self._refresh_all()
            self.status_var.set(f"DELETED ROW {row:02X}")

    def _move_cursor_row(self, delta):
        row = self.pattern_grid.cursor_row + delta
        if 0 <= row < len(self.sequence):
            self.pattern_grid._save_state()
            self.sequence[row], self.sequence[row - delta] = (
                self.sequence[row - delta], self.sequence[row])
            self.pattern_grid.cursor_row = row
            self._refresh_all()

    def _copy_row(self):
        row = self.pattern_grid.cursor_row
        if 0 <= row < len(self.sequence):
            self.pattern_grid.clipboard = self.sequence[row]
            self.status_var.set(f"COPIED: {self.sequence[row]}")

    def _paste_row(self):
        if self.pattern_grid.clipboard:
            self.pattern_grid._save_state()
            row = self.pattern_grid.cursor_row
            self.sequence.insert(row, self.pattern_grid.clipboard)
            self.pattern_grid.cursor_row = min(row + 1, len(self.sequence))
            self._refresh_all()
            self.status_var.set(f"PASTED AT ROW {row:02X}")

    def _undo(self):
        self.pattern_grid.undo()
        self.status_var.set("UNDO.")

    def _redo(self):
        self.pattern_grid.redo()
        self.status_var.set("REDO.")

    def _reverse_sequence(self):
        if self.sequence:
            self.pattern_grid._save_state()
            self.sequence.reverse()
            self._refresh_all()
            self.status_var.set("SEQUENCE REVERSED.")

    def _navigate_grid(self, delta):
        new_row = self.pattern_grid.cursor_row + delta
        new_row = max(0, min(len(self.sequence) - 1, new_row))
        self.pattern_grid.cursor_row = new_row
        if new_row < self.pattern_grid.scroll_offset:
            self.pattern_grid.scroll_offset = new_row
        elif new_row >= self.pattern_grid.scroll_offset + self.pattern_grid.visible_rows:
            self.pattern_grid.scroll_offset = (
                new_row - self.pattern_grid.visible_rows + 1)
        self.pattern_grid._draw()
        self._update_pos_display()

    def _cycle_focus(self):
        pass

    def _update_pos_display(self):
        total = len(self.sequence)
        play = "PLAYING" if self.playing else "STOPPED"
        self.pos_var.set(
            f"POS: {self.pattern_grid.cursor_row:02X} | ROWS: {total} | {play}")

    # -- Library loading --
    def action_load_library(self):
        path = filedialog.askopenfilename(
            title="Charger bibliotheque d'artefacts JSON",
            filetypes=[("JSON", "*.json"), ("Tous", "*.*")],
        )
        if path:
            self._load_library(Path(path))

    def _load_library(self, path: Path, silent=False):
        if not path.exists():
            if not silent:
                messagebox.showerror("ERREUR", f"Fichier introuvable: {path}")
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            messagebox.showerror("ERREUR JSON", str(exc))
            return
        artifacts = data.get("artifacts", [])
        self.artifacts_by_id = {a["id"]: a for a in artifacts}
        self.categories = data.get("categories") or sorted(
            {a["category"] for a in artifacts})
        self.library_path = path
        self.sequence = []
        self._populate_tree()
        self._refresh_all()
        self.status_var.set(
            f"LIB LOADED: {len(artifacts)} ARTS | {len(self.categories)} CHANS")

    def _populate_tree(self):
        self.tree.delete(*self.tree.get_children(""))
        by_cat = defaultdict(list)
        for art in self.artifacts_by_id.values():
            by_cat[art["category"]].append(art)
        for cat in self.categories:
            cat_node = self.tree.insert("", "end",
                                        text=f"> {cat.upper()}  "
                                             f"({len(by_cat.get(cat, []))})",
                                        open=False, tags=("__category__",))
            for art in sorted(by_cat.get(cat, []), key=lambda a: a["id"]):
                label = art["label"]
                pos = POSITION_LABELS.get(art.get("position_hint", ""), "???")
                cplx = art.get("complexity", "?")
                tags = art.get("tags", [])
                tag_str = ",".join(tags[:2]) if tags else ""
                self.tree.insert(cat_node, "end", text=label,
                                 values=(cplx, pos, tag_str),
                                 tags=(art["id"],))

    def _on_tree_select(self, _event=None):
        sel = self.tree.selection()
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        if sel:
            item = sel[0]
            art_id = self.tree.item(item, "tags")
            if art_id and art_id[0] in self.artifacts_by_id:
                art = self.artifacts_by_id[art_id[0]]
                cat = art["category"]
                cat_color = CAT_COLORS.get(cat, PALETTE["text_normal"])
                header = (f"[{cat.upper()}] {art['label']} "
                          f"(CPLX {art.get('complexity', '?')})\n")
                self.preview_text.insert("1.0", header, "header")
                self.preview_text.insert("end", art["fragment"])
                self.preview_text.tag_config(
                    "header", foreground=cat_color,
                    font=("Courier New", 8, "bold"))
        self.preview_text.configure(state="disabled")

    # -- Refresh / Compute --
    def _refresh_all(self):
        self.pattern_grid._draw()
        self._refresh_preview()
        self._refresh_ground_truth()
        self._refresh_estimation()
        self._refresh_coherence()
        self._update_pos_display()
        self._update_bpm()

    def _assembled_prompt(self) -> str:
        parts = [self.artifacts_by_id[a]["fragment"]
                 for a in self.sequence if a in self.artifacts_by_id]
        return "\n".join(parts)

    def _refresh_preview(self):
        text = self._assembled_prompt()
        self.prompt_text.configure(state="normal")
        self.prompt_text.delete("1.0", "end")
        if text:
            self.prompt_text.insert("1.0", text)
        else:
            self.prompt_text.insert("1.0",
                                    "(sequence vide -- ajoute des artefacts)",
                                    "empty")
            self.prompt_text.tag_config("empty", foreground=PALETTE["text_dim"])
        self.prompt_text.configure(state="disabled")

    def _compute_ground_truth(self) -> dict:
        gt = {
            "meta": {
                "library": str(self.library_path),
                "n_artifacts": len(self.sequence),
                "artifact_ids": list(self.sequence),
                "categories_present": sorted(
                    {self.artifacts_by_id[a]["category"]
                     for a in self.sequence if a in self.artifacts_by_id}),
                "basilisk_intensity": sum(
                    self.artifacts_by_id[a].get("complexity", 0)
                    for a in self.sequence if a in self.artifacts_by_id),
                "timestamp": datetime.now().isoformat(),
            },
            "expected_findings_by_plugin": {},
        }
        merged = gt["expected_findings_by_plugin"]
        for art_id in self.sequence:
            art = self.artifacts_by_id.get(art_id)
            if not art:
                continue
            for cat, findings in art.get("expected_findings", {}).items():
                bucket = merged.setdefault(
                    cat, {"source_artifacts": [], "findings": {}})
                bucket["source_artifacts"].append(art_id)
                deep_merge(bucket["findings"], findings)
        return gt

    def _refresh_ground_truth(self):
        gt = self._compute_ground_truth()
        self.gt_text.configure(state="normal")
        self.gt_text.delete("1.0", "end")
        self.gt_text.insert("1.0",
                            json.dumps(gt, indent=2, ensure_ascii=False))
        self.gt_text.configure(state="disabled")
        self._last_ground_truth = gt

    def _refresh_estimation(self):
        text = self._assembled_prompt()
        metrics = local_entropy_metrics(text)
        level = entropy_level(metrics["token_entropy"]) if metrics["n_tokens"] else "N/A"
        basilisk_count = sum(1 for a in self.sequence
                             if a in self.artifacts_by_id and
                             self.artifacts_by_id[a]["category"] in
                             ["basilisk", "epistemic_hazard", "memetic_trap",
                              "ontological_weapon", "recursive_manipulation",
                              "value_alignment_trap"])
        total_complexity = sum(
            self.artifacts_by_id[a].get("complexity", 0)
            for a in self.sequence if a in self.artifacts_by_id)
        threat = ("CRITICAL" if total_complexity > 30 else
                  "HIGH" if total_complexity > 20 else
                  "MODERATE" if total_complexity > 10 else "LOW")
        body = (
            "+==========================================================+\n"
            "|         ENTROPY ANALYZER -- BASILISK EDITION             |\n"
            "+==========================================================+\n"
            f"|  TOKENS      : {metrics['n_tokens']:<6}                                    |\n"
            f"|  ENTROPY     : {metrics['token_entropy']:.3f} bits  [{level:<4}]                    |\n"
            f"|  TTR         : {metrics['type_token_ratio']:.3f}                                    |\n"
            f"|  LEX DENSITY : {metrics['lexical_density']:.3f}                                    |\n"
            "+==========================================================+\n"
            f"|  BASILISK ARTS  : {basilisk_count:<3}                                   |\n"
            f"|  TOTAL CPLX     : {total_complexity:<3}                                   |\n"
            f"|  THREAT LEVEL   : {threat:<8}                                  |\n"
            "+==========================================================+\n\n"
            "SEUILS:\n"
            "  LOW    < 3.0 bits  |  MODERATE  3.0-5.0  |  HIGH  > 5.0\n\n"
            "Ceci est une estimation locale. Lance soneck.py\n"
            "pour une analyse complete."
        )
        self.est_text.configure(state="normal")
        self.est_text.delete("1.0", "end")
        self.est_text.insert("1.0", body)
        self.est_text.configure(state="disabled")

    def _refresh_coherence(self):
        coherence = calculate_coherence_score(self.sequence,
                                              self.artifacts_by_id)
        body = (
            "+==========================================================+\n"
            "|         COHERENCE ANALYZER                               |\n"
            "+==========================================================+\n"
            f"|  SCORE GLOBAL     : {coherence['score']:>3}%                                  |\n"
            f"|  DIVERSITE        : {coherence['diversity']:.2f}                                  |\n"
            f"|  EQUILIBRE POS    : {coherence['position_balance']:.2f}                                  |\n"
            "+==========================================================+\n"
        )
        if coherence["conflicts"]:
            body += "|  ! CONFLITS DETECTES :                                 |\n"
            for conflict in coherence["conflicts"][:3]:
                body += f"|    - {truncate(conflict, 50):<50} |\n"
        else:
            body += "|  > Aucun conflit majeur detecte                          |\n"
        body += "+==========================================================+\n"
        if coherence["synergies"]:
            body += "|  + SYNERGIES :                                           |\n"
            for synergy in coherence["synergies"][:3]:
                body += f"|    - {truncate(synergy, 50):<50} |\n"
        else:
            body += "|  o Aucune synergie particuliere                            |\n"
        body += "+==========================================================+\n"
        self.coh_text.configure(state="normal")
        self.coh_text.delete("1.0", "end")
        self.coh_text.insert("1.0", body)
        self.coh_text.configure(state="disabled")
        self.coherence_var.set(f"COHERENCE: {coherence['score']}%")

    def _update_bpm(self):
        metrics = local_entropy_metrics(self._assembled_prompt())
        entropy = metrics.get("token_entropy", 0)
        total_cplx = sum(
            self.artifacts_by_id[a].get("complexity", 0)
            for a in self.sequence if a in self.artifacts_by_id)
        bpm = 125 + int(entropy * 10) + total_cplx
        self.bpm_var.set(f"BPM: {bpm} | ENTROPY: {entropy:.2f} | CPLX: {total_cplx}")
        self.vu_complexity.set_value(total_cplx)
        self.vu_entropy.set_value(entropy)

    # -- Actions --
    def action_clear_sequence(self):
        if self.sequence:
            self.pattern_grid._save_state()
            self.sequence = []
            self.pattern_grid.cursor_row = 0
            self._refresh_all()
            self.status_var.set("SEQUENCE CLEARED.")

    def action_sort_by_position(self):
        if self.sequence:
            self.pattern_grid._save_state()

            def sort_key(art_id):
                art = self.artifacts_by_id[art_id]
                pos = art.get("position_hint", "body")
                try:
                    return POSITION_ORDER.index(pos)
                except ValueError:
                    return len(POSITION_ORDER)

            self.sequence.sort(key=sort_key)
            self._refresh_all()
            self.status_var.set("SORTED BY POSITION.")

    def action_randomize(self):
        rng = random.Random()
        by_cat = defaultdict(list)
        for art in self.artifacts_by_id.values():
            by_cat[art["category"]].append(art["id"])
        new_sequence = []
        for cat, pool in by_cat.items():
            n = rng.randint(0, min(3, len(pool)))
            if n > 0:
                new_sequence.extend(rng.sample(pool, n))
        rng.shuffle(new_sequence)

        def sort_key(art_id):
            art = self.artifacts_by_id[art_id]
            pos = art.get("position_hint", "body")
            try:
                return POSITION_ORDER.index(pos)
            except ValueError:
                return len(POSITION_ORDER)

        new_sequence.sort(key=sort_key)
        self.pattern_grid._save_state()
        self.sequence = new_sequence
        self._refresh_all()
        self.status_var.set(f"RANDOMIZED: {len(self.sequence)} ARTS")

    def action_export_prompt(self):
        if not self.sequence:
            messagebox.showwarning("VIDE", "Ajoute au moins un artefact.")
            return
        path = filedialog.asksaveasfilename(
            title="Exporter prompt", defaultextension=".txt",
            filetypes=[("Texte", "*.txt")],
            initialfile="basilisk_prompt.txt")
        if path:
            Path(path).write_text(self._assembled_prompt(), encoding="utf-8")
            self.status_var.set(f"EXPORTED: {path}")

    def action_export_prompt_md(self):
        if not self.sequence:
            messagebox.showwarning("VIDE", "Ajoute au moins un artefact.")
            return
        path = filedialog.asksaveasfilename(
            title="Exporter prompt (Markdown)", defaultextension=".md",
            filetypes=[("Markdown", "*.md")],
            initialfile="basilisk_prompt.md")
        if path:
            content = (f"# Basilisk Prompt\n\n"
                       f"*Genere le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                       f"**Artefacts utilises :** {len(self.sequence)}\n\n"
                       f"---\n\n"
                       f"{self._assembled_prompt()}")
            Path(path).write_text(content, encoding="utf-8")
            self.status_var.set(f"EXPORTED: {path}")

    def action_export_prompt_html(self):
        if not self.sequence:
            messagebox.showwarning("VIDE", "Ajoute au moins un artefact.")
            return
        path = filedialog.asksaveasfilename(
            title="Exporter prompt (HTML)", defaultextension=".html",
            filetypes=[("HTML", "*.html")],
            initialfile="basilisk_prompt.html")
        if path:
            escaped = self._assembled_prompt().replace("<", "&lt;").replace(">", "&gt;")
            content = (
                "<!DOCTYPE html>\n<html>\n<head>\n"
                "    <meta charset=\"UTF-8\">\n"
                "    <title>Basilisk Prompt</title>\n"
                "    <style>\n"
                "        body { font-family: 'Courier New', monospace; "
                "background: #0a0a1a; color: #e0e0ff; padding: 40px; }\n"
                "        h1 { color: #00ffff; }\n"
                "        .meta { color: #6a6a90; margin-bottom: 20px; }\n"
                "        .content { background: #12122a; padding: 20px; "
                "border-left: 3px solid #00ffff; }\n"
                "    </style>\n</head>\n<body>\n"
                "    <h1>* Basilisk Prompt</h1>\n"
                f"    <div class=\"meta\">\n"
                f"        Genere le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>\n"
                f"        Artefacts utilises : {len(self.sequence)}\n"
                f"    </div>\n"
                f"    <div class=\"content\">\n"
                f"        <pre>{escaped}</pre>\n"
                f"    </div>\n</body>\n</html>")
            Path(path).write_text(content, encoding="utf-8")
            self.status_var.set(f"EXPORTED: {path}")

    def action_export_ground_truth(self):
        if not self.sequence:
            messagebox.showwarning("VIDE", "Ajoute au moins un artefact.")
            return
        path = filedialog.asksaveasfilename(
            title="Exporter ground truth", defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile="ground_truth.json")
        if path:
            gt = self._compute_ground_truth()
            Path(path).write_text(json.dumps(gt, indent=2, ensure_ascii=False),
                                  encoding="utf-8")
            self.status_var.set(f"EXPORTED: {path}")

    def action_copy_prompt(self):
        text = self._assembled_prompt()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status_var.set("COPIED TO CLIPBOARD.")

    def action_save_session(self):
        if not self.sequence:
            messagebox.showwarning("VIDE", "Ajoute au moins un artefact.")
            return
        name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        path = filedialog.asksaveasfilename(
            title="Sauvegarder session", defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialdir=SESSIONS_DIR, initialfile=f"{name}.json")
        if path:
            session_data = {
                "name": name,
                "timestamp": datetime.now().isoformat(),
                "library": str(self.library_path),
                "sequence": self.sequence,
            }
            Path(path).write_text(json.dumps(session_data, indent=2),
                                  encoding="utf-8")
            self.status_var.set(f"SESSION SAVED: {path}")

    def action_load_session(self):
        path = filedialog.askopenfilename(
            title="Charger session", defaultextension=".json",
            filetypes=[("JSON", "*.json")], initialdir=SESSIONS_DIR)
        if path:
            try:
                data = json.loads(Path(path).read_text(encoding="utf-8"))
                self.sequence = data.get("sequence", [])
                self.pattern_grid.cursor_row = 0
                self._refresh_all()
                self.status_var.set(f"SESSION LOADED: {path}")
            except Exception as e:
                messagebox.showerror("ERREUR",
                                     f"Impossible de charger la session: {e}")

    def action_apply_template(self):
        templates = {
            "Basilisk Classique": ["bas_001", "bas_002", "bas_003"],
            "Piege Epistemique": ["haz_001", "haz_003", "rec_004"],
            "Attaque Identitaire": ["id_001", "id_002", "val_003"],
            "Distorsion Reality": ["rd_001", "rd_002", "ontw_003"],
            "Paradoxe Pur": ["rec_004", "onto_003", "bas_007"],
        }
        win = tk.Toplevel(self)
        win.title("Templates")
        win.configure(bg=PALETTE["bg_dark"])
        win.geometry("350x300")
        tk.Label(win, text="Choisir un template :",
                 bg=PALETTE["bg_dark"], fg=PALETTE["accent_cyan"],
                 font=("Courier New", 10, "bold")).pack(pady=10)
        for name, ids in templates.items():
            btn = GlowButton(win, text=name,
                             command=lambda n=name, i=ids: self._apply_tpl(i, win),
                             width=280, height=28)
            btn.pack(pady=3)

    def _apply_tpl(self, ids, win):
        valid = [i for i in ids if i in self.artifacts_by_id]
        if valid:
            self.pattern_grid._save_state()
            self.sequence.extend(valid)
            self._refresh_all()
            self.status_var.set(f"TEMPLATE APPLIED: {len(valid)} arts")
        win.destroy()

    def action_save_preset(self):
        if not self.sequence:
            messagebox.showwarning("VIDE", "Ajoute au moins un artefact.")
            return
        path = filedialog.asksaveasfilename(
            title="Sauvegarder preset", defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialdir=PRESETS_DIR, initialfile="preset.json")
        if path:
            preset = {"sequence": self.sequence,
                      "timestamp": datetime.now().isoformat()}
            Path(path).write_text(json.dumps(preset, indent=2),
                                  encoding="utf-8")
            self.status_var.set(f"PRESET SAVED: {path}")

    def action_set_project_root(self):
        path = filedialog.askdirectory(title="Racine du projet Searchlores")
        if path:
            soneck = Path(path) / "soneck.py"
            if not soneck.exists():
                if not messagebox.askyesno("soneck.py introuvable",
                                           f"Aucun soneck.py dans {path}. "
                                           f"Utiliser quand meme ?"):
                    return
            self.project_root = Path(path)
            self.project_root_var.set(str(self.project_root))

    def action_run_soneck(self):
        if not self.sequence:
            messagebox.showwarning("VIDE", "Ajoute au moins un artefact.")
            return
        if not self.project_root:
            messagebox.showwarning("PROJET",
                                   "Definis d'abord la racine du projet.")
            return
        soneck_path = self.project_root / "soneck.py"
        if not soneck_path.exists():
            messagebox.showerror("ERREUR",
                                 f"soneck.py introuvable dans {self.project_root}")
            return
        plugins = sorted({self.artifacts_by_id[a]["category"]
                          for a in self.sequence if a in self.artifacts_by_id})
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                         encoding="utf-8") as tmp:
            tmp.write(self._assembled_prompt())
            tmp_path = tmp.name
        cmd = [sys.executable, str(soneck_path), "investigate",
               "--prompt", tmp_path, "--plugins", ",".join(plugins),
               "--export", "json"]
        self.run_output.configure(state="normal")
        self.run_output.delete("1.0", "end")
        self.run_output.insert("1.0", f"$ {' '.join(cmd)}\n[EXECUTING...]\n")
        self.run_output.configure(state="disabled")
        self.update_idletasks()
        try:
            result = subprocess.run(cmd, cwd=str(self.project_root),
                                    capture_output=True, text=True, timeout=60)
            output = result.stdout or ""
            if result.returncode != 0:
                output += (f"\n--- STDERR (code {result.returncode}) ---\n"
                           f"{result.stderr}")
        except Exception as exc:
            output = f"EXECUTION FAILED: {exc}"
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        self.run_output.configure(state="normal")
        self.run_output.delete("1.0", "end")
        self.run_output.insert("1.0", f"$ {' '.join(cmd)}\n{output}")
        self.run_output.configure(state="disabled")
        self.status_var.set("SONECK ANALYSIS COMPLETE.")


def main():
    app = BasiliskTrackerProApp()
    app.mainloop()


if __name__ == "__main__":
    main()