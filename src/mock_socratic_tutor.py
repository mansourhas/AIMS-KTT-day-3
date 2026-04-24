import random

# In your SocraticTutorLLM or ChildSpeechRecognizer classes
# Add a check to only load if not already loaded
class SocraticTutorLLM:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SocraticTutorLLM, cls).__new__(cls)
            # Put your loading logic here
        return cls._instance
    def __init__(self, model_id=None):
        """Mock version: No model loading required."""
        print("🚀 [MOCK] Socratic Tutor initialized (Instant Mode)")
        
        self.praise_templates = [
            "Wow! You are a math superstar! 🌟",
            "That's exactly right! Great job counting!",
            "Perfect! You're getting so good at this!",
            "High five! You got the right answer! ✋"
        ]
        
        self.hint_templates = [
            "Almost! Let's try counting them one more time together.",
            "Not quite, but you're close! Think about what comes after {prev}...",
            "Good try! What if we use our fingers to count {expected}?",
            "Take another look! If you have {total} and take away some, how many are left?"
        ]

    def generate_feedback(self, question_text, expected_answer, child_transcript, is_correct):
        """Returns a deterministic but varied response for the demo."""
        if is_correct:
            return random.choice(self.praise_templates)
        else:
            # Simple logic to make hints feel 'smart'
            hint = random.choice(self.hint_templates)
            return hint.format(
                expected=expected_answer, 
                total=question_text.split()[-1].strip('?'), # Very basic extraction
                prev=int(expected_answer)-1 if expected_answer.isdigit() else "that"
            )

# ==========================================
# QUICK TEST
# ==========================================
if __name__ == "__main__":
    tutor = SocraticTutorLLM()
    print(f"Correct Case: {tutor.generate_feedback('What is 2+2?', '4', 'four', True)}")
    print(f"Wrong Case:   {tutor.generate_feedback('What is 2+2?', '4', 'five', False)}")