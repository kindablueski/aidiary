import re
import unicodedata
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# PHQ-9 Inspired Categories for Diary Entries
PHQ9_CATEGORIES = [
    {
        "name": "interest",
        "keywords": [
            "bored", "no interest", "nothing fun", "lost interest", "little pleasure", "anhedonia",
            "indifferent", "apathetic", "lack of motivation", "not enjoying", "uninterested", "uninspired", "dull", "tedium"
        ],
        "points": 2,
        "tag": "low_interest"
    },
    {
        "name": "depressed",
        "keywords": [
            "depressed", "down", "hopeless", "miserable", "sad", "blue", "downhearted",
            "disheartened", "gloomy", "despair", "heartbroken", "horrible", "devastated", "crushed",
            "forlorn", "despondent", "woeful", "sorrowful"
        ],
        "points": 2,
        "tag": "depressed"
    },
    {
        "name": "sleep",
        "keywords": [
            "insomnia", "sleepless", "trouble sleeping", "sleep too much", "oversleep", "can't sleep",
            "restless sleep", "waking up early", "sleep disturbance", "disturbed sleep", "broken sleep",
            "no sleep", "poor sleep", "night waking", "unrefreshing sleep"
        ],
        "points": 2,
        "tag": "sleep_issues"
    },
    {
        "name": "energy",
        "keywords": [
            "tired", "exhausted", "fatigued", "no energy", "lethargic", "sluggish", "drained", "no drive",
            "wearied", "listless", "overwhelmed", "stressed", "burned out", "spent", "zapped"
        ],
        "points": 2,
        "tag": "low_energy"
    },
    {
        "name": "appetite",
        "keywords": [
            "poor appetite", "not hungry", "overeating", "loss of appetite", "snacking excessively",
            "no appetite", "eating too little", "eating too much", "undereating", "food aversion"
        ],
        "points": 2,
        "tag": "appetite_issues"
    },
    {
        "name": "self_worth",
        "keywords": [
            "feeling bad", "failure", "worthless", "guilty", "disappointed in myself", "let down",
            "left out", "rejected", "ignored", "unworthy", "self-loathing", "self-disgust", "not good enough",
            "inferior", "inadequate", "turned down", "crushed", "defeated", "diminished", "shame"
        ],
        "points": 2,
        "tag": "low_self_worth"
    },
    {
        "name": "concentration",
        "keywords": [
            "trouble concentrating", "can't focus", "difficulty focusing", "distracted",
            "mind wandering", "my mind kept wandering", "couldn't focus", "couldn't concentrate",
            "unable to concentrate", "difficulty paying attention", "scattered thoughts",
            "absent-minded", "space out", "zoning out", "unfocused"
        ],
        "points": 2,
        "tag": "concentration_issues"
    },
    {
        "name": "psychomotor",
        "keywords": [
            "moving slowly", "fidgety", "restless", "can't sit still", "agitated", "slow movements",
            "physical agitation", "jittery", "shaky", "stiff", "uncoordinated", "sluggish movements", "leaden"
        ],
        "points": 2,
        "tag": "psychomotor_changes"
    },
    {
        "name": "suicidal",
        "keywords": [
            "suicidal", "kill myself", "better off dead", "self-harm", "end my life", "want to die",
            "life is not worth living", "commit suicide", "no reason to live", "desire to die", "die", "can't go on", "finish it all"
        ],
        "points": 3,
        "tag": "suicidal_ideation"
    }
]

SYMPTOMS_MAPPING = {
    "1": "Loss of interest or pleasure",
    "2": "Feeling down, depressed, or hopeless",
    "3": "Trouble sleeping or sleeping too much",
    "4": "Feeling tired or having little energy",
    "5": "Poor appetite or overeating",
    "6": "Feeling bad about yourself or that you are a failure",
    "7": "Trouble concentrating on things",
    "8": "Moving or speaking slowly, or being fidgety",
    "9": "Thoughts that you would be better off dead or of hurting yourself"
}

def normalize_text(text):
    return unicodedata.normalize('NFKD', text)

def detect_subject(content):
    text_lower = content.lower()
    first_person_keywords = [" i ", " me ", " my ", "mine", "myself"]
    friend_keywords = ["friend", "friends", "buddy", "buddies", "mate", "mates", "pal", "pals"]
    first_person_count = sum(text_lower.count(word) for word in first_person_keywords)
    friend_count = sum(text_lower.count(word) for word in friend_keywords)
    return "friend" if friend_count > first_person_count else "self"

