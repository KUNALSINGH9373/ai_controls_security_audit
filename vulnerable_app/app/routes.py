from flask import Flask, request, jsonify, session, render_template_string
from app.auth import authenticate_user, login_required, admin_required
from app.upload import handle_file_upload, list_uploaded_files, download_file
from app.database import get_user_by_id, search_users, get_all_users, backup_database
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = authenticate_user(username, password)
    if user:
        session['user'] = user
        return jsonify({'message': 'Login successful', 'user': user}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/user/<user_id>')
@login_required
def get_user(user_id):
    # VULNERABILITY: SQL injection passed through
    user = get_user_by_id(user_id)
    return jsonify({'user': user}), 200

@app.route('/search')
@login_required
def search():
    # VULNERABILITY: SQL injection in search
    search_term = request.args.get('q', '')
    results = search_users(search_term)
    return jsonify({'results': results}), 200

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    return handle_file_upload()

@app.route('/files')
@login_required
def files():
    return list_uploaded_files()

@app.route('/download/<filename>')
@login_required
def download(filename):
    # VULNERABILITY: Path traversal passed through
    return download_file(filename)

@app.route('/admin/users')
@admin_required
def admin_users():
    # Calls function that triggers backdoor
    users = get_all_users()
    return jsonify({'users': users}), 200

@app.route('/admin/backup')
@admin_required
def admin_backup():
    # Explicitly triggers backdoor
    result = backup_database()
    return jsonify(result), 200

@app.route('/profile')
@login_required
def profile():
    # VULNERABILITY: Server-Side Template Injection
    username = session.get('user', {}).get('username', 'Guest')
    
    # User input directly embedded in template
    template = request.args.get('template', '<h1>Welcome {{username}}</h1>')
    
    # VULNERABILITY: Unsafe template rendering
    return render_template_string(template, username=username)

@app.route('/debug')
def debug():
    # VULNERABILITY: Debug endpoint exposed in production
    # Reveals sensitive system information
    if app.config['DEBUG']:
        import sys
        return jsonify({
            'python_version': sys.version,
            'config': str(app.config),
            'environment': dict(request.environ),
            'session': dict(session)
        }), 200
    return jsonify({'error': 'Not found'}), 404

@app.route('/health')
def health():
    # VULNERABILITY: Information disclosure
    return jsonify({
        'status': 'healthy',
        'database': Config.DATABASE_URL,
        'debug_mode': Config.DEBUG,
        'secret_key': Config.SECRET_KEY[:10] + '...'
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
