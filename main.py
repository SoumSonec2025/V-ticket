from flask import Flask, render_template
from flask_cors import CORS
from backend.app.presentation.api_controller import api_bp
from backend.app.infrastructure.database.postgres_repository import init_db

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
app.config.from_object('config.Config')

init_db(app)
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/visitor.html')
def serve_visitor():
    return render_template('visitor.html')

@app.route('/ticket.html')
def serve_ticket():
    return render_template('ticket.html')

@app.route('/admin.html')
def serve_admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)