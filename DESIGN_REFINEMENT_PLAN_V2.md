# Trello Display - Design Refinement Plan (Revised)

**Date:** 2025-10-05

**Objective:** To refine the visual design of the Pygame Trello display (`trello_display.py`) to precisely match the user-provided image and specifications, focusing on card size, font, spacing, and colors.

## User-Provided Specifications:
*   **Font:** Roboto Regular (if available on the system)
*   **Card Color:** `#161A1E` (RGB: `(22, 26, 30)`)
*   **Background Color:** `#000000` (RGB: `(0, 0, 0)`)

## Proposed Changes to `trello_display.py`

The following changes are proposed to address the identified discrepancies and incorporate user specifications:

**1. Color Adjustments:**

*   **Screen Background Color:**
    *   **Current (line 85):** `(0, 0, 0)`
    *   **Proposed:** `(0, 0, 0)` (Pure Black, as specified by user)
    *   **File & Line:** `trello_display.py`, around line 85.
*   **Card Background Color:**
    *   **Current (line 101):** `(25, 25, 25)`
    *   **Proposed:** `(22, 26, 30)` (Corresponds to `#161A1E`, as specified by user)
    *   **File & Line:** `trello_display.py`, around line 101.
*   **Text Color:**
    *   **Current (line 108):** `(255, 255, 255)` (Pure White)
    *   **Proposed:** No change. White text is consistent with the image and user feedback.

**2. Font Adjustments:**

*   **Font Family & Size (line 66):**
    *   **Current:** `pygame.font.SysFont(None, 28)`
    *   **Proposed Size:** `34` (To make text more prominent and visually closer to the image)
    *   **Proposed Family Search Order:**
        1.  `pygame.font.SysFont("Roboto Regular", 34)`
        2.  `pygame.font.SysFont("Roboto", 34)`
        3.  `pygame.font.SysFont("sans-serif", 34)` (Fallback if Roboto is not found)
        4.  `pygame.font.SysFont(None, 34)` (System default sans-serif as final fallback)
    *   **Reasoning:** To attempt using the user-specified "Roboto Regular" font. If not available, fall back gracefully. The increased size should improve resemblance to the design image.
    *   **File & Line:** `trello_display.py`, around line 66.

**3. Sizing and Spacing Adjustments:**

*   **Container Width (Card Width relative to Screen - line 87):**
    *   **Current:** `container_w = int(WIDTH * 0.94)`
    *   **Proposed:** `container_w = int(WIDTH * 0.90)`
    *   **Reasoning:** To increase the side margins of the list container.
    *   **File & Line:** `trello_display.py`, around line 87.
*   **Spacing Between Cards (line 90):**
    *   **Current:** `spacing = 8`
    *   **Proposed:** `spacing = 12`
    *   **Reasoning:** To provide slightly more visual separation between cards.
    *   **File & Line:** `trello_display.py`, around line 90.
*   **Internal Card Padding (Left/Right - affecting lines 91 & 109):**
    *   **Current:** 15px each side.
    *   **Proposed:** 20px each side.
        *   Change line 91 to: `inner_w = container_w - 40`
        *   Change line 109 blit offset to: `x_margin + 20`
    *   **Reasoning:** The image suggests generous horizontal padding.
    *   **File & Line:** `trello_display.py`, around lines 91 and 109.
*   **Internal Card Padding (Top/Bottom - affecting lines 98 & 106):**
    *   **Current:** 12px top/bottom.
    *   **Proposed:** 15px top/bottom.
        *   Change line 98 to: `rect_h = line_h * len(lines) + 30`
        *   Change line 106 to: `text_y = y + 15`
    *   **Reasoning:** To increase vertical padding within cards.
    *   **File & Line:** `trello_display.py`, around lines 98 and 106.
*   **Card Border Radius (line 101):**
    *   **Current:** `border_radius=12`
    *   **Proposed:** `border_radius=10`
    *   **Reasoning:** The corners in the image appear slightly less rounded.
    *   **File & Line:** `trello_display.py`, around line 101.

## Visual Summary of Proposed Changes (Mermaid Diagram)

```mermaid
graph TD
    A[Current App State] --> B{Refine Design to Match Image & User Specs};

    B --> Colors;
    Colors --> C1[Screen BG: Current (0,0,0)];
    C1 --> D1[Change to: (0,0,0) User Spec];
    Colors --> C2[Card BG: Current (25,25,25)];
    C2 --> D2[Change to: (22,26,30) User Spec #161A1E];

    B --> Font;
    Font --> F1[Font Size: 28];
    F1 --> G1[Change to: 34];
    Font --> F2[Font Family: SysFont(None)];
    F2 --> G2[Attempt: "Roboto Regular", "Roboto", then "sans-serif"];

    B --> SizingAndSpacing[Sizing & Spacing];
    SizingAndSpacing --> S1[Container Width: 94% Screen];
    S1 --> T1[Change to: 90% Screen];
    SizingAndSpacing --> S2[Spacing Between Cards: 8px];
    S2 --> T2[Change to: 12px];
    SizingAndSpacing --> S3[Card H-Padding: 15px each side];
    S3 --> T3[Change to: 20px each side];
    SizingAndSpacing --> S4[Card V-Padding: 12px each side];
    S4 --> T4[Change to: 15px each side];
    SizingAndSpacing --> S5[Border Radius: 12px];
    S5 --> T5[Change to: 10px];
```

## Next Steps
1.  Review and approve this revised plan.
2.  If approved, write this plan to `projects/trello/DESIGN_REFINEMENT_PLAN_V2.md`.
3.  Switch to "Code" mode to implement the changes in `trello_display.py`.
4.  Test and compare against the design image.
5.  Further iterate if necessary.