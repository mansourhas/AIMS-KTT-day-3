import json
import os
from gtts import gTTS
import librosa
import soundfile as sf
import time

# pip install gTTS librosa soundfile

CURRICULUM_FILE = './dataset/generated/expanded_curriculum.json'
AUDIO_OUT_DIR = './dataset/generated/synthetic_audio/'

def shift_pitch_to_child(input_path, output_path, n_steps=5.0):
    """Loads an audio file, shifts the pitch up to sound like a child, and saves it."""
    # Load audio
    y, sr = librosa.load(input_path, sr=None)
    
    # Pitch shift up by n_steps (semitones)
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=n_steps)
    
    # Save the modified audio
    sf.write(output_path, y_shifted, sr)

def process_tts(text, lang_code, item_id, lang_suffix):
    """Generates adult TTS, shifts it to a child voice, and cleans up the base file."""
    if not text:
        return

    base_audio_path = os.path.join(AUDIO_OUT_DIR, f"base_{item_id}_{lang_suffix}.wav")
    final_audio_path = os.path.join(AUDIO_OUT_DIR, f"{item_id}_{lang_suffix}.wav")
    
    # Skip if we already generated this file (allows pausing/resuming the script)
    if os.path.exists(final_audio_path):
        return

    try:
        # Generate base adult TTS
        tts = gTTS(text=text, lang=lang_code)
        tts.save(base_audio_path)
        
        # Apply pitch shift to simulate early learner (P1-P3)
        shift_pitch_to_child(base_audio_path, final_audio_path, n_steps=5.0)
        
        # Cleanup the temporary adult voice file
        if os.path.exists(base_audio_path):
            os.remove(base_audio_path)
            
    except Exception as e:
        print(f"  -> Failed processing {item_id} ({lang_suffix}): {e}")

def main():
    os.makedirs(AUDIO_OUT_DIR, exist_ok=True)
    
    if not os.path.exists(CURRICULUM_FILE):
        print(f"Error: Could not find {CURRICULUM_FILE}")
        return

    with open(CURRICULUM_FILE, 'r', encoding='utf-8') as f:
        curriculum = json.load(f)
    
    # Mapping our JSON language keys to gTTS language codes
    # Note: gTTS doesn't natively support Kinyarwanda (rw/kin), so we fallback to Swahili (sw) 
    # to force it to attempt phonetic pronunciation for the hackathon prototype.
    lang_configs = [
        {"key": "stem_en", "code": "en", "suffix": "en"},
        {"key": "stem_fr", "code": "fr", "suffix": "fr"},
        {"key": "stem_kin", "code": "sw", "suffix": "kin"} 
    ]
    
    print(f"Loaded {len(curriculum)} items from curriculum. Starting TTS generation...")
    
    for count, item in enumerate(curriculum, 1):
        item_id = item.get('id', f"UNKNOWN_{count}")
        print(f"Processing [{count}/{len(curriculum)}]: {item_id}")
        
        for config in lang_configs:
            text = item.get(config["key"])
            process_tts(text, config["code"], item_id, config["suffix"])
            
        # Small sleep to avoid getting rate-limited by Google's TTS API
        time.sleep(0.5)

    print(f"\nAudio generation complete! Check the '{AUDIO_OUT_DIR}' folder.")

if __name__ == "__main__":
    main()