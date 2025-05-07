#!/usr/bin/env python3
# ------------------------------------------------------------
#  Trello “Today” list display — auto-sizing version
#  • Works in landscape (480×320) or portrait (320×480)
#  • Full-screen, mouse cursor hidden
#  • Each card appears in a dark rounded rectangle that
#    grows vertically if text wraps to multiple lines.
# ------------------------------------------------------------
import pygame, requests, time, sys

# add to top (after imports)
from pathlib import Path
from dotenv import load_dotenv    # pip install python-dotenv
import os

load_dotenv(Path(__file__).with_name("trello_secrets.env"))

API_KEY   = os.environ.get("API_KEY")
API_TOKEN = os.environ.get("API_TOKEN")
LIST_ID   = os.environ.get("LIST_ID")


# ---------- Trello helper ------------------------------≠≠-------------------
def fetch_cards():
    """Return list of (card_id, card_name) tuples from the Trello list."""
    url = f"https://api.trello.com/1/lists/{LIST_ID}/cards"
    params = {"fields": "name,closed", "key": API_KEY, "token": API_TOKEN}
    try:
        data = requests.get(url, params=params, timeout=10).json()
        return [(c["id"], c["name"]) for c in data if not c.get("closed")]
    except Exception as e:
        return [("", f"Error: {e}")]

# ---------- Pygame initialisation ----------------------------------------
pygame.init()

info         = pygame.display.Info()            # picks current screen size
WIDTH        = info.current_w
HEIGHT       = info.current_h
screen       = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Trello Today")
pygame.mouse.set_visible(False)

font         = pygame.font.SysFont(None, 28)    # default system font, 28 pt
REFRESH_SECS = 120                              # Trello re-pull every 2 min

# ---------- word-wrap helper ---------------------------------------------
def wrap_text(text, font, max_width):
    """Return list of text lines that fit within max_width pixels."""
    words, lines, current = text.split(), [], ""
    for w in words:
        test = (current + " " + w).strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = w
    lines.append(current)
    return lines

# ---------- drawing -------------------------------------------------------
def draw(tasks):
    screen.fill((0, 0, 0))                       # pure black bg

    container_w = int(WIDTH * 0.94)              # 94 % of current width
    x_margin    = (WIDTH - container_w) // 2
    y           = 15
    spacing     = 10
    inner_w     = container_w - 30               # left/right padding 15 px

    for _card_id, text in tasks:
        lines   = wrap_text(text, font, inner_w)
        line_h  = font.get_height()
        rect_h  = line_h * len(lines) + 20       # 10 px top/bottom padding

        rect = pygame.Rect(x_margin, y, container_w, rect_h)
        pygame.draw.rect(screen, (40, 40, 40), rect, border_radius=12)

        text_y = y + 10
        for ln in lines:
            surf = font.render(ln, True, (240, 240, 240))
            screen.blit(surf, (x_margin + 15, text_y))
            text_y += line_h

        y += rect_h + spacing

    pygame.display.flip()

# ---------- main loop -----------------------------------------------------
tasks      = fetch_cards()
last_fetch = time.time()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()

    # Periodically re-pull Trello list
    if time.time() - last_fetch > REFRESH_SECS:
        tasks       = fetch_cards()
        last_fetch  = time.time()

    draw(tasks)
    time.sleep(0.1)        # ~10 fps — enough for static content
