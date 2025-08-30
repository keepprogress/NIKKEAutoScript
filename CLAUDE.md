# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NIKKEAutoScript (NKAS) is an automation script for the game "Goddess of Victory: NIKKE". It automates daily game tasks using computer vision, OCR, and Android device control via ADB/uiautomator2.

## Commands

### Running the Application

```bash
# Main GUI application (runs on port 12271 by default)
python gui.py

# Run with custom port
python gui.py --port 8080

# Run main automation loop directly
python main.py

# Run for specific user profiles
python gui_user1.py
python gui_user2.py

# Launch multi-user support
python launch_multi_user.py
```

### Frontend Development (webapp directory)

```bash
cd webapp

# Install dependencies
npm install

# Development mode with hot reload
npm run dev

# Build for production
npm run build

# Individual build steps
npm run build:vue   # Build Vue frontend
npm run build:tsc   # Build TypeScript
npm run build:win   # Build Electron app for Windows
```

### Python Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

Key dependencies:
- `cnocr==2.2.2.3` - Chinese/text OCR engine
- `uiautomator2==2.16.22` - Android device control
- `adbutils==1.2.2` - ADB utilities
- `opencv-python` - Image processing
- `torch` - Deep learning backend for OCR
- `pywebio==1.7.1` - Web UI framework

## Architecture

### Core Components

1. **Main Automation Loop** (`main.py:NikkeAutoScript`)
   - Central orchestrator that manages task scheduling and execution
   - Implements retry logic and error recovery
   - Task queue management with priority scheduling
   - Config-driven task execution

2. **Device Control Layer** (`module/device/`)
   - Abstraction over multiple Android control methods (ADB, uiautomator2, minitouch)
   - Screenshot capture and caching
   - Touch event simulation
   - App lifecycle management

3. **OCR System** (`module/ocr/`)
   - Custom `NikkeOcr` class extending CnOCR for game-specific text recognition
   - Specialized classes: `Digit` for numbers, `DigitCounter` for counters (e.g., "14/15")
   - Pre-trained models stored in `./bin/cnocr_models/nikke/`
   - Image preprocessing for better OCR accuracy

4. **Task Modules** (`module/*/`)
   Each game feature has its own module:
   - `reward/` - Daily rewards collection
   - `commission/` - Commission management
   - `conversation/` - Character dialogue automation
   - `shop/` - Shop purchases
   - `simulation_room/` - Simulation room battles
   - `tribe_tower/` - Tribe tower challenges
   - `interception/` - Interception battles
   - `liberation/` - Liberation missions

5. **UI Navigation** (`module/ui/`)
   - Page detection and navigation
   - State management for UI transitions
   - Button detection using template matching

6. **Web Interface** (`module/webui/` and `webapp/`)
   - FastAPI backend serving configuration and control endpoints
   - Vue.js frontend for user interaction
   - Electron wrapper for desktop application
   - Real-time process management

### Key Design Patterns

1. **Base Classes**:
   - All task modules inherit from `module.base.base.Base`
   - Provides common functionality: screenshot, click detection, wait methods
   - Implements retry decorators and error handling

2. **Asset Management**:
   - Each module has an `assets.py` file defining UI elements as `Button` objects
   - Buttons contain coordinates and image templates for detection
   - Centralized asset extraction tools in `dev_tools/`

3. **Configuration System**:
   - YAML-based configuration in `module/config/argument/`
   - Multi-language support via i18n
   - Runtime config binding for task-specific settings
   - Config watching for hot-reload

4. **Error Recovery**:
   - Automatic game restart on stuck detection
   - Screenshot logging for debugging (`./log/error/`)
   - Configurable retry limits per task

## Development Guidelines

### Adding New Game Features

1. Create a new module directory under `module/`
2. Define UI elements in `assets.py`
3. Implement task logic inheriting from `Base`
4. Register the task in `main.py:NikkeAutoScript`
5. Add configuration options to `module/config/argument/`

### Working with OCR

- Game must have specific graphics settings enabled: "光晕效果" (Halo Effect) and "颜色分级" (Color Grading)
- OCR models are specifically trained for NIKKE's UI font
- Use `Digit` class for number recognition, `Ocr` for general text

### Device Requirements

- BlueStacks emulator version 5.20.101.6503 recommended
- Display: 720x1280, 240 DPI, portrait mode
- Graphics: Vulkan renderer, software interface renderer
- Android debugging must be enabled

### Debugging

- Error logs with screenshots saved to `./log/error/<timestamp>/`
- Use `logger` module for consistent logging
- Screenshot deque maintains last 60 screenshots for debugging
- Sensitive information is automatically redacted from logs

## Common Issues

1. **OCR failures**: Ensure game graphics settings match requirements
2. **Click detection issues**: Verify emulator resolution is 720x1280 (portrait)
3. **Connection issues**: Check ADB connection string in config (e.g., `127.0.0.1:5555`)
4. **Google Play issues**: Use QooApp version of the game instead