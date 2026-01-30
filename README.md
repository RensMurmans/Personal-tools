# File Converter - DOCX ⇄ PDF

A modern web application for converting between Word documents (.docx) and PDF files (.pdf) in both directions. Features high-quality conversions powered by LibreOffice, running entirely on your local machine.

![File Converter](https://img.shields.io/badge/Status-Ready-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![LibreOffice](https://img.shields.io/badge/LibreOffice-Required-orange)

## ✨ Features

- **Bidirectional Conversion**: Convert DOCX → PDF and PDF → DOCX
- **High-Quality Results**: Powered by LibreOffice for professional-grade conversions
- **Batch Processing**: Convert multiple files at once
- **Modern UI**: Beautiful, responsive interface with drag-and-drop support
- **Progress Tracking**: Real-time conversion progress for each file
- **Bulk Download**: Download all converted files as a ZIP archive
- **100% Local**: All processing happens on your machine, no data leaves your computer

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.8 or higher**
   - Check your version: `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **LibreOffice**
   - Required for document conversion
   - See installation instructions below

### Installing LibreOffice on Mac

#### Option 1: Download from Website (Recommended)
1. Visit https://www.libreoffice.org/download/
2. Download the macOS version
3. Open the downloaded `.dmg` file
4. Drag LibreOffice to your Applications folder
5. Verify installation by opening Terminal and running:
   ```bash
   /Applications/LibreOffice.app/Contents/MacOS/soffice --version
   ```

#### Option 2: Using Homebrew
If you have Homebrew installed:
```bash
brew install --cask libreoffice
```

## 🚀 Setup Instructions

### Step 1: Navigate to Project Directory
```bash
cd /Users/rensmurmans/Documents/Tools/file-converter
```

### Step 2: Set Up Python Backend

1. **Create a virtual environment** (recommended):
   ```bash
   cd backend
   python3 -m venv venv
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Step 3: Start the Backend Server

```bash
python app.py
```

You should see:
```
🚀 Starting File Converter Backend Server...
📍 Server running at: http://localhost:5000
✅ LibreOffice found at: /Applications/LibreOffice.app/Contents/MacOS/soffice
```

**Keep this terminal window open** - the backend server needs to stay running.

### Step 4: Start the Frontend

Open a **new terminal window** and run:

```bash
cd /Users/rensmurmans/Documents/Tools/file-converter/frontend
python3 -m http.server 3000
```

You should see:
```
Serving HTTP on 0.0.0.0 port 3000 (http://0.0.0.0:3000/) ...
```

### Step 5: Open in Browser

Open your web browser and navigate to:
```
http://localhost:3000
```

🎉 **You're all set!** The application should now be running.

## 📖 How to Use

### Converting Files

1. **Choose Conversion Direction**
   - Click "Word → PDF" to convert DOCX to PDF
   - Click "PDF → Word" to convert PDF to DOCX

2. **Add Files**
   - **Drag & Drop**: Drag files directly onto the upload zone
   - **Browse**: Click "Browse Files" to select files from your computer

3. **Convert**
   - Click "Convert All" to start the conversion process
   - Watch the progress bar for each file

4. **Download**
   - Click "Download" on individual files, or
   - Click "Download All" to get all files in a ZIP archive

### Supported Formats

- **Input (Word → PDF)**: `.docx` files
- **Input (PDF → Word)**: `.pdf` files

## 🔧 Troubleshooting

### LibreOffice Not Found

If you see "LibreOffice not found" error:

1. Verify LibreOffice is installed:
   ```bash
   ls /Applications/LibreOffice.app
   ```

2. If not found, install LibreOffice following the instructions above

3. Restart the backend server:
   ```bash
   # Press Ctrl+C to stop, then run again
   python app.py
   ```

### Backend Connection Error

If the frontend can't connect to the backend:

1. Ensure the backend is running (check terminal)
2. Verify it's running on port 5000:
   ```bash
   curl http://localhost:5000/api/health
   ```
3. Check for any error messages in the backend terminal

### Port Already in Use

If port 3000 or 5000 is already in use:

**For Frontend (port 3000):**
```bash
python3 -m http.server 8080  # Use different port
# Then open http://localhost:8080
```

**For Backend (port 5000):**
Edit `backend/app.py` and change the port number in the last line:
```python
app.run(debug=True, port=5001)  # Use different port
```

Then update `frontend/app.js` to point to the new port:
```javascript
const API_BASE_URL = 'http://localhost:5001/api';
```

### Conversion Quality Issues

**DOCX → PDF**: Should preserve most formatting accurately

**PDF → DOCX**: Quality depends on the PDF structure:
- **Best results**: Text-based PDFs with simple layouts
- **Good results**: PDFs with tables and basic formatting
- **Limited results**: Scanned PDFs (images) or complex layouts

For scanned PDFs, consider using OCR software first.

## 🛑 Stopping the Application

1. **Stop Frontend**: Go to the frontend terminal and press `Ctrl+C`
2. **Stop Backend**: Go to the backend terminal and press `Ctrl+C`
3. **Deactivate Virtual Environment** (if used):
   ```bash
   deactivate
   ```

## 📁 Project Structure

```
file-converter/
├── backend/
│   ├── app.py              # Flask server with conversion logic
│   ├── requirements.txt    # Python dependencies
│   ├── uploads/           # Temporary upload storage (auto-created)
│   └── converted/         # Converted files storage (auto-created)
├── frontend/
│   ├── index.html         # Main HTML structure
│   ├── styles.css         # Modern design system
│   └── app.js            # Frontend logic
└── README.md             # This file
```

## 🔒 Privacy & Security

- **100% Local Processing**: All conversions happen on your machine
- **No Data Uploaded**: Files never leave your computer
- **Temporary Storage**: Files are stored temporarily during conversion and can be deleted manually
- **No Telemetry**: No tracking or analytics

## 💡 Tips

- **Large Files**: Conversion time increases with file size
- **Batch Conversion**: Best for files of similar size
- **Quality**: DOCX → PDF generally produces better results than PDF → DOCX
- **Formatting**: Complex documents may require manual adjustments after conversion

## 🐛 Known Limitations

1. **PDF → DOCX**: Complex PDF layouts may not convert perfectly
2. **Scanned PDFs**: Cannot convert image-based PDFs (no OCR)
3. **Password-Protected**: Encrypted files are not supported
4. **File Size**: Very large files (>100MB) may take a long time or fail

## 📝 License

This project is free to use for personal and commercial purposes.

## 🙏 Credits

- **LibreOffice**: Document conversion engine
- **Flask**: Python web framework
- **Inter Font**: Google Fonts

---

**Need Help?** Check the troubleshooting section above or verify all prerequisites are correctly installed.
