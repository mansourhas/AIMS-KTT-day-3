import os
import pandas as pd
from gtts import gTTS
import time

# Paths
SEED_DIR = './dataset/seeds'
AUDIO_DIR = os.path.join(SEED_DIR, 'audio')
CSV_PATH = os.path.join(SEED_DIR, 'child_utt_sample_seed.csv')

# The sample data from your project's manifest
MOCK_DATA = [
    {"utt_id": "U001", "audio_path": "audio/u001.wav", "transcript_en": "five", "language": "en", "correctness": "great"},
    {"utt_id": "U002", "audio_path": "audio/u002.wav", "transcript_en": "tu", "language": "fr", "correctness": "ok"},
    {"utt_id": "U003", "audio_path": "audio/u003.wav", "transcript_en": "esheshatu", "language": "kin", "correctness": "great"},
    {"utt_id": "U004", "audio_path": "audio/u004.wav", "transcript_en": "twewenti", "language": "en", "correctness": "poor"},
    {"utt_id": "U005", "audio_path": "audio/u005.wav", "transcript_en": "neuf", "language": "fr", "correctness": "great"}
]

def main():
    # 1. Create directories
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    # 2. Generate the CSV file
    df = pd.DataFrame(MOCK_DATA)
    df.to_csv(CSV_PATH, index=False)
    print(f"Created mock CSV at {CSV_PATH}")

    # Map dataset languages to gTTS language codes (Swahili for Kinyarwanda fallback)
    gtts_lang_map = {'en': 'en', 'fr': 'fr', 'kin': 'sw'}
    
    print("\nGenerating mock audio files...")
    
    # 3. Generate fake audio for each row
    for index, row in df.iterrows():
        text_to_speak = row['transcript_en']
        lang_code = gtts_lang_map.get(row['language'], 'en')
        
        # We need the absolute path to save the file
        full_audio_path = os.path.join(SEED_DIR, row['audio_path'])
        
        # Skip if we already mocked it
        if os.path.exists(full_audio_path):
            print(f"  -> Skipping {row['utt_id']}, file already exists.")
            continue
            
        try:
            # Generate the TTS
            tts = gTTS(text=text_to_speak, lang=lang_code)
            tts.save(full_audio_path)
            print(f"  -> Created {row['utt_id']} ({row['language']}): '{text_to_speak}'")
            time.sleep(0.5) # Prevent rate limits
        except Exception as e:
            print(f"  -> Failed to create audio for {row['utt_id']}: {e}")

    print("\nMock data generation complete! You can now run your ASR pipeline.")

if __name__ == "__main__":
    main()