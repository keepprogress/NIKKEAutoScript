# Building NIKKEAutoScript Release

This guide explains how to build a Windows release with executable (.exe) for NIKKEAutoScript.

## Prerequisites

1. **Node.js and npm** - Required for building the Electron app
2. **Python 3.9.13** - Embedded version for the release
3. **Git** - For version control and updates

## Build Process

### Step 1: Prepare Python Environment

1. Download `python-3.9.13-embed-amd64.7z` from Python official site
2. Extract to project root directory
3. Keep folder name as `python-3.9.13-embed-amd64`

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Build Electron Application

```bash
# Navigate to webapp directory
cd webapp

# Install Node.js dependencies
npm install

# Run full build process
npm run build
```

The build command executes three steps in sequence:
- `npm run build:vue` - Builds Vue.js frontend with TypeScript checking
- `npm run build:tsc` - Compiles TypeScript for Electron main process
- `npm run build:win` - Packages everything into Windows executable using electron-builder

### Step 3: Locate Build Output

After successful build, the executable will be located at:
- **Main Executable**: `webapp/output/app/NikkeAutoScript.exe`
- **Frontend Assets**: `webapp/output/dist/`
- **Electron Build**: `webapp/output/build/`

## Build Configuration

The build is configured in `webapp/package.json`:

```json
{
  "build": {
    "appId": "NikkeAutoScript",
    "productName": "NikkeAutoScript",
    "win": {
      "icon": "public/Helm.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true
    },
    "files": [
      "output/dist/**/*",
      "output/build/**/*"
    ],
    "directories": {
      "output": "output/app"
    }
  }
}
```

## Release Package Structure

A complete release package should include:

```
NIKKEAutoScript-Release/
├── NikkeAutoScript.exe              # Main executable (from webapp/output/app/)
├── python-3.9.13-embed-amd64/       # Embedded Python
│   ├── python.exe
│   ├── python39.dll
│   └── ... (other Python files)
├── bin/
│   └── cnocr_models/
│       └── nikke/                   # OCR models for text recognition
│           └── *.ckpt
├── toolkit/
│   ├── Git/
│   │   └── mingw64/bin/git.exe     # Git for auto-updates
│   └── android-platform-tools/
│       └── adb.exe                  # Android Debug Bridge
├── assets/                          # Game UI templates for recognition
│   ├── cn/
│   └── event/
├── module/                          # Python automation scripts
│   ├── base/
│   ├── ocr/
│   ├── device/
│   └── ... (other modules)
├── config/
│   └── deploy-template.yaml         # Configuration template
└── requirements.txt                 # Python dependencies

```

## Development Build

For development with hot reload:

```bash
cd webapp

# Start development server with hot reload
npm run dev
```

This command:
1. Kills any process on port 5173
2. Starts Vite dev server for Vue.js frontend
3. Watches TypeScript files for changes
4. Runs Electron in development mode

## Individual Build Commands

If you need to run build steps separately:

```bash
cd webapp

# Build Vue frontend only
npm run build:vue

# Compile TypeScript only
npm run build:tsc

# Package with Electron Builder only (requires prior steps)
npm run build:win
```

## Dependencies Required

### Python Dependencies (requirements.txt)
- `uvicorn` - ASGI server
- `pywebio==1.7.1` - Web UI framework
- `torch` - Deep learning for OCR
- `cnocr==2.2.2.3` - Chinese OCR engine
- `uiautomator2==2.16.22` - Android automation
- `opencv-python` - Image processing
- `adbutils==1.2.2` - ADB utilities

### Node.js Dependencies (webapp/package.json)
- `electron` - Desktop app framework
- `vue` - Frontend framework
- `vite` - Build tool
- `electron-builder` - Packaging tool
- `typescript` - Type checking

## Troubleshooting

### Common Issues

1. **Missing Python Embedded**: Ensure `python-3.9.13-embed-amd64` folder exists in project root
2. **Node modules not found**: Run `npm install` in webapp directory
3. **Build fails on TypeScript errors**: Check TypeScript compilation with `npm run build:tsc`
4. **Electron packaging fails**: Ensure all build artifacts exist in `output/dist` and `output/build`

### Verification

After building, test the executable:
1. Run `NikkeAutoScript.exe` from `webapp/output/app/`
2. Check if web UI opens on `http://localhost:12271`
3. Verify Python scripts can be executed through the UI

## Notes

- The application uses Electron to wrap a FastAPI/PyWebIO backend with Vue.js frontend
- Python scripts are executed via python-shell from the Electron main process
- The embedded Python ensures consistency across different systems
- OCR models must be included for game automation features to work