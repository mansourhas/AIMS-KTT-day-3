import json
import os
import time
import torch
import scipy.io.wavfile
import librosa
import soundfile as sf
from gtts import gTTS
from transformers import VitsModel, AutoTokenizer

# pip install transformers torch scipy gTTS librosa soundfile
# Paths
CURRICULUM_FILE = './dataset/generated/expanded_curriculum.json'
AUDIO_OUT_DIR = './dataset/generated/synthetic_audio/'

# ==========================================
# 1. LOAD THE MMS MODEL FOR KINYARWANDA
# ==========================================
print("Loading Meta MMS Kinyarwanda TTS Model (This may take a minute to download...)")
mms_model_id = "facebook/mms-tts-kin"
kin_tokenizer = AutoTokenizer.from_pretrained(mms_model_id)
kin_model = VitsModel.from_pretrained(mms_model_id)
print("Model loaded successfully!")

def shift_pitch_to_child(input_path, output_path, n_steps=5.0):
    """Loads an audio file, shifts the pitch up to sound like a child, and saves it."""
    y, sr = librosa.load(input_path, sr=None)
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=n_steps)
    sf.write(output_path, y_shifted, sr)

def generate_mms_audio(text, output_path):
    """Generates audio using Meta's MMS local model."""
    inputs = kin_tokenizer(text, return_tensors="pt")
    
    with torch.no_grad():
        output = kin_model(**inputs).waveform
        
    # MMS returns a 1D waveform tensor. We convert it to numpy and save using scipy
    audio_data = output[0].numpy()
    scipy.io.wavfile.write(output_path, rate=kin_model.config.sampling_rate, data=audio_data)

def process_tts(text, lang_code, item_id, lang_suffix):
    """Routes to the correct TTS engine, shifts to child voice, and cleans up."""
    if not text:
        return

    base_audio_path = os.path.join(AUDIO_OUT_DIR, f"base_{item_id}_{lang_suffix}.wav")
    final_audio_path = os.path.join(AUDIO_OUT_DIR, f"{item_id}_{lang_suffix}.wav")
    
    # Skip if already generated (Resume capability)
    if os.path.exists(final_audio_path):
        return

    try:
        # Route to the correct engine
        if lang_code == "mms-kin":
            generate_mms_audio(text, base_audio_path)
        else:
            # Use gTTS for English and French
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
    
    # Configuration: En/Fr use gTTS, Kin uses local MMS Model
    lang_configs = [
        {"key": "stem_en", "code": "en", "suffix": "en"},
        {"key": "stem_fr", "code": "fr", "suffix": "fr"},
        {"key": "stem_kin", "code": "mms-kin", "suffix": "kin"} 
    ]
    
    print(f"Loaded {len(curriculum)} items from curriculum. Starting TTS generation...")
    
    for count, item in enumerate(curriculum, 1):
        item_id = item.get('id', f"UNKNOWN_{count}")
        print(f"Processing [{count}/{len(curriculum)}]: {item_id}")
        
        for config in lang_configs:
            text = item.get(config["key"])
            process_tts(text, config["code"], item_id, config["suffix"])
            
        # Small sleep only needed to avoid gTTS rate limits
        time.sleep(0.5)

    print(f"\nAudio generation complete! Check the '{AUDIO_OUT_DIR}' folder.")

if __name__ == "__main__":
    main()