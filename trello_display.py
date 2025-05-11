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


# ---------- Trello helpers ------------------------------≠≠-------------------
def fetch_cards():
    """Return list of (card_id, card_name) tuples from the Trello list."""
    url = f"https://api.trello.com/1/lists/{LIST_ID}/cards"
    params = {"fields": "name,closed", "key": API_KEY, "token": API_TOKEN}
    try:
        data = requests.get(url, params=params, timeout=10).json()
        return [(c["id"], c["name"]) for c in data if not c.get("closed")]
    except Exception as e:
        return [("", f"Error: {e}")]

def archive_card(card_id):
    """Archive a card in Trello."""
    url = f"https://api.trello.com/1/cards/{card_id}"
    params = {"key": API_KEY, "token": API_TOKEN, "closed": "true"}
    try:
        response = requests.put(url, params=params, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error archiving card: {e}")
        return False

def unarchive_card(card_id):
    """Unarchive a card in Trello."""
    url = f"https://api.trello.com/1/cards/{card_id}"
    params = {"key": API_KEY, "token": API_TOKEN, "closed": "false"}
    try:
        response = requests.put(url, params=params, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error unarchiving card: {e}")
        return False

# ---------- Pygame initialisation ----------------------------------------
pygame.init()

info         = pygame.display.Info()            # picks current screen size
WIDTH        = info.current_w
HEIGHT       = info.current_h
screen       = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Trello Today")
pygame.mouse.set_visible(False)

# Attempt to load specified fonts, falling back to system default
FONT_SIZE = 26
FONT_CANDIDATES = ["Roboto Regular", "Roboto", "sans-serif", None]
# Define a dictionary for fonts
fonts = {}
for name in FONT_CANDIDATES:
    try:
        fonts['default'] = pygame.font.SysFont(name, FONT_SIZE)
        # print(f"Successfully loaded font: {name if name else 'System Default'} with size {FONT_SIZE}") # Optional: for debugging
        break  # Exit loop if font is successfully loaded
    except pygame.error:
        # print(f"Font '{name}' not found or failed to load, trying next...") # Optional: for debugging
        if name == FONT_CANDIDATES[-1] and 'default' not in fonts:  # Check if it's the last candidate and font is still None
            print(f"CRITICAL: Default font (None) also failed to load with size {FONT_SIZE}. Exiting.")
            pygame.quit()
            sys.exit() # Exit if all fonts fail

if 'default' not in fonts: # This case should ideally be handled by the sys.exit() in the loop
    print(f"CRITICAL: No suitable font could be loaded after trying all candidates: {FONT_CANDIDATES}. Exiting.")
    pygame.quit()
    sys.exit()

# Load other font sizes as needed by the new modal
try:
    fonts['modal_header'] = pygame.font.SysFont(FONT_CANDIDATES[0] if FONT_CANDIDATES[0] else "sans-serif", 28) # For "ITEM ARCHIVED"
    fonts['modal_button'] = pygame.font.SysFont(FONT_CANDIDATES[0] if FONT_CANDIDATES[0] else "sans-serif", 24) # For Undo/Dismiss buttons
except pygame.error as e:
    print(f"Error loading additional fonts: {e}. Using default.")
    if 'modal_header' not in fonts: fonts['modal_header'] = fonts['default']
    if 'modal_button' not in fonts: fonts['modal_button'] = fonts['default']


font = fonts['default'] # Keep 'font' for existing code compatibility

REFRESH_SECS = 120                              # Trello re-pull every 2 min
LINE_SPACING_MULTIPLIER = 1.2                 # Adjust for more/less space between wrapped lines
CARD_VERTICAL_PADDING_EACH_SIDE = 19          # Pixels of padding above and below text in a card

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
def draw_list_view(tasks, animating_card_id_to_exclude=None):
    # This function draws the list of Trello cards.
    # It excludes a specific card if its ID is provided in animating_card_id_to_exclude,
    # which is used when a card is being animated into/out of the modal.

    # Note: screen.fill() is handled by the main loop before calling this.
    # pygame.display.flip() is also handled by the main loop after all drawing.

    container_w = int(WIDTH * 0.90)              # Cards occupy 90% of screen width
    x_margin    = (WIDTH - container_w) // 2     # Centered horizontally
    y           = 15                             # Initial Y position for the first card
    spacing     = 12                             # Vertical space between cards
    inner_w     = container_w - 40               # Text area width inside a card (20px padding L/R)

    card_rects = []  # Stores (pygame.Rect, card_id, card_text) for click detection

    for card_id, text in tasks:
        if animating_card_id_to_exclude and card_id == animating_card_id_to_exclude:
            # If this card is being animated (e.g., into the modal), skip drawing it here.
            # It will be drawn separately as part of the animation.
            continue

        lines = wrap_text(text, fonts['default'], inner_w)
        line_h = fonts['default'].get_height()

        # Calculate the height of the text block within the card
        if not lines: # Handle cases with empty card text
            text_block_height = 0
        elif len(lines) == 1:
            text_block_height = line_h
        else:
            # Height of all text lines + height of (n-1) inter-line spaces
            text_block_height = (line_h * len(lines)) + \
                                (line_h * (LINE_SPACING_MULTIPLIER - 1) * (len(lines) - 1))
        
        # Total height of the card rectangle, including vertical padding
        rect_h = int(text_block_height + (CARD_VERTICAL_PADDING_EACH_SIDE * 2))

        # Create the rectangle for the current card
        rect = pygame.Rect(x_margin, y, container_w, rect_h)
        pygame.draw.rect(screen, (22, 26, 30), rect, border_radius=10) # Dark card background

        # Store the card's rectangle, ID, and text for later click detection
        card_rects.append((rect, card_id, text))

        # Draw the text lines onto the card
        text_y_start = y + CARD_VERTICAL_PADDING_EACH_SIDE # Y position for the first line of text
        current_text_y = text_y_start
        for ln_text in lines:
            text_surface = fonts['default'].render(ln_text, True, (255, 255, 255)) # White text
            screen.blit(text_surface, (x_margin + 20, current_text_y)) # 20px left padding for text
            current_text_y += line_h * LINE_SPACING_MULTIPLIER # Move to next line position

        y += rect_h + spacing # Advance Y position for the next card

    return card_rects

# def show_undo_modal(card_id, card_text): # This function is now obsolete
#     """Show a centered modal with an undo option after archiving a task."""
#     # Create semi-transparent overlay for the entire screen
#     overlay_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
#     overlay_surface.fill((0, 0, 0, 180))  # Darker semi-transparent black
#
#     # Modal properties
#     modal_width = int(WIDTH * 0.7) # 70% of screen width
#     modal_height = int(HEIGHT * 0.4) # 40% of screen height, or fixed e.g. 150
#     if modal_height < 150: modal_height = 150 # Ensure minimum height
#     if modal_width < 280: modal_width = 280 # Ensure minimum width
#
#     modal_x = (WIDTH - modal_width) // 2
#     modal_y = (HEIGHT - modal_height) // 2
#
#     modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
#     pygame.draw.rect(overlay_surface, (50, 50, 50), modal_rect, border_radius=15) # Dark gray modal
#
#     # Text: "Archived: [Full Card Text]"
#     # Wrap text if it's too long for the modal width
#     title_font = pygame.font.SysFont(None, 28) # Slightly larger font
#     archived_label_text = "Archived:"
#     archived_label_surf = title_font.render(archived_label_text, True, (220, 220, 220))
#
#     card_display_font = pygame.font.SysFont(None, 24)
#     # Max width for card text is modal_width minus padding
#     card_text_lines = wrap_text(card_text, card_display_font, modal_width - 40) # 20px padding each side
#
#     # UNDO Button
#     button_width = 150
#     button_height = 50
#     undo_button_x = modal_x + (modal_width - button_width) // 2 # Centered
#     undo_button_y = modal_y + modal_height - button_height - 20 # 20px from bottom
#     undo_button_rect = pygame.Rect(undo_button_x, undo_button_y, button_width, button_height)
#
#     pygame.draw.rect(overlay_surface, (60, 100, 180), undo_button_rect, border_radius=10) # Blueish button
#
#     undo_font = pygame.font.SysFont(None, 32)
#     undo_text_surf = undo_font.render("UNDO", True, (240, 240, 240))
#
#     # Blit overlay with modal elements to the screen
#     screen.blit(overlay_surface, (0,0))
#
#     # Blit "Archived:" label
#     screen.blit(archived_label_surf, (modal_x + 20, modal_y + 20))
#
#     # Blit wrapped card text
#     current_text_y = modal_y + 20 + archived_label_surf.get_height() + 10 # Start below "Archived:"
#     for line_surf_text in card_text_lines:
#         if current_text_y + card_display_font.get_height() > undo_button_y - 10: # Check if text overflows
#             # Optionally add "..." or handle overflow
#             break
#         line_surf = card_display_font.render(line_surf_text, True, (210, 210, 210))
#         screen.blit(line_surf, (modal_x + 20, current_text_y))
#         current_text_y += card_display_font.get_height()
#
#     # Blit UNDO text onto its button
#     screen.blit(undo_text_surf,
#                 (undo_button_rect.x + (undo_button_rect.width - undo_text_surf.get_width()) // 2,
#                  undo_button_rect.y + (undo_button_rect.height - undo_text_surf.get_height()) // 2))
#
#     pygame.display.flip()
#
#     # Return the clickable rect for the UNDO button, card_id, and card_text
#     # Note: The undo_button_rect is relative to the overlay, but mouse pos is absolute.
#     # For collision detection, we use the absolute coordinates.
#     return undo_button_rect, card_id, card_text

# ---------- New Enhanced Undo Modal Drawing Function -------------------------
def draw_enhanced_undo_modal(screen, fonts, modal_y_pos, animating_card_surface, card_current_pos_on_screen, dismiss_progress): # Corrected parameter name
    """Draws the enhanced undo modal with animations and new buttons."""
    # Skrim
    skrim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    skrim_surface.fill((0, 0, 0, 180))  # Semi-transparent black
    screen.blit(skrim_surface, (0, 0))

    # Modal properties
    modal_width = WIDTH # Modal spans 100% of screen width
    modal_height = int(HEIGHT * 0.40) # Adjusted for taller buttons
    if modal_height < 280: modal_height = 280 # Min height increased for stacked buttons
    
    modal_x = 0 # Modal starts at the left edge of the screen
    # modal_y_pos is passed in for animation

    modal_bg_color = (30, 30, 30) # Dark grey, similar to task cards
    modal_rect = pygame.Rect(modal_x, modal_y_pos, modal_width, modal_height)
    pygame.draw.rect(screen, modal_bg_color, modal_rect, border_radius=15)

    # Header: "ITEM ARCHIVED"
    header_text_surf = fonts['modal_header'].render("ITEM ARCHIVED", True, (220, 220, 220))
    header_text_rect = header_text_surf.get_rect(centerx=modal_rect.centerx, top=modal_y_pos + 20)
    screen.blit(header_text_surf, header_text_rect)

    # Animated Task Card (blit the pre-rendered surface at its current animated position)
    if animating_card_surface and card_current_pos_on_screen:
        screen.blit(animating_card_surface, card_current_pos_on_screen)

    # Buttons properties
    button_height = 50
    button_spacing = 10 # Vertical space between stacked buttons
    stacked_button_width = modal_width - 40 # Buttons span modal width with 20px padding each side
    
    # Dismiss Button (Grey, with timer) - Top button
    dismiss_button_color = (70, 70, 70) # Darker Grey
    dismiss_button_y = modal_y_pos + modal_height - (2 * button_height) - button_spacing - 20 # Positioned above Undo
    dismiss_button_rect = pygame.Rect(
        modal_x + 20, # Centered with padding
        dismiss_button_y,
        stacked_button_width,
        button_height
    )
    pygame.draw.rect(screen, dismiss_button_color, dismiss_button_rect, border_radius=10)

    # Dismiss Timer Visual (Light grey overlay on Dismiss button) - DRAWN BEFORE TEXT
    timer_overlay_color = (120, 120, 120) # Light grey
    timer_width = int(stacked_button_width * (1.0 - dismiss_progress)) # Use stacked_button_width
    if timer_width > 0: # Only draw if there's progress left
        timer_overlay_rect = pygame.Rect(
            dismiss_button_rect.left + (stacked_button_width - timer_width), # Anchored to the right
            dismiss_button_rect.top,
            timer_width,
            dismiss_button_rect.height
        )
        # Draw the timer overlay carefully to respect the main button's border radius
        pygame.draw.rect(screen, timer_overlay_color, timer_overlay_rect, border_radius=10)

    # Dismiss Text - DRAWN AFTER TIMER OVERLAY
    dismiss_text_surf = fonts['modal_button'].render("Dismiss", True, (200, 200, 200))
    dismiss_text_rect = dismiss_text_surf.get_rect(center=dismiss_button_rect.center)
    screen.blit(dismiss_text_surf, dismiss_text_rect)


    # Undo Button (Blue) - Bottom button
    undo_button_color = (0, 122, 255) # Blue
    undo_button_y = dismiss_button_rect.bottom + button_spacing # Positioned below Dismiss
    undo_button_rect = pygame.Rect(
        modal_x + 20, # Centered with padding
        undo_button_y,
        stacked_button_width,
        button_height
    )
    pygame.draw.rect(screen, undo_button_color, undo_button_rect, border_radius=10)
    undo_text_surf = fonts['modal_button'].render("Undo", True, (255, 255, 255))
    undo_text_rect = undo_text_surf.get_rect(center=undo_button_rect.center)
    screen.blit(undo_text_surf, undo_text_rect)
    
    # pygame.display.flip() # Flip is handled once at the end of the main loop
    return {'undo_button': undo_button_rect, 'dismiss_button': dismiss_button_rect}


# ---------- main loop -----------------------------------------------------
tasks      = fetch_cards()
last_fetch = time.time()
card_rects = []  # Initialize card_rects

# Old undo variables - to be removed or integrated
# undo_active = False
# undo_modal_button_rect = None
# undo_card_id = None
# undo_card_text = None
# undo_card_original_index = -1
# undo_start_time = 0

# New state management variables from the plan
APP_STATE_LIST_VIEW = 'LIST_VIEW'
APP_STATE_MODAL_ANIMATING_IN = 'MODAL_ANIMATING_IN'
APP_STATE_MODAL_ACTIVE = 'MODAL_ACTIVE'
APP_STATE_MODAL_ANIMATING_OUT = 'MODAL_ANIMATING_OUT'

app_state = APP_STATE_LIST_VIEW

animating_card_details = {
    'id': None,
    'text': None,
    'original_rect': None,
    'rendered_surface': None, # This will store the pygame.Surface of the card
    'original_list_index': -1,
    'current_pos': None, # For animation: (x,y)
    'target_pos_in_modal': None # For animation: (x,y) relative to screen
}

modal_anim_start_time = 0.0
modal_current_y = HEIGHT # Start off-screen
modal_target_y = HEIGHT - int(HEIGHT * 0.35) - 20 # Target Y position for modal (20px from bottom)
if modal_target_y + int(HEIGHT * 0.35) > HEIGHT -20: # ensure it's on screen
    modal_target_y = HEIGHT - int(HEIGHT * 0.35) - 20


modal_dismiss_timer_start_time = 0.0
UNDO_TIMEOUT = 5  # Seconds for the new modal timeout
ANIMATION_DURATION = 0.3  # Seconds for modal slide and card animation

# Ensure modal_target_y calculation for modal_height is consistent
_modal_height_for_target_y = int(HEIGHT * 0.40) # Adjusted for taller buttons
if _modal_height_for_target_y < 280: _modal_height_for_target_y = 280 # Min height increased
modal_target_y = HEIGHT - _modal_height_for_target_y - 20 # Final position from bottom


clock = pygame.time.Clock()
active_modal_buttons = {} # To store clickable rects for modal buttons

while True:
    dt = clock.tick(60) / 1000.0 # Delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if app_state == APP_STATE_LIST_VIEW:
                for i, (rect, card_id_clicked, card_text_clicked) in enumerate(card_rects):
                    if rect.collidepoint(pos) and card_id_clicked:
                        # --- Initiate Modal ---
                        app_state = APP_STATE_MODAL_ANIMATING_IN
                        
                        animating_card_details['id'] = card_id_clicked
                        animating_card_details['text'] = card_text_clicked
                        animating_card_details['original_rect'] = rect.copy()
                        animating_card_details['original_list_index'] = i
                        
                        # Create a surface for the card to animate
                        # This assumes card content is drawn simply without complex overlaps
                        animating_card_details['rendered_surface'] = screen.subsurface(rect).copy()
                        
                        animating_card_details['current_pos'] = rect.topleft
                        
                        # Calculate target position for the card within the modal
                        # The card should be centered horizontally within the modal, and placed below the header.
                        # _modal_w is now effectively WIDTH, and _modal_x_abs is 0
                        
                        header_height_approx = fonts['modal_header'].get_height() + 20 # header text + padding above
                        card_y_offset_in_modal = 20 + header_height_approx + 10 # top_padding + header_h + padding_below_header
                        
                        # Card is centered on the screen, as modal is full width
                        _card_target_x_on_screen = (WIDTH - rect.width) // 2
                        _card_target_y_on_screen = modal_target_y + card_y_offset_in_modal
                        
                        animating_card_details['target_pos_in_modal'] = (_card_target_x_on_screen, _card_target_y_on_screen)

                        modal_anim_start_time = time.time()
                        modal_current_y = HEIGHT # Start modal off-screen

                        # Remove the card from the main tasks list as it's now being handled by the modal.
                        # Storing its original index allows for correct re-insertion if "Undo" is chosen.
                        tasks.pop(animating_card_details['original_list_index'])
                        break
            elif app_state == APP_STATE_MODAL_ACTIVE:
                if active_modal_buttons.get('undo_button') and active_modal_buttons['undo_button'].collidepoint(pos):
                    if unarchive_card(animating_card_details['id']):
                        # Restore card to its original position
                        if 0 <= animating_card_details['original_list_index'] <= len(tasks):
                            tasks.insert(animating_card_details['original_list_index'], (animating_card_details['id'], animating_card_details['text']))
                        else: # Fallback
                            tasks.append((animating_card_details['id'], animating_card_details['text']))
                    # Regardless of API success for now, proceed to animate out
                    app_state = APP_STATE_MODAL_ANIMATING_OUT
                    modal_anim_start_time = time.time() # Reset timer for out-animation
                elif active_modal_buttons.get('dismiss_button') and active_modal_buttons['dismiss_button'].collidepoint(pos):
                    archive_card(animating_card_details['id']) # API call
                    # Card is already visually removed from list, tasks list reflects this if pop was used
                    # Or if we filter, it's fine.
                    app_state = APP_STATE_MODAL_ANIMATING_OUT
                    modal_anim_start_time = time.time()

    # --- State Logic & Drawing ---
    screen.fill((0, 0, 0)) # Clear screen at the beginning of each frame

    if app_state == APP_STATE_LIST_VIEW:
        if time.time() - last_fetch > REFRESH_SECS:
            tasks = fetch_cards() # ToDo: consider if animating_card_id should be preserved if fetch happens during animation
            last_fetch = time.time()
        card_rects = draw_list_view(tasks, None) # Pass None as no card is currently animating

    elif app_state == APP_STATE_MODAL_ANIMATING_IN:
        elapsed_anim_time = time.time() - modal_anim_start_time
        anim_progress = min(elapsed_anim_time / ANIMATION_DURATION, 1.0)

        # Modal slide animation (ease-out can be added later)
        modal_current_y = HEIGHT - ((HEIGHT - modal_target_y) * anim_progress)

        # Card position animation
        start_x, start_y = animating_card_details['original_rect'].topleft
        target_x, target_y = animating_card_details['target_pos_in_modal']
        
        current_card_x = start_x + (target_x - start_x) * anim_progress
        current_card_y = start_y + (target_y - start_y) * anim_progress
        animating_card_details['current_pos'] = (current_card_x, current_card_y)

        # Draw background tasks (excluding the one being animated)
        draw_list_view(tasks, animating_card_details['id'])
        
        # Draw the modal and the animating card
        active_modal_buttons = draw_enhanced_undo_modal(
            screen, fonts,
            modal_current_y,
            animating_card_details['rendered_surface'],
            animating_card_details['current_pos'],
            0.0 # No dismiss progress during intro animation
        )

        if anim_progress == 1.0:
            app_state = APP_STATE_MODAL_ACTIVE
            modal_dismiss_timer_start_time = time.time()
            # The card is now at its 'target_pos_in_modal'
            animating_card_details['current_pos'] = animating_card_details['target_pos_in_modal']


    elif app_state == APP_STATE_MODAL_ACTIVE:
        # Logic for active modal (timer, button clicks) will be here
        # For now, just draw it statically after animation
        draw_list_view(tasks, animating_card_details['id']) # Draw background
        
        elapsed_dismiss_time = time.time() - modal_dismiss_timer_start_time
        current_dismiss_progress = min(elapsed_dismiss_time / UNDO_TIMEOUT, 1.0)

        active_modal_buttons = draw_enhanced_undo_modal(
            screen, fonts,
            modal_target_y, # Modal is at its final Y position
            animating_card_details['rendered_surface'],
            animating_card_details['current_pos'], # Card is at its final position in modal
            current_dismiss_progress
        )
        
        if current_dismiss_progress == 1.0: # Timeout
            archive_card(animating_card_details['id'])
            app_state = APP_STATE_MODAL_ANIMATING_OUT
            modal_anim_start_time = time.time()

    elif app_state == APP_STATE_MODAL_ANIMATING_OUT:
        elapsed_anim_time = time.time() - modal_anim_start_time
        anim_progress = min(elapsed_anim_time / ANIMATION_DURATION, 1.0)

        # Modal slide out animation (reversing the in-animation)
        modal_current_y = modal_target_y + ((HEIGHT - modal_target_y) * anim_progress)
        
        # Card also moves with the modal (its position relative to modal top remains same)
        # We need to calculate its on-screen position based on modal_current_y
        _card_target_x_on_screen, _card_target_y_in_modal_final = animating_card_details['target_pos_in_modal']
        _offset_y_card_from_modal_top = _card_target_y_in_modal_final - modal_target_y
        current_card_y_on_screen = modal_current_y + _offset_y_card_from_modal_top
        
        animating_card_details['current_pos'] = (_card_target_x_on_screen, current_card_y_on_screen)

        # Draw background tasks
        # If card was unarchived, it's back in 'tasks'. If archived, it's not.
        # draw_list_view will handle not drawing it if its ID matches animating_card_details['id']
        # but for animating out, we usually don't want to see it in the background list yet.
        # The list should only update visually *after* the modal is gone.
        # So, draw the list as it was when the modal became active.
        # For simplicity now, just draw current tasks, filtering out the animated card.
        draw_list_view(tasks, animating_card_details['id'])

        active_modal_buttons = draw_enhanced_undo_modal(
            screen, fonts,
            modal_current_y,
            animating_card_details['rendered_surface'],
            animating_card_details['current_pos'],
            1.0 # Dismiss progress is full as it's disappearing
        )

        if anim_progress == 1.0:
            app_state = APP_STATE_LIST_VIEW
            # Reset animating_card_details
            animating_card_details = {
                'id': None, 'text': None, 'original_rect': None,
                'rendered_surface': None, 'original_list_index': -1,
                'current_pos': None, 'target_pos_in_modal': None
            }
            card_rects = draw_list_view(tasks, None) # Force redraw of list in its new state
            active_modal_buttons = {}


    pygame.display.flip() # Single flip at the end of the main loop