def compute_wellness_score(text):
    # Normalize and prepare text
    text = normalize_text(text)
    text_lower = text.lower()
  
    # PHQ-9 Keyword-Based Calculation
    phq9_score = 0
    detected_tags = []
    for category in PHQ9_CATEGORIES:
        pattern = re.compile(r'\b(?:' + '|'.join(re.escape(keyword) for keyword in category["keywords"]) + r')\b')
        if pattern.search(text_lower):
            phq9_score += category["points"]
            detected_tags.append(category["tag"])
    max_phq9 = sum(category["points"] for category in PHQ9_CATEGORIES)
    keyword_score = int(100 * (max_phq9 - phq9_score) / max_phq9)
  
    # VADER Sentiment Analysis Calculation
    sentiment = analyzer.polarity_scores(text)
    compound = sentiment["compound"]  # ranges from -1 to +1
    sentiment_score = 60 + (compound * 40)
    sentiment_score = int(max(0, min(100, sentiment_score)))
  
    # Combine Scores
    combined_score = int((keyword_score + sentiment_score) / 2)
    return combined_score, detected_tags

def get_symptom_severity(answer):
    answer = int(answer)
    if answer == 0:
        return None
    elif answer == 1:
        return "Mild"
    elif answer == 2:
        return "Moderate"
    elif answer == 3:
        return "Severe"
def get_custom_tip(content, tags):
    """
    Generate feedback and suggestions based on the diary entry.
    For a positive diary entry (with a positive compound sentiment), provide encouraging words.
    Otherwise, provide suggestions based on the detected negative tags.
    """
    subject = detect_subject(content)
    analysis = []
    
    # Compute sentiment using VADER
    sentiment = analyzer.polarity_scores(content)
    compound = sentiment["compound"]
    
    # If overall sentiment is positive, give encouraging feedback.
    if compound > 0.3:
        analysis.append("It looks like you had a really positive day! Keep up the great work and continue doing what makes you happy!")
    else:
        # Provide suggestions only if certain negative tags are present (i.e., moderate or severe issues).
        if "depressed" in tags:
            if subject == "self":
                analysis.append("You seem very down today. It might help to talk to a trusted adult about how you're feeling.")
            else:
                analysis.append("It looks like your friend is feeling very depressed. Encourage them to speak with someone they trust.")
        if "low_self_worth" in tags:
            if subject == "self":
                analysis.append("Feeling not good enough is tough. Try writing or talking about what makes you special.")
            else:
                analysis.append("Your friend might be feeling low about themselves. Reminding them of their strengths could help.")
        if "sleep_issues" in tags:
            if subject == "self":
                analysis.append("Trouble sleeping can be hard. A calming bedtime routine might help you get better rest.")
            else:
                analysis.append("If your friend is having trouble sleeping, suggesting a quiet routine before bed could be useful.")
        if "low_energy" in tags:
            if subject == "self":
                analysis.append("Feeling low on energy can be a sign of deeper sadness. A short walk or a fun activity might help.")
            else:
                analysis.append("If your friend seems low on energy, maybe invite them to do something fun together.")
        if "concentration_issues" in tags:
            if subject == "self":
                analysis.append("Having trouble focusing can be frustrating. Taking short breaks might help you concentrate better.")
            else:
                analysis.append("If your friend is struggling to concentrate, suggest a short break or a change of activity.")
        if "psychomotor_changes" in tags:
            if subject == "self":
                analysis.append("If you're feeling restless or slow, try some stretching or light exercise.")
            else:
                analysis.append("Encouraging your friend to move around a bit might help if they seem restless.")
        if "suicidal_ideation" in tags:
            if subject == "self":
                analysis.append("Your entry shows severe distress. Please reach out immediately to a trusted adult or professional.")
            else:
                analysis.append("It appears your friend is in serious distress. Urge them to seek help from a trusted adult immediately.")
        
        # If no negative tags were detected, but the sentiment isn't strongly positive,
        # offer a gentle suggestion.
        if not analysis:
            analysis.append("Your entry shows some challenging feelings. Consider talking to someone you trust about what you're experiencing.")
    
    return " ".join(analysis)

def update_current_wellness(user_id, new_entry_score, get_db_connection):
    """
    Update the user's current wellness score by blending the new score with the previous one.
    """
    alpha = 0.2  # Weight for new score
    conn = get_db_connection()
    cur = conn.cursor()
    user = cur.execute('SELECT current_wellness FROM users WHERE id = ?', (user_id,)).fetchone()
    old_score = user['current_wellness'] if user else 100
    updated_score = int(alpha * new_entry_score + (1 - alpha) * old_score)
    cur.execute('UPDATE users SET current_wellness = ? WHERE id = ?', (updated_score, user_id))
    conn.commit()
    conn.close()
