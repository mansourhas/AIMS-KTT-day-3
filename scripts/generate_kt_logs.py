import pandas as pd
import numpy as np
import os

PROBES_FILE = './dataset/seeds/diagnostic_probes_seed.csv'
OUTPUT_FILE = './dataset/generated/kt_interaction_logs.csv'

def simulate_student_interactions(probes_df, num_students=100, interactions_per_student=50):
    logs = []
    skills = probes_df['skill'].unique()
    
    for student_id in range(1, num_students + 1):
        # Assign a random initial hidden mastery level for each skill
        mastery = {skill: np.random.uniform(0.1, 0.4) for skill in skills}
        
        for step in range(interactions_per_student):
            # Select a random probe/question
            probe = probes_df.sample(1).iloc[0]
            skill = probe['skill']
            difficulty = probe['difficulty']
            
            # Probability of correct answer depends on mastery vs difficulty
            # Using a simplified Item Response Theory (IRT) curve
            prob_correct = 1 / (1 + np.exp(-(mastery[skill] * 10 - difficulty)))
            
            # Simulate guess (0.2) and slip (0.1)
            is_correct = 1 if np.random.rand() < prob_correct else 0
            if is_correct == 0 and np.random.rand() < 0.2: is_correct = 1
            if is_correct == 1 and np.random.rand() < 0.1: is_correct = 0
            
            logs.append({
                "student_id": f"STU_{str(student_id).zfill(4)}",
                "timestamp": pd.Timestamp('2026-05-01') + pd.Timedelta(minutes=step*5),
                "item_id": probe['id'],
                "skill": skill,
                "difficulty": difficulty,
                "correct": is_correct
            })
            
            # Simulate learning (update hidden mastery)
            mastery[skill] = min(0.99, mastery[skill] + np.random.uniform(0.01, 0.05))
            
    return pd.DataFrame(logs)

def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    probes = pd.read_csv(PROBES_FILE)
    
    kt_logs = simulate_student_interactions(probes, num_students=200, interactions_per_student=60)
    kt_logs.to_csv(OUTPUT_FILE, index=False)
    print(f"Generated {len(kt_logs)} KT interaction rows. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()