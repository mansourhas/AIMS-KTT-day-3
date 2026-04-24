import json
import os

CURRICULUM_FILE = './dataset/generated/expanded_curriculum.json'

def main():
    if not os.path.exists(CURRICULUM_FILE):
        print(f"Error: Could not find {CURRICULUM_FILE}")
        return

    # 1. Load the existing data
    with open(CURRICULUM_FILE, 'r', encoding='utf-8') as f:
        curriculum = json.load(f)

    print(f"Loaded {len(curriculum)} existing items.")
    
    # 2. Add the audio links without changing anything else
    updated_count = 0
    for item in curriculum:
        item_id = item.get('id')
        if not item_id:
            continue
            
        # Add the audio paths if they don't already exist
        if 'tts_en' not in item:
            item['tts_en'] = f"synthetic_audio/{item_id}_en.wav"
            updated_count += 1
        if 'tts_fr' not in item:
            item['tts_fr'] = f"synthetic_audio/{item_id}_fr.wav"
        if 'tts_kin' not in item:
            item['tts_kin'] = f"synthetic_audio/{item_id}_kin.wav"

    # 3. Save it back to the exact same file
    with open(CURRICULUM_FILE, 'w', encoding='utf-8') as f:
        json.dump(curriculum, f, indent=2, ensure_ascii=False)

    print(f"Successfully linked audio for {updated_count} items!")
    print("Your dataset is now ready for the frontend.")

if __name__ == "__main__":
    main()