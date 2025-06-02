# Blueprint Generator

Aplikasi GUI untuk menghasilkan dokumentasi proyek dan file `.cursorrules` yang membantu AI di Cursor IDE tetap fokus dan konsisten dengan tujuan development Anda.

## 🎯 Apa yang Dihasilkan

- **`.cursorrules`** - File konfigurasi AI untuk Cursor IDE
- **`architecture.md`** - Dokumentasi arsitektur aplikasi
- **`project_plan.md`** - Rencana proyek dengan task checklist
- **`README.md`** - (opsional) README untuk proyek
- **`.gitignore`** - (opsional) File gitignore
- **Git repository** - (opsional) Inisialisasi git repo

## 🚀 Cara Menjalankan dari Python

### 1. Persiapan Environment

```bash
# Clone atau download file
# Masuk ke folder proyek
cd blueprint_generator

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi

```bash
python blueprint_generator.py
```

### 3. Setup API Keys

Sebelum menggunakan, pastikan Anda memiliki API key dari:
- **OpenAI** (untuk GPT models) - https://platform.openai.com/api-keys
- **Google Gemini** (untuk Gemini models) - https://makersuite.google.com/app/apikey

## 📦 Membuat File Executable (.exe) di Windows

### 1. Install PyInstaller (jika belum ada)

```bash
# Pastikan venv aktif
pip install pyinstaller
```

### 2. Generate Executable

```bash
# Single file executable (direkomendasikan)
pyinstaller --name BlueprintGenerator --onefile --windowed blueprint_generator.py

# Atau dengan icon (jika ada file .ico)
pyinstaller --name BlueprintGenerator --onefile --windowed --icon=icon.ico blueprint_generator.py
```

### 3. Hasil Executable

File `.exe` akan tersedia di folder:
```
dist/BlueprintGenerator.exe
```

File ini sudah standalone dan bisa dijalankan tanpa Python terinstall.

## 🛠️ Requirements

- **Python 3.7+**
- **tkinter** (biasanya sudah termasuk dalam Python)
- **openai** (untuk OpenAI GPT models)
- **google-generativeai** (untuk Google Gemini models)

## 📋 Penggunaan Singkat

1. **Isi informasi proyek** di tab "Project Setup"
2. **Tambah modul aplikasi** di tab "Modules" 
3. **Masukkan API key** AI provider pilihan Anda
4. **Generate blueprint** di tab "Preview & Generate"
5. **Copy file `.cursorrules`** ke root folder proyek Cursor IDE

## 🔧 Troubleshooting

### Error: AI library tidak ditemukan
```bash
pip install openai google-generativeai
```

### Error: PyInstaller tidak ditemukan
```bash
pip install pyinstaller
```

### Error: API key tidak valid
- Pastikan API key benar dan masih aktif
- Cek quota/billing di dashboard provider AI

### File .exe tidak jalan
- Pastikan tidak ada antivirus yang memblokir
- Coba jalankan dari Command Prompt untuk melihat error message

## 📖 Informasi Lebih Lanjut

Untuk penjelasan detail tentang tujuan dan fitur aplikasi, baca [ABOUT.md](ABOUT.md)

---

**Blueprint Generator** - Membuat AI Cursor IDE Anda lebih cerdas dan fokus 