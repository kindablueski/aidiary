from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from db import get_db_connection
from helper import get_symptom_severity, SYMPTOMS_MAPPING

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

QUESTIONS = [
    {"id": 1, "question": "I did not enjoy the things I usually like."},
    {"id": 2, "question": "I felt sad or down."},
    {"id": 3, "question": "I had trouble sleeping or slept too much."},
    {"id": 4, "question": "I felt very tired or had little energy."},
    {"id": 5, "question": "I did not feel hungry or ate too much."},
    {"id": 6, "question": "I felt bad about myself, like I was a failure."},
    {"id": 7, "question": "I had trouble paying attention in class."},
    {"id": 8, "question": "I felt very slow or fidgety."},
    {"id": 9, "question": "I thought that life was not worth living."}
]

@quiz_bp.route('/start')
def quiz_start():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    session['quiz_answers'] = {}
    return redirect(url_for('quiz.quiz_question', qid=1))

@quiz_bp.route('/<int:qid>', methods=['GET', 'POST'])
def quiz_question(qid):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if 'quiz_answers' not in session:
        session['quiz_answers'] = {}
    question = next((q for q in QUESTIONS if q['id'] == qid), None)
    if not question:
        flash("Invalid question.", "info")
        return redirect(url_for('quiz.quiz_start'))
    if request.method == 'POST':
        answer = request.form.get('answer')
        if answer is None:
            flash("Please provide an answer.", "info")
            return redirect(url_for('quiz.quiz_question', qid=qid))
        answers = session['quiz_answers']
        answers[str(qid)] = int(answer)
        session['quiz_answers'] = answers
        if qid < len(QUESTIONS):
            return redirect(url_for('quiz.quiz_question', qid=qid + 1))
        else:
            total_score = sum(answers.get(str(q['id']), 0) for q in QUESTIONS)
            max_quiz_score = 27
            initial_wellness = int(100 * (max_quiz_score - total_score) / max_quiz_score)
            user_id = session['user_id']
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'UPDATE users SET current_wellness = ?, quiz_taken = 1 WHERE id = ?',
                (initial_wellness, user_id)
            )
            diagnostic_entry = "Diagnostic quiz baseline score."
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                'INSERT INTO entries (user_id, content, wellness_score, tags, analysis, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, diagnostic_entry, initial_wellness, "", "", created_at)
            )
            conn.commit()
            conn.close()
            flash(f"Quiz completed! Your initial wellness score is {initial_wellness}/100.", "info")
            session['quiz_results'] = answers
            session['initial_wellness'] = initial_wellness
            session.pop('quiz_answers', None)
            return redirect(url_for('quiz.quiz_results'))
    return render_template('quiz_question.html', question=question, current_qid=qid, total_questions=len(QUESTIONS))

@quiz_bp.route('/results')
def quiz_results():
    if 'user_id' not in session or 'quiz_results' not in session or 'initial_wellness' not in session:
        flash("Please complete the quiz first.", "info")
        return redirect(url_for('quiz.quiz_start'))
    quiz_results = session['quiz_results']
    initial_wellness = session['initial_wellness']
    detected_symptoms = []
    for qid, answer in quiz_results.items():
        severity = get_symptom_severity(answer)
        if severity:
            symptom = SYMPTOMS_MAPPING.get(qid, f"Question {qid}")
            detected_symptoms.append(f"{symptom} ({severity})")
    return render_template('quiz_results.html', wellness=initial_wellness, symptoms=detected_symptoms)
