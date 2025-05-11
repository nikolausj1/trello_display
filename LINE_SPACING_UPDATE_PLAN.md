# Plan: Increase Line Spacing in Trello Display

**Objective:** Increase the vertical spacing between wrapped lines of text for items displayed by `trello_display.py`.

**Key File:** `projects/trello/trello_display.py`

**Core Idea:**
Introduce a "line spacing multiplier" to increase the gap between lines of text. This will affect:
1.  The `y` coordinate calculation when drawing each subsequent line of text.
2.  The total height calculation for the background rectangle of each card to ensure it accommodates the increased text height.

**Detailed Plan:**

1.  **Introduce a Line Spacing Multiplier:**
    *   Define a constant or a variable, for example, `LINE_SPACING_MULTIPLIER`.
    *   A value like `1.1` (for 10% extra space) or `1.2` (for 20% extra space) should provide "a little space." This can be tuned.
    *   This can be defined near your font settings or at the beginning of the `draw` function.

2.  **Modify Text Rendering in `draw()` function:**
    *   Locate the loop where individual lines (`ln`) of a card's text are rendered (currently around lines 126-129 in `trello_display.py`).
    *   The line `text_y += line_h` (line 129) advances the vertical position for the next line.
    *   **Change this to:** `text_y += line_h * LINE_SPACING_MULTIPLIER`. This will push subsequent lines further down.

3.  **Adjust Card Background Rectangle Height (`rect_h`) in `draw()` function:**
    *   The current calculation for `rect_h` is `line_h * len(lines) + 30` (line 117). This needs to account for the new spacing.
    *   A more accurate calculation for the total height of the text block, considering the multiplier, would be:
        *   If `len(lines) == 0`: `text_block_height = 0`
        *   If `len(lines) == 1`: `text_block_height = line_h`
        *   If `len(lines) > 1`: `text_block_height = (line_h * (len(lines) - 1) * LINE_SPACING_MULTIPLIER) + line_h`
            *   This formula considers `len(lines) - 1` gaps between lines, each with the new multiplied spacing, plus the height of the first line (which doesn't have spacing above it within the block).
    *   **The new `rect_h` will then be:** `rect_h = text_block_height + 30` (where `30` is your existing top/bottom padding of 15px each).

**Visual Plan (Simplified Flow for `draw` function changes):**

```mermaid
graph TD
    A[Start draw(tasks)] --> B{For each card};
    B --> C[Get card text & wrap into 'lines'];
    C --> D[line_h = font.get_height()];
    D --> E[Define LINE_SPACING_MULTIPLIER (e.g., 1.1)];
    E --> F{Calculate text_block_height with LINE_SPACING_MULTIPLIER};
    F -- If len(lines) > 1 --> G1[(line_h * (len(lines) - 1) * LINE_SPACING_MULTIPLIER) + line_h];
    F -- If len(lines) == 1 --> G2[line_h];
    F -- If len(lines) == 0 --> G3[0];
    G1 --> H[rect_h = text_block_height + 30];
    G2 --> H;
    G3 --> H;
    H --> I[Draw card background rectangle using new rect_h];
    I --> J[Initialize text_y for first line];
    J --> K{Loop through 'lines' to render text};
    K --> L[Render current line];
    L --> M[Update text_y: text_y += line_h * LINE_SPACING_MULTIPLIER];
    M --> K;
    K -- All lines rendered --> N[Update main y for next card];
    N --> B;
    B -- All cards drawn --> O[End draw function];