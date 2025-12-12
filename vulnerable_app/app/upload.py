import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from app.config import Config

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    # VULNERABILITY: Case sensitivity bypass
    # 'shell.PHP' would pass this check
    return '.' in filename and filename.split('.')[-1] in ALLOWED_EXTENSIONS

def handle_file_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    # VULNERABILITY: No file content validation
    # File extension check can be bypassed
    if allowed_file(file.filename):
        # VULNERABILITY: Path traversal possible
        # secure_filename not used consistently
        filename = request.form.get('filename', file.filename)
        
        # VULNERABILITY: Directory traversal
        # User can specify '../../../etc/passwd' in filename
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # VULNERABILITY: No size limit enforcement
        # MAX_FILE_SIZE is defined but not checked
        
        file.save(filepath)
        return jsonify({'message': 'File uploaded', 'path': filepath}), 200
    
    return jsonify({'error': 'File type not allowed'}), 400

def list_uploaded_files():
    # VULNERABILITY: Information disclosure
    # Lists all files including sensitive ones
    files = []
    for filename in os.listdir(Config.UPLOAD_FOLDER):
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        files.append({
            'name': filename,
            'path': filepath,
            'size': os.path.getsize(filepath)
        })
    return jsonify({'files': files}), 200

def download_file(filename):
    # VULNERABILITY: Path traversal in download
    # No validation of filename parameter
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    
    # VULNERABILITY: Arbitrary file read
    # Can read files outside upload folder using ../
    with open(filepath, 'rb') as f:
        content = f.read()
    
    return content, 200
