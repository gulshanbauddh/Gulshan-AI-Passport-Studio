# Gulshan AI Passport Studio

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()

An automated desktop utility powered by Deep Learning AI (`bria-rmbg-2.0` / ONNX Runtime) to convert raw smartphone camera captures into official **Indian Standard Passport Size Photos (35mm x 45mm)** with a solid **Pure White Background (`#FFFFFF`)**.

Designed for institutional workflows, schools, student ID management, and automated ERP photo processing.

---

## Key Features

- **AI-Powered Background Eraser:** Automatically cuts complex backgrounds cleanly, including loose hair and edges.
- **Pure White Background Replacement:** Composites the isolated subject onto standard RGB `(255, 255, 255)`.
- **Intelligent Passport Cropping:** Centers the head and torso according to standard 35mm x 45mm (413 x 531 px @ 300 DPI) framing.
- **Automated AI Engine Check:** Checks if the local ONNX weights exist. If present, the engine status turns **Green (Ready)**; otherwise, provides a one-click built-in downloader.
- **Multi-threaded GUI:** Batch processes hundreds of images smoothly without GUI freeze or "Not Responding" errors.
- **Offline Capable:** Works 100% locally on CPU without sending data to third-party APIs or cloud servers once model weights are stored.

---

## Directory Structure

```text
Gulshan_AI_Passport_Studio/
├── removeBG.py          # Main Tkinter Desktop Application
├── requirements.txt     # Python dependencies
├── build_exe.bat        # 1-Click PyInstaller executable builder
├── .gitignore           # Ignores build artifacts and raw datasets
├── LICENSE              # MIT License
└── README.md            # Documentation & setup guide
```

---

## Prerequisites

- **OS:** Windows 10 / 11 (64-bit)
- **Python:** Python 3.9 to 3.12 (Make sure to check *"Add Python to PATH"* during installation)

---

## Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/gulshanbauddh/Gulshan-AI-Passport-Studio.git
   cd Gulshan-AI-Passport-Studio
   ```

2. **Create and Activate a Virtual Environment (Recommended):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Launch the Application:**
   ```powershell
   python removeBG.py
   ```

---

## How to Use

1. Launch the application.
2. Verify the **AI Engine Status** indicator:
   - **Green (● AI Engine Ready):** The model is present locally at `~/.rembg/models/bria-rmbg/bria-rmbg.onnx`.
   - **Red (● AI Model Missing):** Click **Download AI Model (1.02 GB)** once. Progress will display directly in the app.
3. Click **Browse...** to select your **Source Folder** containing raw student photos.
4. Click **Browse...** to select your **Destination Folder** where the output passport photos will be saved.
5. Click **Start Processing Photos**. The tool will automatically isolate the subject, apply white background, resize to 413x531 px, and export high-quality JPEGs.

---

## Build Standalone Windows EXE

To compile a single portable `.exe` file that runs without Python installed:

### Method 1: Using the provided batch script
Double-click `build_exe.bat` or run:
```cmd
build_exe.bat
```

### Method 2: Manual command
```powershell
python -m PyInstaller --noconsole --onefile --name "Gulshan_AI_Passport_Studio" --hidden-import="rembg" --hidden-import="onnxruntime" --hidden-import="PIL" --hidden-import="timm" removeBG.py
```

The compiled standalone executable will be located inside the `dist/` folder:
```text
dist/Gulshan_AI_Passport_Studio.exe
```

---

## Author

- **Developer:** Gulshan
- **Project:** Gulshan-AI-Passport-Studio ERP & Identity Utility

---

## License

This project is licensed under the [MIT License](LICENSE).
