import json
import os
import random
import math

# Paths
SEED_FILE = './dataset/seeds/curriculum_seed.json'
OUTPUT_FILE = './dataset/generated/expanded_curriculum.json'

NOUNS = [
    {"en": "apples", "fr": "pommes", "kin": "pome", "vis": "apples"},
    {"en": "mangoes", "fr": "mangues", "kin": "imyembe", "vis": "mangoes"},
    {"en": "goats", "fr": "chèvres", "kin": "ihene", "vis": "goats"},
    {"en": "beans", "fr": "haricots", "kin": "ibishyimbo", "vis": "beans"},
    {"en": "stones", "fr": "pierres", "kin": "amabuye", "vis": "stones"},
    {"en": "cows", "fr": "vaches", "kin": "inka", "vis": "cows"}
]

NAMES = [
    {"en": "Sara", "fr": "Sara", "kin": "Keza"},
    {"en": "John", "fr": "Jean", "kin": "Kwizera"},
    {"en": "Mary", "fr": "Marie", "kin": "Uwase"}
]

# Defines the upper bound of "comfortable" numbers for each age group
AGE_EXPECTATIONS = {
    "5-6": 10,   # P1 early: Numbers up to 10
    "6-7": 20,   # P1 late/P2 early: Numbers up to 20
    "7-8": 50,   # P2 late/P3 early: Numbers up to 50
    "8-9": 100   # P3 late: Numbers up to 100
}

def load_seeds():
    if os.path.exists(SEED_FILE):
        with open(SEED_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def calculate_relative_difficulty(primary_number, age_band, skill_offset=0):
    """
    Calculates difficulty (1-10) based on how large the number is 
    *relative* to what the specific age group is expected to know.
    """
    max_expected = AGE_EXPECTATIONS[age_band]
    
    # Ratio of the number against their expected maximum capacity
    ratio = primary_number / max_expected
    
    # Scale to a 1-10 base difficulty
    base_diff = math.ceil(ratio * 10)
    
    # Apply skill offset (e.g., word problems are cognitively harder than basic counting)
    final_diff = base_diff + skill_offset
    
    # Clamp between 1 and 10
    return max(1, min(10, final_diff if final_diff > 0 else 1))

def generate_counting(i, age_band):
    noun = random.choice(NOUNS)
    max_val = AGE_EXPECTATIONS[age_band]
    ans = random.randint(1, max_val)
    
    return {
        "id": f"GEN_C{str(i).zfill(3)}",
        "skill": "counting",
        "age_band": age_band,
        "difficulty": calculate_relative_difficulty(ans, age_band),
        "stem_en": f"How many {noun['en']} are there?",
        "stem_fr": f"Combien de {noun['fr']} y a-t-il?",
        "stem_kin": f"Hari {noun['kin']} zingahe?",
        "visual": f"{noun['vis']}_{ans}",
        "answer_int": ans
    }

def generate_addition(i, age_band):
    noun = random.choice(NOUNS)
    max_val = AGE_EXPECTATIONS[age_band]
    
    # Ensure a+b doesn't drastically exceed the max expected for their age
    a = random.randint(1, max(1, max_val // 2))
    b = random.randint(1, max(1, max_val - a + 2)) 
    ans = a + b
    
    return {
        "id": f"GEN_A{str(i).zfill(3)}",
        "skill": "addition",
        "age_band": age_band,
        "difficulty": calculate_relative_difficulty(ans, age_band), 
        "stem_en": f"What is {a} {noun['en']} plus {b} {noun['en']}?",
        "stem_fr": f"Combien font {a} {noun['fr']} plus {b} {noun['fr']}?",
        "stem_kin": f"{a} {noun['kin']} guteranya {b} {noun['kin']} ni kangahe?",
        "visual": f"{noun['vis']}_{a}_plus_{b}",
        "answer_int": ans
    }

def generate_subtraction(i, age_band):
    noun = random.choice(NOUNS)
    max_val = AGE_EXPECTATIONS[age_band]
    
    a = random.randint(2, max_val)
    b = random.randint(1, a - 1)
    ans = a - b
    
    # Difficulty driven by the starting number, not the result
    return {
        "id": f"GEN_S{str(i).zfill(3)}",
        "skill": "subtraction",
        "age_band": age_band,
        "difficulty": calculate_relative_difficulty(a, age_band), 
        "stem_en": f"What is {a} {noun['en']} minus {b} {noun['en']}?",
        "stem_fr": f"Combien font {a} {noun['fr']} moins {b} {noun['fr']}?",
        "stem_kin": f"{a} {noun['kin']} gukuramo {b} {noun['kin']} ni kangahe?",
        "visual": f"{noun['vis']}_{a}_minus_{b}",
        "answer_int": ans
    }

def generate_number_sense(i, age_band):
    max_val = AGE_EXPECTATIONS[age_band]
    a = random.randint(1, max_val)
    b = random.randint(1, max_val)
    while a == b: b = random.randint(1, max_val)
    ans = max(a, b)
    
    return {
        "id": f"GEN_N{str(i).zfill(3)}",
        "skill": "number_sense",
        "age_band": age_band,
        "difficulty": calculate_relative_difficulty(ans, age_band),
        "stem_en": f"Which number is bigger: {a} or {b}?",
        "stem_fr": f"Quel nombre est le plus grand : {a} ou {b}?",
        "stem_kin": f"Ni iyihe nimero nini: {a} cyangwa {b}?",
        "visual": f"compare_{a}_{b}",
        "answer_int": ans
    }

def generate_word_problem(i, age_band):
    noun = random.choice(NOUNS)
    name = random.choice(NAMES)
    max_val = AGE_EXPECTATIONS[age_band]
    
    a = random.randint(1, max(1, max_val // 2))
    b = random.randint(1, max(1, max_val - a + 2))
    ans = a + b
    
    # Word problems have an inherent +2 difficulty offset due to reading/listening comprehension
    return {
        "id": f"GEN_W{str(i).zfill(3)}",
        "skill": "word_problem",
        "age_band": age_band,
        "difficulty": calculate_relative_difficulty(ans, age_band, skill_offset=2),
        "stem_en": f"{name['en']} has {a} {noun['en']}. They find {b} more. How many do they have now?",
        "stem_fr": f"{name['fr']} a {a} {noun['fr']}. Ils en trouvent {b} de plus. Combien en ont-ils maintenant?",
        "stem_kin": f"{name['kin']} afite {noun['kin']} {a}. Abonye izindi {b}. Afite zingahe zose?",
        "visual": f"{noun['vis']}_word_add_{a}_{b}",
        "answer_int": ans
    }

def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    seeds = load_seeds()
    
    generators = [
        generate_counting,
        generate_addition,
        generate_subtraction,
        generate_number_sense,
        generate_word_problem
    ]
    age_bands = list(AGE_EXPECTATIONS.keys())
    
    generated_items = []
    for i in range(60):
        # 1. First, assign a random age band for this generated question
        age_band = random.choice(age_bands)
        
        # 2. Pick a random skill
        gen_func = random.choice(generators)
        
        # 3. Generate the question bound by that age's expectations
        generated_items.append(gen_func(i, age_band))
    
    expanded = seeds + generated_items
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(expanded, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {len(generated_items)} new items using age-relative difficulty logic.")
    print(f"Total dataset size: {len(expanded)}. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()