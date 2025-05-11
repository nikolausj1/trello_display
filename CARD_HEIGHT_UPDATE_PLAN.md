# Plan: Increase Card Height via Vertical Padding

**Objective:** Increase the overall height of the item cards in `trello_display.py` by adding more vertical padding above and below the text within each card.

**Key File:** `projects/trello/trello_display.py`

**Chosen Padding Value:** `CARD_VERTICAL_PADDING_EACH_SIDE = 25` (resulting in 25px top padding and 25px bottom padding, for a total of 50px vertical padding per card).

**Core Idea:**
Introduce a configurable constant for the amount of padding on each side (top and bottom) within the card. This constant will then be used to calculate the total height of the card rectangle and the starting `y` position of the text.

**Detailed Plan:**

1.  **Define a Vertical Padding Constant:**
    *   Introduce a new constant: `CARD_VERTICAL_PADDING_EACH_SIDE = 25`.
    *   This constant will be defined near other display-related constants in `trello_display.py`.

2.  **Modify `draw()` function:**
    *   **Update `rect_h` (card rectangle height) calculation:**
        *   The current calculation adds a fixed `30` for padding. This will be replaced.
        *   The new line will be: `rect_h = int(text_block_height + (CARD_VERTICAL_PADDING_EACH_SIDE * 2))`.
    *   **Update initial `text_y` (text starting vertical position) calculation:**
        *   The current calculation for the first line of text within a card uses a hardcoded `15` for top padding.
        *   This will be changed to: `text_y = y + CARD_VERTICAL_PADDING_EACH_SIDE`.

**Visual Plan (Simplified Flow for `draw` function changes):**

```mermaid
graph TD
    A[Start draw(tasks)] --> B(Define CARD_VERTICAL_PADDING_EACH_SIDE = 25);
    B --> C{For each card};
    C --> D[Calculate text_block_height (using LINE_SPACING_MULTIPLIER as before)];
    D --> E[rect_h = int(text_block_height + (CARD_VERTICAL_PADDING_EACH_SIDE * 2))];
    E --> F[Draw card background rectangle using new rect_h];
    F --> G[text_y = y + CARD_VERTICAL_PADDING_EACH_SIDE];
    G --> H{Loop through 'lines' to render text};
    H --> I[Render current line];
    I --> J[Update text_y using line_h * LINE_SPACING_MULTIPLIER];
    J --> H;
    H -- All lines rendered --> K[Update main y for next card: y += rect_h + spacing];
    K --> C;
    C -- All cards drawn --> L[pygame.display.flip()];
    L --> M[End draw function];