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
