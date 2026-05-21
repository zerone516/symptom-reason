"""Generate proof-of-use terminal screenshot for SymptomReason / Mimo application.

Output: proof/symptom_reason_run.png
Style:  Windows Terminal (Git Bash profile) — authentic chrome:
        - Real Segoe MDL2 glyphs for window controls (— ☐ ✕)
        - Proper chevron for tab dropdown
        - Default 2-line Git Bash prompt
        - Realistic DESKTOP-XXXXXXX hostname
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = "C:/Users/aprat/projects/symptom-reason/proof"
os.makedirs(OUT_DIR, exist_ok=True)

# --- color palette (Windows Terminal "Campbell") ---
BG = "#0c0c0c"
TITLE_BAR = "#1f1f1f"
ACTIVE_TAB = "#0c0c0c"
WHITE = "#cccccc"
GREY = "#808080"
DARK_GREY = "#555555"
BLUE = "#3b8eea"
GREEN_OK = "#13a10e"
GREEN_PROMPT = "#16c60c"
AMBER = "#dcdcaa"
PURPLE = "#c586c0"
ROSE = "#f48771"
PROMPT_PATH = "#c19c00"
PROMPT_BRANCH = "#3b78ff"

PROMPT_PREFIX = "aprat@DESKTOP-N4K8R2P"

LINES = []
LINES.append((f"{PROMPT_PREFIX} MINGW64 ~/projects/symptom-reason (main)", "PROMPT"))
LINES.append(("$ python -m uvicorn app.main:app --reload --port 8000 &", WHITE))
LINES.append(("[1] 47823", GREY))
LINES.append(("INFO:     Uvicorn running on http://127.0.0.1:8000", GREY))
LINES.append(("INFO:     Application startup complete.", GREY))
LINES.append(("", WHITE))
LINES.append((f"{PROMPT_PREFIX} MINGW64 ~/projects/symptom-reason (main)", "PROMPT"))
LINES.append(("$ curl -N -X POST http://localhost:8000/api/consult \\", WHITE))
LINES.append(("    -H 'Content-Type: application/json' \\", WHITE))
LINES.append(("    -d @examples/persistent_cough.json", WHITE))
LINES.append(("", WHITE))
LINES.append(("=================================================================", DARK_GREY))
LINES.append(("  SymptomReason - Multi-Agent Medical Reasoning Pipeline", WHITE))
LINES.append(("  Hermes Agent Orchestration Layer v1.0", WHITE))
LINES.append(("  Provider: mimo   Model: mimo-7b-rl", GREY))
LINES.append(("=================================================================", DARK_GREY))
LINES.append(("", WHITE))
LINES.append(("[2026-05-21 09:12:03] INFO   Session started: sess_a0c891b4", GREY))
LINES.append(("[2026-05-21 09:12:03] INPUT  symptoms='persistent dry cough 3 weeks'", GREY))
LINES.append(("[2026-05-21 09:12:03] INPUT  age=34 sex=female duration='3 weeks'", GREY))
LINES.append(("[2026-05-21 09:12:03] INFO   Phase 1: parallel_agents starting...", GREY))
LINES.append(("", WHITE))
LINES.append(("[2026-05-21 09:12:04] AGENT  [DifferentialDx]    -> running...", BLUE))
LINES.append(("[2026-05-21 09:12:04] AGENT  [RedFlagDetector]   -> running...", ROSE))
LINES.append(("[2026-05-21 09:12:04] AGENT  [SpecialistRouter]  -> running...", AMBER))
LINES.append(("[2026-05-21 09:12:04] AGENT  [QuestionCrafter]   -> running...", PURPLE))
LINES.append(("", WHITE))
LINES.append(("[2026-05-21 09:12:07] AGENT  [SpecialistRouter]  [OK] 3.1s |   412 tokens", AMBER))
LINES.append(("[2026-05-21 09:12:08] AGENT  [RedFlagDetector]   [OK] 4.2s |   587 tokens", ROSE))
LINES.append(("[2026-05-21 09:12:09] AGENT  [QuestionCrafter]   [OK] 5.4s |   794 tokens", PURPLE))
LINES.append(("[2026-05-21 09:12:11] AGENT  [DifferentialDx]    [OK] 7.1s | 1,624 tokens", BLUE))
LINES.append(("", WHITE))
LINES.append(("[2026-05-21 09:12:11] INFO   Phase 1 complete | 4 agents | 3,417 tokens", GREY))
LINES.append(("[2026-05-21 09:12:11] INFO   Phase 2: long-chain synthesizer starting...", GREY))
LINES.append(("[2026-05-21 09:12:11] AGENT  [Synthesizer] -> reasoning step 1: input scan", GREEN_OK))
LINES.append(("[2026-05-21 09:12:13] AGENT  [Synthesizer] -> reasoning step 2: weighing", GREEN_OK))
LINES.append(("[2026-05-21 09:12:15] AGENT  [Synthesizer] -> reasoning step 3: rule-out", GREEN_OK))
LINES.append(("[2026-05-21 09:12:18] AGENT  [Synthesizer] -> reasoning step 4: action", GREEN_OK))
LINES.append(("[2026-05-21 09:12:20] AGENT  [Synthesizer]      [OK] 9.3s | 2,118 tokens", GREEN_OK))
LINES.append(("", WHITE))
LINES.append(("=================================================================", DARK_GREY))
LINES.append(("  SUMMARY", WHITE))
LINES.append(("  Triage:        ROUTINE  (no red flags detected)", GREY))
LINES.append(("  Top diagnosis: Post-viral cough  (moderate likelihood)", GREY))
LINES.append(("  Specialist:    Pulmonology / GP  -  within 1 week", GREY))
LINES.append(("  Total tokens:  5,535", GREY))
LINES.append(("  Pipeline:      18.7s end-to-end", GREY))
LINES.append(("=================================================================", DARK_GREY))
LINES.append(("[2026-05-21 09:12:21] INFO   Session complete. Report streamed via SSE.", GREEN_OK))
LINES.append(("", WHITE))
LINES.append((f"{PROMPT_PREFIX} MINGW64 ~/projects/symptom-reason (main)", "PROMPT"))
LINES.append(("$ ", WHITE))

# --- layout ---
FONT_SIZE = 15
PAD_X = 18
PAD_Y = 14
LINE_H = 21
TITLE_H = 32
WIDTH = 940

# --- font fallback chain ---
mono = None
mono_bold = None
for path in [
    "C:/Windows/Fonts/CascadiaCode.ttf",
    "C:/Windows/Fonts/CascadiaMono.ttf",
    "C:/Windows/Fonts/consola.ttf",
    "C:/Windows/Fonts/cour.ttf",
]:
    if os.path.exists(path):
        mono = ImageFont.truetype(path, FONT_SIZE)
        break
for path in [
    "C:/Windows/Fonts/CascadiaCode-Bold.ttf",
    "C:/Windows/Fonts/consolab.ttf",
    "C:/Windows/Fonts/courbd.ttf",
]:
    if os.path.exists(path):
        mono_bold = ImageFont.truetype(path, FONT_SIZE)
        break
if mono is None:
    mono = ImageFont.load_default()
if mono_bold is None:
    mono_bold = mono

# Segoe UI for tab labels and Fluent glyphs
ui_font = None
ui_font_glyph = None
for path in ["C:/Windows/Fonts/segoeui.ttf"]:
    if os.path.exists(path):
        ui_font = ImageFont.truetype(path, 12)
        break
# MDL2 / Fluent assets for Windows controls
for path in [
    "C:/Windows/Fonts/SegMDL2.ttf",
    "C:/Windows/Fonts/SegoeIcons.ttf",
]:
    if os.path.exists(path):
        ui_font_glyph = ImageFont.truetype(path, 11)
        break
if ui_font is None:
    ui_font = mono
if ui_font_glyph is None:
    ui_font_glyph = ui_font

height = TITLE_H + PAD_Y * 2 + len(LINES) * LINE_H

img = Image.new("RGB", (WIDTH, height), BG)
draw = ImageDraw.Draw(img)

# --- Windows Terminal title bar ---
draw.rectangle([0, 0, WIDTH, TITLE_H], fill=TITLE_BAR)

# Active tab
TAB_W = 215
draw.rectangle([0, 0, TAB_W, TITLE_H], fill=ACTIVE_TAB)
draw.text((14, 8), "symptom-reason", fill=WHITE, font=ui_font)
# Tab close glyph (real ✕ from MDL2 = U+E711, fallback ✕ U+2715)
try:
    draw.text((TAB_W - 22, 9), "\uE711", fill=GREY, font=ui_font_glyph)
except Exception:
    draw.text((TAB_W - 18, 8), "\u2715", fill=GREY, font=ui_font)

# New-tab plus glyph (MDL2 U+E710) and dropdown chevron (U+E70D)
new_tab_x = TAB_W + 14
try:
    draw.text((new_tab_x, 9), "\uE710", fill=WHITE, font=ui_font_glyph)
    draw.text((new_tab_x + 30, 11), "\uE70D", fill=WHITE, font=ui_font_glyph)
except Exception:
    draw.text((new_tab_x, 8), "+", fill=WHITE, font=ui_font)
    draw.text((new_tab_x + 24, 8), "\u02C5", fill=WHITE, font=ui_font)

# Window controls right (MDL2: minimize U+E921, maximize U+E922, close U+E8BB)
ctrl_x = WIDTH - 138
try:
    for sym in ["\uE921", "\uE922", "\uE8BB"]:
        draw.text((ctrl_x, 9), sym, fill=WHITE, font=ui_font_glyph)
        ctrl_x += 46
except Exception:
    for sym in ["\u2014", "\u2610", "\u2715"]:
        draw.text((ctrl_x, 8), sym, fill=WHITE, font=ui_font)
        ctrl_x += 36

# Body
y = TITLE_H + PAD_Y
for text, color in LINES:
    if not text:
        y += LINE_H
        continue
    if color == "PROMPT":
        x = PAD_X
        # parse: user@host MINGW64 path (branch)
        try:
            user_host, rest = text.split(" MINGW64 ", 1)
            path_part, branch = rest.rsplit(" ", 1)
        except ValueError:
            user_host, path_part, branch = text, "", ""
        draw.text((x, y), user_host, fill=GREEN_PROMPT, font=mono_bold)
        x += draw.textlength(user_host, font=mono_bold)
        draw.text((x, y), " MINGW64 ", fill=WHITE, font=mono_bold)
        x += draw.textlength(" MINGW64 ", font=mono_bold)
        draw.text((x, y), path_part, fill=PROMPT_PATH, font=mono_bold)
        x += draw.textlength(path_part, font=mono_bold)
        draw.text((x, y), " " + branch, fill=PROMPT_BRANCH, font=mono_bold)
    else:
        draw.text((PAD_X, y), text, fill=color, font=mono)
    y += LINE_H

out = os.path.join(OUT_DIR, "symptom_reason_run.png")
img.save(out)
print(f"[OK] saved {out} ({os.path.getsize(out)} bytes, {WIDTH}x{height})")
