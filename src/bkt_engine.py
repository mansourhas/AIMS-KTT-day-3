import json
import random
import os

class AdaptiveTutorBKT:
    def __init__(self, curriculum_path):
        """Initializes the Bayesian Knowledge Tracing engine."""
        print("Loading Curriculum for BKT Engine...")
        
        if not os.path.exists(curriculum_path):
            raise FileNotFoundError(f"Could not find {curriculum_path}")
            
        with open(curriculum_path, 'r', encoding='utf-8') as f:
            self.curriculum = json.load(f)
            
        # Group questions by skill and difficulty for fast lookups
        self.questions_by_skill = {}
        for q in self.curriculum:
            skill = q['skill']
            if skill not in self.questions_by_skill:
                self.questions_by_skill[skill] = []
            self.questions_by_skill[skill].append(q)

        # Standard BKT Parameters for early learners
        self.bkt_params = {
            "p_init": 0.20,      # Initial probability they know the skill
            "p_transit": 0.15,   # Probability they learn it after one question
            "p_slip": 0.10,      # Probability they know it but make a mistake (10%)
            "p_guess": 0.20      # Probability they don't know it but guess right (20%)
        }
        
        # This dictionary tracks the current user's mastery of each skill
        # In a real app, this would load from a database based on student_id
        self.student_mastery = {
            "counting": self.bkt_params["p_init"],
            "addition": self.bkt_params["p_init"],
            "subtraction": self.bkt_params["p_init"],
            "number_sense": self.bkt_params["p_init"],
            "word_problem": self.bkt_params["p_init"]
        }

    def update_mastery(self, skill, is_correct):
        """
        The core BKT math. Updates the student's mastery probability 
        based on whether they got the last question right or wrong.
        """
        p_L = self.student_mastery[skill]
        p_T = self.bkt_params["p_transit"]
        p_S = self.bkt_params["p_slip"]
        p_G = self.bkt_params["p_guess"]

        if is_correct:
            # Probability they knew it, given they got it right
            p_L_given_obs = (p_L * (1 - p_S)) / ((p_L * (1 - p_S)) + ((1 - p_L) * p_G))
        else:
            # Probability they knew it, given they got it wrong
            p_L_given_obs = (p_L * p_S) / ((p_L * p_S) + ((1 - p_L) * (1 - p_G)))

        # Add the probability that they learned it DURING this step
        new_mastery = p_L_given_obs + (1 - p_L_given_obs) * p_T
        
        # Clamp between 0.01 and 0.99
        self.student_mastery[skill] = max(0.01, min(0.99, new_mastery))
        
        return self.student_mastery[skill]

    
    def get_next_question(self, target_skill=None, target_age_band=None):
        """
        Selects the next question from the Zone of Proximal Development.
        Now supports age-band filtering!
        """
        # 1. Pick the lowest mastered skill if one isn't explicitly requested
        if not target_skill:
            target_skill = min(self.student_mastery, key=self.student_mastery.get)

        mastery_level = self.student_mastery[target_skill]
        
        # 2. Map mastery (0.0 to 1.0) to a target difficulty (1 to 10)
        target_difficulty = max(1, int(mastery_level * 10))
        
        available_questions = self.questions_by_skill.get(target_skill, [])
        
        # 3. NEW: Filter by age band to keep it age-appropriate
        if target_age_band:
            available_questions = [
                q for q in available_questions 
                if q['age_band'] == target_age_band
            ]
        
        # 4. Find questions within +/- 1 difficulty level
        suitable_questions = [
            q for q in available_questions 
            if abs(q['difficulty'] - target_difficulty) <= 1
        ]
        
        # Fallback if the filters are too strict
        if not suitable_questions:
            suitable_questions = available_questions if available_questions else self.curriculum
            
        return random.choice(suitable_questions)

# ==========================================
# BATCH TESTING LOGIC (Run from Terminal)
# ==========================================
def main():
    CURRICULUM_PATH = './dataset/generated/expanded_curriculum.json'
    tutor = AdaptiveTutorBKT(CURRICULUM_PATH)
    
    print("\n--- Testing Knowledge Tracing (BKT) Engine ---")
    skill_to_test = "addition"
    print(f"Initial mastery for '{skill_to_test}': {tutor.student_mastery[skill_to_test]:.2f}")
    
    # Simulate a student getting 3 questions RIGHT in a row
    print("\nSimulating 3 correct answers...")
    for _ in range(3):
        new_m = tutor.update_mastery(skill_to_test, is_correct=True)
        print(f" -> Student answered CORRECTLY. New Mastery: {new_m:.2f}")
        
    next_q = tutor.get_next_question(skill_to_test)
    print(f"\nServed Next Question -> Difficulty: {next_q['difficulty']} | Text: {next_q['stem_en']}")

    # Simulate a student getting 2 questions WRONG
    print("\nSimulating 2 incorrect answers...")
    for _ in range(2):
        new_m = tutor.update_mastery(skill_to_test, is_correct=False)
        print(f" -> Student answered INCORRECTLY. New Mastery: {new_m:.2f}")
        
    next_q = tutor.get_next_question(skill_to_test)
    print(f"\nServed Next Question -> Difficulty: {next_q['difficulty']} | Text: {next_q['stem_en']}")

if __name__ == "__main__":
    main()