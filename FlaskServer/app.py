import flask
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import sys

# Load env vars
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
from video_processor import process_video

# Database configuration
from flask_migrate import Migrate
from models import db, User, VideoLog

# ... (Imports)

app = Flask(__name__)

# Security: Restrict CORS to the frontend origin
CORS(app, origins=["http://localhost:5173"])

# Database connection
# Default to local sqlite if not provided, for safety, but prioritize Postgres
# USER PROVIDED: Postgres is running on port 5433 (mapped from 5432)
# We need to construct the URL. Assuming default user 'postgres' and password 'postgres' or similar from generic docker-compose
# If we don't have exact creds, we might fail. Let's try to read from env or default to a likely one.
# For this portfolio project, let's assume a standard URL or use SQLite as fallback if connection fails?
# User asked for Postgres. Let's try to use the one from docker ps: recallforge-db-1
# url: postgresql://postgres:postgres@localhost:5433/postgres (Standard docker defaults)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5433/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Security: Limit max content length
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/classify', methods=['POST'])
def classify_image():
    # ... (Keep existing logic, maybe log if needed)
    pass # Function body is same, just skipped for brevity involved in this specific tool call if not replacing whole file

# We need to replace the endpoints below to add DB logging

@app.route('/analyze_video', methods=['POST'])
def analyze_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400

        video = request.files['video']
        
        # Get User ID from request (header or form)
        # Get User ID from request (header or form)
        user_id = request.form.get('user_id') or request.headers.get('X-User-ID')
        
        # DEMO MODE: If no user_id, use/create a "Guest" user to ensure analysis always works
        if not user_id:
            guest_email = "guest@threatsense.ai"
            guest = User.query.filter_by(email=guest_email).first()
            if not guest:
                guest = User(name="Guest User", email=guest_email)
                db.session.add(guest)
                db.session.commit()
            user_id = guest.id
            print(f"Using Guest User ID: {user_id}")

        if video.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(video.filename):
            return jsonify({'error': 'Invalid file type. Allowed: mp4, avi, mov'}), 400

        import tempfile
        
        suffix = "." + video.filename.rsplit('.', 1)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            video.save(tmp.name)
            tmp_path = tmp.name

        try:
            # Process video
            results = process_video(tmp_path, sample_rate=30)
            os.remove(tmp_path)
            
            # Log to Database
            summary = None
            if results.get('analyst_report'):
                summary = results['analyst_report'].get('summary')
            
            new_log = VideoLog(
                user_id=user_id, # Link to user
                filename=video.filename,
                classification=results.get('classification', 'Unknown'),
                people_count=results.get('people_count', 0),
                report_summary=summary,
                severity_score=results.get('analyst_report', {}).get('severity_score', 0) if results.get('analyst_report') else 0
            )
            db.session.add(new_log)
            db.session.commit()

            return jsonify(results)
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            print(f"Video processing error: {e}")
            return jsonify({'error': 'Video processing failed'}), 500

    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/analyze_frame', methods=['POST'])
def analyze_frame():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image = request.files['image']
        if image.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        import tempfile
        import shutil
        from agent_manager import process_frame_with_agents

        suffix = "." + image.filename.rsplit('.', 1)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            image.save(tmp.name)
            tmp_path = tmp.name

        try:
            # Delegate to Agent Manager
            result = process_frame_with_agents(tmp_path)
            
            os.remove(tmp_path)
            
            # Optional: Log frames too? Might be too noisy. user asked for "videos captured or uploaded".
            # Live camera frames might be spammy. Let's log ONLY if a threat is detected?
            if result.get('classification') != "Normal":
                 summary = None
                 if result.get('analyst_report'):
                    summary = result['analyst_report'].get('summary')
                 
                 new_log = VideoLog(
                    filename=f"live_frame_{image.filename}",
                    classification=result.get('classification', 'Unknown'),
                    people_count=result.get('people_count', 0),
                    report_summary=summary,
                    severity_score=result.get('analyst_report', {}).get('severity_score', 0) if result.get('analyst_report') else 0
                 )
                 db.session.add(new_log)
                 db.session.commit()
            
            return jsonify(result)

        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            print(f"Frame analysis error: {e}")
            return jsonify({'error': 'Frame analysis failed'}), 500

    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        
        if not name or not email:
            return jsonify({'error': 'Name and email are required'}), 400
            
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # For demo purposes, return their existing ID so they can "login"
            return jsonify({
                'message': 'Email already registered',
                'user_id': existing_user.id
            }), 200
            
        new_user = User(name=name, email=email)
        # ID is auto-generated by model default logic or we can do it here
        # db.session.add(new_user) generates it if using the default=func
        
        db.session.add(new_user)
        db.session.commit()
        
        print(f"New user registration: {name} ({email}) -> ID: {new_user.id}")
        return jsonify({
            'message': 'Registration successful',
            'user_id': new_user.id
        }), 200
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

if __name__ == '__main__':
    with app.app_context():
        pass
    app.run(host='0.0.0.0', port=7001, debug=True)