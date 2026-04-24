import os
import pandas as pd
import librosa
import torch
import difflib
import re
from transformers import pipeline

class ChildSpeechRecognizer:
    def __init__(self, model_id="openai/whisper-tiny"):
        """
        Initializes the ASR pipeline. 
        By putting this in __init__, Gradio will only load the heavy model ONCE.
        """
        print(f"Loading ASR Model ({model_id})...")
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
        # We use pipeline for easy integration, chunking, and handling audio arrays
        self.asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model=model_id,
            device=device
        )
        print("ASR Model loaded successfully!")

    def clean_text(self, text):
        """Removes punctuation and lowers case for fairer grading."""
        text = str(text).lower()
        # Remove anything that isn't a letter or a number
        return re.sub(r'[^a-z0-9\s]', '', text).strip()

    def is_match_fuzzy(self, transcript, expected_answer, threshold=0.75):
        """
        Compares the ASR transcript to the expected answer.
        Requires a 75% similarity to pass.
        """
        clean_transcript = self.clean_text(transcript)
        clean_expected = self.clean_text(expected_answer)
        
        # Check if the exact expected word is hidden inside a longer sentence
        if clean_expected in clean_transcript:
            return True, 1.0
            
        # Calculate similarity ratio (e.g., "fiv" vs "five" = 0.85)
        ratio = difflib.SequenceMatcher(None, clean_transcript, clean_expected).ratio()
        
        return ratio >= threshold, ratio

    def evaluate_audio(self, audio_input, expected_text, language_code):
        """
        The core function Gradio will call. 
        Accepts either a file path or a raw numpy array from a mic.
        """
        # Map our dataset language codes to Whisper's language names
        whisper_lang_map = {
            'en': 'english',
            'fr': 'french',
            'kin': 'swahili' # Fallback for Kinyarwanda
        }
        whisper_lang = whisper_lang_map.get(language_code, 'english')

        try:
            # Force whisper to transcribe in the expected language
            result = self.asr_pipeline(
                audio_input, 
                generate_kwargs={"language": whisper_lang}
            )
            transcript = result["text"].strip()
            
            # Grade the answer
            is_correct, confidence = self.is_match_fuzzy(transcript, expected_text)
            
            return {
                "status": "success",
                "transcript": transcript,
                "is_correct": is_correct,
                "confidence_score": round(confidence, 2)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

# ==========================================
# BATCH TESTING LOGIC (Run this from Terminal)- -make sure you ran mock_child_audio.py first to generate the test audio files!
# ==========================================
def main():
    SEED_FILE = './dataset/seeds/child_utt_sample_seed.csv'
    # Base dir assumes the audio folder is sitting next to the seed file
    BASE_AUDIO_DIR = './dataset/seeds/' 

    if not os.path.exists(SEED_FILE):
        print(f"Error: Could not find {SEED_FILE}")
        return

    df = pd.read_csv(SEED_FILE)
    
    # Instantiate the class (Loads model)
    recognizer = ChildSpeechRecognizer()
    
    results_log = []
    
    print("\nStarting Batch Evaluation...\n")
    for index, row in df.iterrows():
        utt_id = row['utt_id']
        expected_text = row['transcript_en'] # The ground truth
        lang = row['language']
        
        # Construct the full path to the audio file
        audio_path = os.path.join(BASE_AUDIO_DIR, row['audio_path'])
        
        if not os.path.exists(audio_path):
            print(f"[{utt_id}] SKIPPED: Audio file missing at {audio_path}")
            continue
            
        print(f"[{utt_id}] Listening to {lang} audio... Expected: '{expected_text}'")
        
        # Evaluate
        result = recognizer.evaluate_audio(audio_path, expected_text, lang)
        
        if result["status"] == "success":
            transcribed = result['transcript']
            graded = "✅ PASS" if result['is_correct'] else "❌ FAIL"
            print(f"   -> Heard: '{transcribed}' | Grade: {graded} (Sim: {result['confidence_score']})")
        else:
            print(f"   -> Error processing audio: {result['message']}")
            
        results_log.append(result)

if __name__ == "__main__":
    main()