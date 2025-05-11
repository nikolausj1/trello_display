# Trello Display - Design Update Plan

**Date:** 2025-10-05

**Objective:** To update the visual design of the Pygame Trello display (`trello_display.py`) to closely match the user-provided image. The image shows a dark-themed list with rounded rectangular items, white text, and appropriate spacing.

## Analysis of Current `trello_display.py` Settings (Pre-Change)

*   **Background Color:** `(0, 0, 0)` (Pure Black) - Line 85
*   **Card Color:** `(40, 40, 40)` (Dark Gray) - Line 101
*   **Card Border Radius:** `12` pixels - Line 101
*   **Text Color:** `(240, 240, 240)` (Very Light Gray / Off-White) - Line 108
*   **Font:** Default system font, size 28 (`pygame.font.SysFont(None, 28)`) - Line 66
*   **Internal Card Padding (Top/Bottom):** 10 pixels each (total 20px, from `rect_h = line_h * len(lines) + 20`) - Line 98
*   **Internal Card Padding (Left/Right):** 15 pixels each (from `inner_w = container_w - 30` and text blit `x_margin + 15`) - Lines 91, 109
*   **Spacing Between Cards:** `10` pixels (`spacing = 10`) - Line 90

## Proposed Changes to `trello_display.py`

To align with the visual style of the provided image, the following modifications are planned:

1.  **Card Background Color:**
    *   **Current:** `(40, 40, 40)`
    *   **Proposed:** `(25, 25, 25)` (Darker gray, closer to image)
    *   **File & Line:** `trello_display.py`, around line 101.

2.  **Text Color:**
    *   **Current:** `(240, 240, 240)`
    *   **Proposed:** `(255, 255, 255)` (Pure White)
    *   **File & Line:** `trello_display.py`, around line 108.

3.  **Spacing Between Cards:**
    *   **Current:** `spacing = 10`
    *   **Proposed:** `spacing = 8` (Slightly tighter)
    *   **File & Line:** `trello_display.py`, around line 90.

4.  **Internal Card Padding (Top/Bottom):**
    *   **Current:** Total 20 pixels (10px top, 10px bottom via `... + 20`)
    *   **Proposed:** Total 24 pixels (12px top, 12px bottom via `... + 24`)
    *   **File & Line:** `trello_display.py`, around line 98 (modify the `+ 20` part).

5.  **Internal Card Padding (Left/Right):**
    *   **Current:** 15 pixels each side.
    *   **Proposed:** No change. Looks appropriate.

6.  **Card Border Radius:**
    *   **Current:** `border_radius=12`.
    *   **Proposed:** No change. Matches image.

7.  **Font Style and Size:**
    *   **Current:** `pygame.font.SysFont(None, 28)`.
    *   **Proposed:** No change for now. Revisit if other changes are insufficient.

## Visual Summary of Changes (Mermaid Diagram)

```mermaid
graph TD
    A[Current Design Settings] --> B{Match Image Design};

    B --> C1[Card Color: (40,40,40)];
    C1 --> D1[Change to: (25,25,25)];

    B --> C2[Text Color: (240,240,240)];
    C2 --> D2[Change to: (255,255,255)];

    B --> C3[Spacing Between Cards: 10px];
    C3 --> D3[Change to: 8px];

    B --> C4[Card V-Padding: 10px top/bottom (total 20px)];
    C4 --> D4[Change to: 12px top/bottom (total 24px)];

    B --> C5[Card H-Padding: 15px left/right];
    C5 --> D5[No Change];

    B --> C6[Border Radius: 12px];
    C6 --> D6[No Change];

    B --> C7[Font: SysFont, 28pt];
    C7 --> D7[No Change (Revisit if needed)];