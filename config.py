class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:soum@localhost/v_tickets'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key'
    API_KEY = 'admin-key'