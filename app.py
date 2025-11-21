import os
import json
import secrets
import string
import hashlib
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

app = Flask(__name__)
# IMPORTANT: Change this secret key for production use!
app.secret_key = "very-secure-random-secret-key-for-portfolio-app"

API_KEYS_DB = {
    "frontend_app": "e551717849e6f3b7d15764d50c18428580f121d5a9d82e18153c3e808381cc93"
}


SUBMISSIONS_FILE = 'submissions.json'

SOCIAL_LINKS = {
    "github": "https://github.com/NiahrikaaSingh21",
    "linkedin": "https://www.linkedin.com/in/niharikaa21"
    
}

PORTFOLIO_PROJECTS = [
     {
        "title": "Portfolio using HTML/ CSS/JS",
        "desc": " You can view my work on my portfolio the present one is just to exhibit my skills with flask",
        "link": "niharikaasingh21.github.io/Portfolio/"
    },

    {
        "title": "Ummed-Inspiring-India",
        "desc": "Umeed (उम्मीद) means 'hope'. This repository aims to collect, organize, and share initiatives, stories, and resources that inspire action and empower individuals and communities throughout India❤️",
        "link": "https://adityaxchaudhary.github.io/Umeed-Inspiring-India/"
    },
    {
        "title": "Weather-App",
        "desc": "A simple and smart Weather App that shows accurate 5-day forecasts, uses your current location, and offers light/dark theme toggling for a comfortable viewing experience.❤️",
        "link": "https://weather-app-eta-ruby.vercel.app/"
    },
     {
        "title": "Netflix Clone",
        "desc": " Netflix Clone A responsive and visually engaging Netflix Clone website built using HTML, CSS, and JavaScript.",
        "link": "niharikaasingh21.github.io/Netflix-Clone/"
        
    },
    {
        "title": "More Projects",
        "desc": " Visit my Github account for more amaing projects .",
        "link": "https://github.com/NiharikaaSingh21/"
        
    }


]


def save_submission(data):
    """Loads existing submissions and appends the new one."""
    submissions = []
    if os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as f:
            try:
                submissions = json.load(f)
            except json.JSONDecodeError:
                submissions = []
    
    data["timestamp"] = datetime.utcnow().isoformat() + "Z"
    submissions.append(data)
    
    with open(SUBMISSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(submissions, f, indent=2, ensure_ascii=False)


def hash_key(key):
    """
    Hashes the key using SHA-256 for secure comparison.
    NOTE: For production, use a library like 'passlib' with bcrypt or Argon2.
    """
    return hashlib.sha256(key.encode()).hexdigest()

def generate_api_key():
    """Generates a secure, 40-character API key (For manual, one-time generation)."""
    characters = string.ascii_letters + string.digits + '.-_'
    new_key = ''.join(secrets.choice(characters) for i in range(40))
    print("-" * 50)
    print(f"Generated Key (Plain Text): {new_key}")
    print(f"Key Hash (STORE THIS IN API_KEYS_DB): {hash_key(new_key)}")
    print("-" * 50)
    return new_key

def require_api_key(view_func):
    """
    Decorator to protect routes by requiring a valid API Key in the 'X-API-Key' header.
    """
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({"error": "Unauthorized: Missing API Key in X-API-Key header"}), 401
        
        incoming_hash = hash_key(api_key)
        
        is_valid = False
        for stored_hash in API_KEYS_DB.values():
            if stored_hash == incoming_hash:
                is_valid = True
                break

        if not is_valid:
            return jsonify({"error": "Forbidden: Invalid API Key"}), 403
        
        return view_func(*args, **kwargs)
    return decorated_function



@app.route('/')
def index():
  
    return render_template("index.html", projects=PORTFOLIO_PROJECTS, socials=SOCIAL_LINKS)
current_year = datetime.now().year
@app.route("/contact", methods=["POST"])
def contact():
    """Handles traditional HTML form submissions."""
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("Please fill in all fields.", "danger")
        return redirect(url_for("index") + "#contact")

    submission = {
        "name": name,
        "email": email,
        "message": message
    }

    try:
        save_submission(submission)
        flash("Thanks — your message was received!", "success")
    except Exception as e:
        app.logger.error(f"Error saving traditional contact form: {e}")
        flash("There was an error saving your message. Try again.", "danger")

    return redirect(url_for("index") + "#contact")


@app.route('/api/submit_contact', methods=['POST'])
@require_api_key  # <-- This endpoint requires the API key
def submit_contact():
   
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not all([name, email, message]):
            return jsonify({'error': 'Missing required fields'}), 400

        submission = {
            'name': name,
            'email': email,
            'message': message
        }

        save_submission(submission)
        
        return jsonify({'message': 'Submission successful!'}), 200

    except Exception as e:
        app.logger.error(f"Error during API submission: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500


@app.route("/api/submissions", methods=["GET"])
def api_submissions():
    
    if os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    return jsonify(data)

if __name__ == '__main__':
    
    app.run(debug=True)