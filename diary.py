from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
from db import get_db_connection
from helper import compute_wellness_score, get_custom_tip, update_current_wellness


diary_bp = Blueprint('diary', __name__)


@diary_bp.route('/diary')
def diary():
   if 'user_id' not in session:
       return redirect(url_for('auth.login'))
   user_id = session['user_id']
   conn = get_db_connection()
   cur = conn.cursor()
   quiz_status = cur.execute('SELECT quiz_taken FROM users WHERE id = ?', (user_id,)).fetchone()
   if quiz_status is None:
       flash("User not found. Please log in again.", "info")
       return redirect(url_for('auth.login'))
   if quiz_status['quiz_taken'] == 0:
       flash("Please take the quiz first to get your initial wellness score.", "info")
       conn.close()
       return redirect(url_for('quiz.quiz_start'))
   # Retrieve all entries (ordered by most recent first)
   entries = cur.execute('SELECT * FROM entries WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
   user = cur.execute('SELECT current_wellness FROM users WHERE id = ?', (user_id,)).fetchone()
   conn.close()
   # The most recent entry is the first one if available.
   recent_entry = entries[0] if entries else None
   return render_template('diary.html', entries=entries, current_wellness=user['current_wellness'], recent_entry=recent_entry)




@diary_bp.route('/add', methods=['POST'])
def add_entry():
   if 'user_id' not in session:
       return redirect(url_for('auth.login'))
   content = request.form.get('content')
   if not content:
       flash("Please enter some content for your diary entry.", "info")
       return redirect(url_for('diary.diary'))
   score, tags = compute_wellness_score(content)
   analysis = get_custom_tip(content, tags)
   created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   user_id = session['user_id']
   tags_str = ", ".join(tags)
   conn = get_db_connection()
   conn.execute(
       'INSERT INTO entries (user_id, content, wellness_score, tags, analysis, created_at) VALUES (?, ?, ?, ?, ?, ?)',
       (user_id, content, score, tags_str, analysis, created_at)
   )
   conn.commit()
   conn.close()
   # Update overall wellness score
   update_current_wellness(user_id, score, get_db_connection)
   return redirect(url_for('diary.diary'))


@diary_bp.route('/progress')
def progress():
   if 'user_id' not in session:
       return redirect(url_for('auth.login'))
   return render_template('progress.html')


@diary_bp.route('/api/progress')
def api_progress():
   if 'user_id' not in session:
       return jsonify({"error": "Not logged in"}), 401
   user_id = session['user_id']
   conn = get_db_connection()
   entries = conn.execute('SELECT created_at, wellness_score FROM entries WHERE user_id = ? ORDER BY created_at ASC', (user_id,)).fetchall()
   conn.close()
   dates = [entry['created_at'] for entry in entries]
   scores = [entry['wellness_score'] for entry in entries]
   return jsonify({"dates": dates, "scores": scores})
