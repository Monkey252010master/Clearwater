from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///erlc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# ERLC API configuration
ERLC_API_TOKEN = os.getenv('ERLC_TOKEN')
ERLC_SERVER_ID = os.getenv('ERLC_SERVER_ID')
api_base_url = "https://api.emergency-response.tech"

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    discord_id = db.Column(db.String(80), unique=True, nullable=False)
    is_hr = db.Column(db.Boolean, default=False)
    is_staff = db.Column(db.Boolean, default=False)

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(20), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    response = db.Column(db.Text, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/api/server-info')
def server_info():
    try:
        headers = {'Authorization': ERLC_API_TOKEN}
        response = requests.get(f"{api_base_url}/servers/{ERLC_SERVER_ID}/players", headers=headers)
        if response.status_code == 200:
            return jsonify(response.json())
        return jsonify({'error': 'Failed to fetch server info'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications', methods=['GET', 'POST'])
def applications():
    if request.method == 'POST':
        data = request.json
        application = Application(
            discord_id=data['discord_id'],
            username=data['username']
        )
        db.session.add(application)
        db.session.commit()
        return jsonify({'message': 'Application submitted successfully'})
    
    # Only HR can view all applications
    if not current_user.is_hr:
        return jsonify({'error': 'Unauthorized'}), 403
        
    applications = Application.query.all()
    return jsonify([{
        'id': app.id,
        'username': app.username,
        'status': app.status,
        'submitted_at': app.submitted_at.isoformat()
    } for app in applications])

@app.route('/api/shifts', methods=['GET', 'POST'])
@login_required
def shifts():
    if request.method == 'POST':
        shift = Shift(
            user_id=current_user.id,
            start_time=datetime.utcnow()
        )
        db.session.add(shift)
        db.session.commit()
        return jsonify({'message': 'Shift started'})
    
    user_shifts = Shift.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'start_time': shift.start_time.isoformat(),
        'end_time': shift.end_time.isoformat() if shift.end_time else None
    } for shift in user_shifts])

@app.route('/api/shifts/end', methods=['POST'])
@login_required
def end_shift():
    active_shift = Shift.query.filter_by(
        user_id=current_user.id,
        end_time=None
    ).first()
    
    if active_shift:
        active_shift.end_time = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Shift ended'})
    return jsonify({'error': 'No active shift found'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)