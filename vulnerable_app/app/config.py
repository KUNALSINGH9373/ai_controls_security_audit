import os

class Config:
    # VULNERABILITY: Hardcoded database credentials
    DATABASE_URL = "postgresql://admin:SuperSecret123!@localhost:5432/production_db"
    
    # VULNERABILITY: Hardcoded API key
    API_KEY = "YOUR_API_KEY"
    
    # VULNERABILITY: Debug mode enabled in production
    DEBUG = True
    
    # VULNERABILITY: Hardcoded secret key
    SECRET_KEY = "this_is_my_super_secret_key_12345"
    
    # DATABASE_URL = os.environ.get('DATABASE_URL')
    # API_KEY = os.environ.get('API_KEY')
    # SECRET_KEY = os.environ.get('SECRET_KEY')
    
    UPLOAD_FOLDER = '/tmp/uploads'
    MAX_FILE_SIZE = 16 * 1024 * 1024
