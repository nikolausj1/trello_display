# Trello Display Project Log

This file tracks important project details, changes, and decisions for reference in future conversations.

## Project Overview

- **Repository**: https://github.com/nikolausj1/trello_display.git
- **Description**: A Python application that displays Trello cards from a specific list on a screen
- **Primary Use Case**: Keeping track of tasks on a dedicated display (e.g., Raspberry Pi)

## Key Components

- **trello_display.py**: Main Python script that fetches and displays Trello cards
- **trello_secrets.env**: Contains API credentials (not tracked in Git)
- **.config/autostart/trello-display.desktop**: User-specific autostart configuration

## Feature Timeline

### 2025-05-06
- Added comprehensive documentation to README.md

### 2025-06-05
- Implemented autostart functionality for Raspberry Pi/Linux
- Updated README.md with autostart setup instructions
- Created this project log file

## Setup Notes

### Autostart Configuration
- Location: `~/.config/autostart/trello-display.desktop`
- Purpose: Starts the application automatically on system boot
- Implementation: Standard Linux desktop entry file
- Status: Tested and working on Raspberry Pi

## Future Considerations

- Consider creating an installation script to automate setup (including autostart configuration)
- Potential enhancements to display formatting or card visualization
- Consider adding more interactive features like card editing or creation


### 2025-09-05
- Added interactive task archiving functionality
  - Users can now tap on a task to bring up an archive confirmation dialog
  - Tasks can be archived directly from the display with confirmation
  - The display refreshes immediately after archiving to show the updated list
- Fixed issue with the "No" button in the confirmation dialog
  - Ensured the screen redraws properly when canceling the archive action
  - Improved user experience by making both "Yes" and "No" buttons work correctly
- Enhanced archive confirmation dialog
  - The dialog now shows which item is being archived in the title
  - Added an "Undo" option that appears after archiving an item
  - Undo notification automatically disappears after 5 seconds if not used

### 2025-10-05
- Improved undo functionality
  - Increased undo button size from 80×30 to 150×50 pixels for better visibility and easier touch interaction
  - Enhanced undo button text with larger font size (32pt) and uppercase styling
  - Extended undo notification timeout from 5 to 15 seconds, giving users more time to decide whether to undo an action
- Enhanced archive confirmation dialog
  - Improved Yes/No buttons with larger size (110×40 pixels) and more rounded corners
  - Used more vibrant colors for better visibility and visual appeal
  - Enhanced button text with larger font size (28pt) and uppercase styling for better readability


## UX Improvement Plan for Unarchiving Cards (2025-10-05)

**Objective:** Refine the user experience for un-archiving cards to be more intuitive and responsive, and to better accommodate physical interaction constraints.

**Core Changes:**

1.  **Immediate Archive on Click:**
    *   When a card is clicked, the "Are you sure?" confirmation dialog (`show_archive_confirmation`) will be removed.
    *   The card will be immediately archived via the Trello API.
    *   Temporarily store the card's information (ID, text) and its original position (index) in the displayed list.
    *   The card will be instantly removed from the local list on screen, and the list will be redrawn to reflect this.

2.  **New Centered "Undo" Modal:**
    *   The current bottom-bar `show_undo_notification` will be replaced with a new modal dialog.
    *   This modal will be centered on the screen for easier interaction.
    *   It will clearly display "Archived: [Full Card Text]" (or a suitably formatted version).
    *   It will feature a prominent "UNDO" button.
    *   This modal will appear immediately after a card is archived.

3.  **"Undo" Action and Restoring Card Position:**
    *   If the "UNDO" button on the new modal is tapped:
        *   The card will be unarchived via the Trello API.
        *   The card will be immediately re-inserted into the *local list on screen at its original position* (using the stored index).
        *   The list will be redrawn, showing the card restored.
        *   The "Undo" modal will disappear.
    *   This provides instant visual feedback of the card being restored to its previous place.

4.  **Undo Timeout:**
    *   The "Undo" modal will have a timeout (e.g., 15 seconds). If the timeout occurs without "UNDO" being pressed, the modal will disappear, and the card will remain archived.

**Visual Flow (Simplified):**

```mermaid
graph TD
    A[User Clicks Card on List] --> B[1. Card Archived (API)];
    B --> C[2. Card Info & Original Index Stored Locally];
    C --> D[3. Card Visually Removed from List (Local Update)];
    D --> E[4. List Redrawn Immediately];
    E --> F[5. Centered Modal Appears: "Archived: [Card Text]" with UNDO Button];

    F -- User Clicks UNDO --> G[6a. Card Unarchived (API)];
    G --> H[7a. Card Visually Re-inserted at Original Position (Local Update)];
    H --> I[8a. List Redrawn Immediately with Restored Card];
    I --> J[9a. Undo Modal Disappears];

    F -- Timeout (15s) --> K[6b. Undo Modal Disappears];
    K --> L[7b. Card Remains Archived];

    M[Periodic Trello Fetch (every 2 mins)] --> N[Syncs local list with Trello server state];
```

**Key Points of this Plan:**

*   **Responsiveness:** Actions like archiving and undoing will have immediate visual feedback on the local display before the full Trello API sync, making the interface feel faster.
*   **User Control:** The "Undo" option remains the primary way to revert an accidental archive.
*   **Accessibility:** The centered modal should be easier to use with the 3D printed case.
