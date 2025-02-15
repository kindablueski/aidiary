from flask import Flask, redirect, url_for
from auth import auth_bp
from quiz import quiz_bp
from diary import diary_bp
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(quiz_bp, url_prefix='/auth')
app.register_blueprint(diary_bp, url_prefix='/auth')

@app.route('/')
def home():
    return redirect(url_for('auth.login'))

@app.template_filter('format_date')
def format_date(value):
    if isinstance(value, str):
        dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    else:
        dt = value
    return dt.strftime('%B %d')

if __name__ == '__main__':
    app.run(debug=True)
