import os
import subprocess
import uuid
import shutil
import zipfile
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pdf2docx import Converter

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = Path('uploads')
CONVERTED_FOLDER = Path('converted')
ALLOWED_EXTENSIONS = {'docx', 'pdf'}

# Create necessary directories
UPLOAD_FOLDER.mkdir(exist_ok=True)
CONVERTED_FOLDER.mkdir(exist_ok=True)

# Store conversion status
conversion_status = {}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def find_libreoffice():
    """Find LibreOffice executable on macOS"""
    possible_paths = [
        '/Applications/LibreOffice.app/Contents/MacOS/soffice',
        '/usr/local/bin/soffice',
        '/opt/homebrew/bin/soffice'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Try to find in PATH
    try:
        result = subprocess.run(['which', 'soffice'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    
    return None

def convert_with_libreoffice(input_file, output_dir, output_format):
    """
    Convert document using LibreOffice
    
    Args:
        input_file: Path to input file
        output_dir: Directory for output file
        output_format: Target format ('pdf' or 'docx')
    
    Returns:
        Path to converted file or None if conversion failed
    """
    soffice_path = find_libreoffice()
    
    if not soffice_path:
        raise FileNotFoundError(
            "LibreOffice not found. Please install LibreOffice from https://www.libreoffice.org/download/"
        )
    
    # LibreOffice conversion command
    # For PDF output, we use writer_pdf_Export
    # For DOCX output, we let LibreOffice auto-detect
    filter_name = 'writer_pdf_Export' if output_format == 'pdf' else None
    
    cmd = [
        soffice_path,
        '--headless',
        '--convert-to',
        output_format if not filter_name else f'{output_format}:{filter_name}',
        '--outdir',
        str(output_dir),
        str(input_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"LibreOffice conversion error: {result.stderr}")
            return None
        
        # Find the converted file
        input_stem = Path(input_file).stem
        converted_file = output_dir / f'{input_stem}.{output_format}'
        
        if converted_file.exists():
            return converted_file
        else:
            print(f"Converted file not found: {converted_file}")
            return None
            
    except subprocess.TimeoutExpired:
        print("Conversion timeout")
        return None
    except Exception as e:
        print(f"Conversion error: {e}")
        return None

@app.route('/api/convert/docx-to-pdf', methods=['POST'])
def convert_docx_to_pdf():
    """Convert DOCX to PDF"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.docx'):
        return jsonify({'error': 'File must be a .docx document'}), 400
    
    try:
        # Generate unique ID for this conversion
        file_id = str(uuid.uuid4())
        conversion_status[file_id] = {'status': 'processing', 'progress': 0}
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = UPLOAD_FOLDER / f'{file_id}_{filename}'
        file.save(input_path)
        
        conversion_status[file_id]['progress'] = 30
        
        # Convert using LibreOffice
        output_path = convert_with_libreoffice(input_path, CONVERTED_FOLDER, 'pdf')
        
        if not output_path:
            conversion_status[file_id] = {'status': 'error', 'message': 'Conversion failed'}
            return jsonify({'error': 'Conversion failed'}), 500
        
        # Rename to include file_id for easy retrieval
        final_output = CONVERTED_FOLDER / f'{file_id}_{Path(filename).stem}.pdf'
        output_path.rename(final_output)
        
        conversion_status[file_id] = {
            'status': 'completed',
            'progress': 100,
            'output_file': str(final_output),
            'original_name': Path(filename).stem + '.pdf'
        }
        
        # Clean up input file
        input_path.unlink()
        
        return jsonify({
            'file_id': file_id,
            'status': 'completed',
            'original_name': Path(filename).stem + '.pdf'
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/convert/pdf-to-docx', methods=['POST'])
def convert_pdf_to_docx():
    """Convert PDF to DOCX"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'File must be a .pdf document'}), 400
    
    try:
        # Generate unique ID for this conversion
        file_id = str(uuid.uuid4())
        conversion_status[file_id] = {'status': 'processing', 'progress': 0}
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = UPLOAD_FOLDER / f'{file_id}_{filename}'
        file.save(input_path)
        
        conversion_status[file_id]['progress'] = 30
        
        # Convert using pdf2docx
        filename_stem = Path(filename).stem
        final_output = CONVERTED_FOLDER / f'{file_id}_{filename_stem}.docx'
        
        try:
            cv = Converter(str(input_path))
            cv.convert(str(final_output))
            cv.close()
        except Exception as e:
            print(f"pdf2docx error: {e}")
            conversion_status[file_id] = {'status': 'error', 'message': f'Conversion failed: {str(e)}'}
            return jsonify({'error': f'Conversion failed: {str(e)}'}), 500
        
        conversion_status[file_id] = {
            'status': 'completed',
            'progress': 100,
            'output_file': str(final_output),
            'original_name': filename_stem + '.docx'
        }
        
        # Clean up input file
        input_path.unlink()
        
        return jsonify({
            'file_id': file_id,
            'status': 'completed',
            'original_name': filename_stem + '.docx'
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/convert/batch', methods=['POST'])
def convert_batch():
    """Convert multiple files"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    direction = request.form.get('direction', 'docx-to-pdf')
    
    results = []
    
    for file in files:
        if file.filename == '':
            continue
        
        # Route to appropriate conversion endpoint
        if direction == 'docx-to-pdf':
            if not file.filename.lower().endswith('.docx'):
                results.append({
                    'filename': file.filename,
                    'error': 'Invalid file type'
                })
                continue
        else:  # pdf-to-docx
            if not file.filename.lower().endswith('.pdf'):
                results.append({
                    'filename': file.filename,
                    'error': 'Invalid file type'
                })
                continue
        
        try:
            file_id = str(uuid.uuid4())
            conversion_status[file_id] = {'status': 'processing', 'progress': 0}
            
            filename = secure_filename(file.filename)
            input_path = UPLOAD_FOLDER / f'{file_id}_{filename}'
            file.save(input_path)
            
            # Determine output format
            output_format = 'pdf' if direction == 'docx-to-pdf' else 'docx'
            
            # Convert
            output_path = convert_with_libreoffice(input_path, CONVERTED_FOLDER, output_format)
            
            if not output_path:
                results.append({
                    'filename': file.filename,
                    'error': 'Conversion failed'
                })
                continue
            
            # Rename output
            final_output = CONVERTED_FOLDER / f'{file_id}_{Path(filename).stem}.{output_format}'
            output_path.rename(final_output)
            
            conversion_status[file_id] = {
                'status': 'completed',
                'progress': 100,
                'output_file': str(final_output),
                'original_name': Path(filename).stem + f'.{output_format}'
            }
            
            # Clean up input
            input_path.unlink()
            
            results.append({
                'filename': file.filename,
                'file_id': file_id,
                'status': 'completed',
                'original_name': Path(filename).stem + f'.{output_format}'
            })
            
        except Exception as e:
            results.append({
                'filename': file.filename,
                'error': str(e)
            })
    
    return jsonify({'results': results})

@app.route('/api/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download a converted file"""
    if file_id not in conversion_status:
        return jsonify({'error': 'File not found'}), 404
    
    status = conversion_status[file_id]
    
    if status['status'] != 'completed':
        return jsonify({'error': 'File not ready'}), 400
    
    output_file = Path(status['output_file'])
    
    if not output_file.exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        output_file,
        as_attachment=True,
        download_name=status['original_name']
    )

@app.route('/api/download/bulk', methods=['POST'])
def download_bulk():
    """Download multiple files as a ZIP"""
    # Support both JSON body and form data
    if request.is_json:
        data = request.get_json()
        file_ids = data.get('file_ids', [])
    else:
        # Form data - file_ids is JSON encoded string
        file_ids_str = request.form.get('file_ids', '[]')
        import json
        file_ids = json.loads(file_ids_str)
    
    if not file_ids:
        return jsonify({'error': 'No files specified'}), 400
    
    # Create a temporary ZIP file
    zip_id = str(uuid.uuid4())
    zip_path = CONVERTED_FOLDER / f'{zip_id}_converted_files.zip'
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_id in file_ids:
            if file_id in conversion_status:
                status = conversion_status[file_id]
                if status['status'] == 'completed':
                    output_file = Path(status['output_file'])
                    if output_file.exists():
                        zipf.write(output_file, status['original_name'])
    
    return send_file(
        zip_path,
        as_attachment=True,
        download_name='converted_files.zip'
    )

@app.route('/api/status/<file_id>', methods=['GET'])
def get_status(file_id):
    """Get conversion status"""
    if file_id not in conversion_status:
        return jsonify({'error': 'File not found'}), 404
    
    return jsonify(conversion_status[file_id])

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    soffice_path = find_libreoffice()
    
    return jsonify({
        'status': 'healthy',
        'libreoffice_found': soffice_path is not None,
        'libreoffice_path': soffice_path
    })

if __name__ == '__main__':
    print("🚀 Starting File Converter Backend Server...")
    print("📍 Server running at: http://localhost:5001")
    print("🔍 Checking LibreOffice installation...")
    
    soffice = find_libreoffice()
    if soffice:
        print(f"✅ LibreOffice found at: {soffice}")
    else:
        print("⚠️  LibreOffice not found! Please install it from https://www.libreoffice.org/download/")
    
    app.run(debug=True, port=5001)
