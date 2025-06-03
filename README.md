# Blueprint Generator

A GUI application to generate project documentation and `.cursorrules` files that help the AI in Cursor IDE stay focused and consistent with your development goals.

## 🎯 What It Generates

- **`.cursorrules`** - AI configuration file for Cursor IDE
- **`architecture.md`** - Application architecture documentation
- **`project_plan.md`** - Project plan with task checklist
- **`README.md`** - (optional) README for the project
- **`.gitignore`** - (optional) Gitignore file
- **Git repository** - (optional) Initialize git repo

## 🚀 How to Run from Python

### 1. Environment Setup

```bash
# Clone or download files
# Go to the project folder
cd blueprint_generator

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python blueprint_generator.py
```

### 3. Setup API Keys

Before using, ensure you have API keys from:
- **OpenAI** (for GPT models) - https://platform.openai.com/api-keys
- **Google Gemini** (for Gemini models) - https://makersuite.google.com/app/apikey

## 📦 Creating an Executable File (.exe) on Windows

### 1. Install PyInstaller (if not already installed)

```bash
# Make sure venv is active
pip install pyinstaller
```

### 2. Generate Executable

```bash
# Single file executable (recommended)
pyinstaller --name BlueprintGenerator --onefile --windowed blueprint_generator.py

# Or with an icon (if you have an .ico file)
pyinstaller --name BlueprintGenerator --onefile --windowed --icon=icon.ico blueprint_generator.py
```

### 3. Executable Result

The `.exe` file will be available in the folder:
```
dist/BlueprintGenerator.exe
```

This file is standalone and can be run without Python installed.

## 🛠️ Requirements

- **Python 3.7+**
- **tkinter** (usually included with Python)
- **openai** (for OpenAI GPT models)
- **google-generativeai** (for Google Gemini models)

## 📋 Quick Usage

1. **Fill in project information** in the "Project Setup" tab
2. **Add application modules** in the "Modules" tab
3. **Enter the API key** of your chosen AI provider
4. **Generate blueprint** in the "Preview & Generate" tab
5. **Copy the `.cursorrules` file** to the root folder of your Cursor IDE project

## 🔧 Troubleshooting

### Error: AI library not found
```bash
pip install openai google-generativeai
```

### Error: PyInstaller not found
```bash
pip install pyinstaller
```

### Error: Invalid API key
- Ensure the API key is correct and still active
- Check quota/billing on the AI provider's dashboard

### .exe file does not run
- Ensure no antivirus is blocking it
- Try running from Command Prompt to see the error message

## 📖 More Information

For a detailed explanation of the application's purpose and features, read [ABOUT.md](ABOUT.md)

---

**Blueprint Generator** - Making Your Cursor IDE AI smarter and more focused 