
import re
import unicodedata
from textblob import TextBlob
import logging


# PHQ-9 Inspired Categories for Diary Entries
import re
import unicodedata
from textblob import TextBlob

# Expanded PHQ-9 Categories for Diary Entries (Updated Keywords)
PHQ9_CATEGORIES = [
    {
        "name": "interest",
        "keywords": [
            "bored", "no interest", "nothing fun", "lost interest", "little pleasure", "anhedonia",
            "indifferent", "apathetic", "lack of motivation", "not enjoying", "uninterested", "uninspired", "dull", "tedium",
            "disinterested", "unenthusiastic", "not excited", "lack of enthusiasm"
        ],
        "points": 3,
        "tag": "low_interest"
    },
    {
        "name": "depressed",
        "keywords": [
            "depressed", "down", "hopeless", "miserable", "sad", "blue", "downhearted",
            "disheartened", "gloomy", "despair", "heartbroken", "horrible", "devastated", "crushed",
            "forlorn", "despondent", "woeful", "sorrowful", "dismal", "dejection",
            "nothing matters", "pointless", "no meaning", "empty", "Nothing makes me happy"
        ],
        "points": 5,
        "tag": "depressed"
    },
    {
        "name": "sleep",
        "keywords": [
            "insomnia", "sleepless", "trouble sleeping", "sleep too much", "oversleep", "can't sleep",
            "restless sleep", "waking up early", "sleep disturbance", "disturbed sleep", "broken sleep",
            "no sleep", "poor sleep", "night waking", "unrefreshing sleep", "unable to sleep", "sleep problems", "sleep way too much"
        ],
        "points": 2,
        "tag": "sleep_issues"
    },
    {
        "name": "energy",
        "keywords": [
            "tired", "exhausted", "fatigued", "no energy", "lethargic", "sluggish", "drained", "no drive",
            "wearied", "listless", "overwhelmed", "stressed", "burned out", "spent", "zapped", "worn out", "lack of stamina", "wish I had more energy"
        ],
        "points": 2,
        "tag": "low_energy"
    },
    {
        "name": "concentration",
        "keywords": [
            "trouble concentrating", "can't focus", "difficulty focusing", "distracted",
            "mind wandering", "my mind kept wandering", "couldn't focus", "couldn't concentrate",
            "unable to concentrate", "difficulty paying attention", "scattered thoughts",
            "absent-minded", "space out", "zoning out", "unfocused", "lack of concentration", "mental fog", "brain feels foggy"
        ],
        "points": 2,
        "tag": "concentration_issues"
    },
    {
        "name": "appetite",
        "keywords": [
            "poor appetite", "loss of appetite", "no appetite", "not hungry", "overeating", "eating too much",
            "binge eating", "skipping meals", "lack of appetite", "uninterested in food", "food not appealing",
            "weight loss", "weight gain", "nervous eating", "emotional eating", "cravings", "snacking too much", "forget to eat", "eat way too much"
        ],
        "points": 2,
        "tag": "appetite_issues"
    },
    {
        "name": "self_esteem",
        "keywords": [
            "feeling like a failure", "feeling bad about yourself", "worthless", "not good enough", "self-loathing",
            "self-critical", "inferior", "unlovable", "self-hate", "disgust with self", "low self-esteem",
            "feeling inadequate", "hopeless about myself", "feeling undeserving", " I’m just not good at anything", 
            "invisible", "useless", "always disappointing", "disappointing people", "no one cares", "doesn't matter", "nothing matters", "It’s not like anyone would care"
        ],
        "points": 4,
        "tag": "feelings_of_worthlessness"
    },
    {
        "name": "psychomotor",
        "keywords": [
            "moving slowly", "slowed speech", "psychomotor retardation", "fidgety", "restless", "agitated",
            "slowed movement", "physical slowing", "lack of physical energy", "clumsiness", "sluggish movements",
            "feeling heavy", "motor retardation", "slowness", "struggling to keep up"
        ],
        "points": 2,
        "tag": "psychomotor_changes"
    },
    {
        "name": "suicidal",
        "keywords": [
            "better off dead", "kill myself", "end my life", "die", "suicide", "self-harm",
            "no reason to live", "want to die", "worth dying", "murder myself", "commit suicide",
            "hopeless", "can't go on", "life isn't worth living", "suicidal thoughts", "hurt myself",
            "disappear", "disappeared", "just disappear", "would be easier if I just disappeared", "better off disappearing"
        ],
        "points": 9,
        "tag": "suicidal_thoughts"
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

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

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

    sentiment = TextBlob(text).sentiment.polarity
    sentiment_score = int(50 + (sentiment * 50))
.
    combined_score = int(0.25 * keyword_score + 0.75 * sentiment_score)

    # Log details (optional)
    logging.debug(f"PHQ-9 Score: {phq9_score} / {max_phq9}")
    logging.debug(f"Keyword Score: {keyword_score}")
    logging.debug(f"Sentiment: {sentiment}")
    logging.debug(f"Sentiment Score: {sentiment_score}")
    logging.debug(f"Combined Wellness Score: {combined_score}")
    
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
    from textblob import TextBlob
    sentiment = TextBlob(content).sentiment.polarity
    suggestions = []

    # Check if entry is strongly positive and has no negative symptom tags
    if sentiment > 0.3 and not tags:
        suggestions.append("It sounds like you're having a truly great day! Keep up the wonderful energy and continue enjoying your successes!")
        return "\n\n".join(suggestions)
    
    # Otherwise, provide the more detailed feedback
    if sentiment > 0.5:
        suggestions.append(
            "Your diary entry carries an overall positive tone, which is encouraging. "
            "Even so, some specific areas might benefit from a closer look to further enhance your well-being."
        )
    elif sentiment < 0.25:
        suggestions.append(
            "Your writing reflects some heavy and challenging emotions. "
            "The following suggestions are meant to help you explore these feelings and consider strategies to improve your day-to-day life. "
            "If these feelings persist, please consider reaching out for professional support."
        )
    else:
        suggestions.append(
            "Your diary suggests a mixed emotional state. "
            "While you seem to have moments of balance, there are a few areas that might improve with targeted self-care strategies."
        )

    # Detailed Tips for All 9 PHQ-9 Categories
    detailed_tips = {
        "loss_of_interest": (
            "You mentioned a loss of interest or pleasure in activities that once brought you joy. "
            "This can be an early signal of emotional fatigue or depression. "
            "Consider gently reintroducing small, engaging activities or exploring new hobbies that might spark your interest."
        ),
        "depressed": (
            "Your entry indicates feelings of deep sadness or depression. "
            "It might be very helpful to discuss these feelings with someone you trust—a friend, family member, or mental health professional. "
            "Talking about your emotions can sometimes lighten the load and open the door to further support."
        ),
        "sleep_issues": (
            "Sleep difficulties, whether trouble falling asleep or oversleeping, can significantly affect your mood and energy. "
            "Establishing a calming bedtime routine—like reducing screen time and engaging in relaxing activities—may help improve the quality of your sleep."
        ),
        "low_energy": (
            "Feeling persistently low on energy can make everyday tasks seem overwhelming. "
            "Incorporating short breaks, light physical activity, or even a brief walk into your day might help boost your energy levels over time."
        ),
        "appetite_issues": (
            "Noticing changes in your appetite, such as eating too much or too little, can be a response to emotional stress. "
            "Keeping a food journal might help you observe patterns, and discussing these changes with a healthcare provider could offer further insights."
        ),
        "feelings_of_worthlessness": (
            "Experiencing feelings of worthlessness or self-criticism can be deeply painful. "
            "It’s important to remind yourself that these thoughts do not reflect your true value. "
            "Consider seeking support—whether through trusted individuals or professional guidance—to work through these feelings and rebuild self-esteem."
        ),
        "concentration_issues": (
            "Difficulty concentrating can interfere with both your professional and personal life. "
            "Breaking tasks into smaller, manageable steps and creating a distraction-minimized environment may help improve your focus. "
            "Mindfulness practices can also assist in sharpening your concentration over time."
        ),
        "psychomotor_changes": (
            "Changes in the way you move or speak can sometimes mirror internal emotional shifts. "
            "If you notice that you’re moving or reacting more slowly (or even more agitated) than usual, it might be helpful to reflect on what might be causing this change and consider discussing it with a healthcare provider."
        ),
        "suicidal_thoughts": (
            "If you’re experiencing thoughts that you would be better off dead or are considering self-harm, this is a serious matter. "
            "Please consider speaking to someone immediately—a trusted friend, family member, or mental health professional. "
            "If you feel in immediate danger, do not hesitate to call your local emergency services."
        )
    }

    # Append a detailed tip for each detected PHQ-9 category
    for tag, tip in detailed_tips.items():
        if tag in tags:
            suggestions.append(tip)

    # Combined insights for overlapping issues
    if "low_energy" in tags and "sleep_issues" in tags:
        suggestions.append(
            "Since low energy and sleep disturbances often go hand in hand, focusing on your sleep hygiene could be doubly beneficial. "
            "A consistent and calming nighttime routine may help you wake up feeling more refreshed, which in turn might improve your overall energy levels."
        )

    # Fallback if no specific PHQ-9 issues were detected beyond the general sentiment
    if len(suggestions) == 1:
        suggestions.append(
            "Your diary entry does not seem to indicate any specific issues from the PHQ-9 categories. "
            "Continuing with a balanced routine that incorporates regular self-care and reflection can help maintain your well-being."
        )

    return "\n\n".join(suggestions)




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


