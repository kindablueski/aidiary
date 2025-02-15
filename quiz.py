from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from db import get_db_connection
from helper import get_symptom_severity, SYMPTOMS_MAPPING

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

QUESTIONS = [
    {"id": 1, "question": "Over the past two weeks, how often did you have fun with your favorite activities? "},
    {"id": 2, "question": "Over the past two weeks, how often did you feel really sad or unhappy? "},
    {"id": 3, "question": "Over the past two weeks, how often did you have trouble falling asleep or sleep too much? "},
    {"id": 4, "question": "Over the past two weeks, how often did you feel super tired or low on energy?"},
    {"id": 5, "question": "Over the past two weeks, how often did you feel less hungry than usual or eat too much? "},
    {"id": 6, "question": "Over the past two weeks, how often did you feel like you weren't doing well or made a lot of mistakes?"},
    {"id": 7, "question": "Over the past two weeks, how often was it hard to focus in class?"},
    {"id": 8, "question": "Over the past two weeks, how often did you feel either really slow or too fidgety?"},
    {"id": 9, "question": "Over the past two weeks, how often did you feel so sad that nothing seemed to cheer you up?"}
]

# Mapping descriptive answer choices to numeric values
ANSWER_CHOICES = {
    0: "Never",
    1: "Rarely",
    2: "Sometimes",
    3: "A lot"
}

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
            max_quiz_score = 27  # 9 questions * 3 max points per question
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
    return render_template(
        'quiz_question.html',
        question=question,
        current_qid=qid,
        total_questions=len(QUESTIONS),
        answer_choices=ANSWER_CHOICES  # Passing the mapping to the template
    )
@quiz_bp.route('/results')
def quiz_results():
    if 'user_id' not in session or 'quiz_results' not in session or 'initial_wellness' not in session:
        flash("Please complete the quiz first.", "info")
        return redirect(url_for('quiz.quiz_start'))
    
    quiz_results = session['quiz_results']
    initial_wellness = session['initial_wellness']
    detected_symptoms = []
    suggestions = []

    # Mapping of symptom keys (or names) to suggestion texts.
    SUGGESTIONS_MAPPING = {
        "Question 2": "Consider talking to a trusted friend or counselor about your feelings.",
        "Question 3": "Try establishing a regular sleep schedule and create a relaxing bedtime routine.",
        "Question 4": "Incorporate small physical activities into your day to boost energy levels.",
        "Question 5": "Monitor your eating habits and consider consulting a nutritionist if needed.",
        "Question 6": "Keep a journal to track mistakes and identify patterns for improvement.",
        "Question 7": "Experiment with different study techniques or break tasks into smaller parts.",
        "Question 8": "Consider mindfulness or meditation practices to help manage fidgetiness.",
        "Question 9": "Engage in activities that usually bring you joy and try reaching out to someone who cares."
    }
    
    # Process each quiz question result.
    for qid, answer in quiz_results.items():
        severity = get_symptom_severity(answer)
        if severity:
            symptom = SYMPTOMS_MAPPING.get(qid, f"Question {qid}")
            detected_symptoms.append(f"{symptom} ({severity})")
            
            # Only add suggestions if severity is not mild.
            if severity.lower() != "mild":
                key = symptom if symptom.startswith("Question") else f"Question {qid}"
                if key in SUGGESTIONS_MAPPING:
                    suggestions.append(SUGGESTIONS_MAPPING[key])
    
    # Determine the image based on the wellness score.
    if initial_wellness >= 80:
        image_file = url_for('static', filename='images/happy.png')
    elif initial_wellness >= 50:
        image_file = url_for('static', filename='images/neutral.png')
    else:
        image_file = url_for('static', filename='images/sad.png')
    
    return render_template(
        'quiz_results.html',
        wellness=initial_wellness,
        symptoms=detected_symptoms,
        image_file=image_file,
        suggestions=suggestions
    )
