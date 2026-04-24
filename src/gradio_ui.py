import gradio as gr
import os
import time

# Import your custom modules
from asr_pipeline import ChildSpeechRecognizer
from bkt_engine import AdaptiveTutorBKT
from mock_socratic_tutor import SocraticTutorLLM

# --- CONFIGURATION & INITIALIZATION ---
CURRICULUM_PATH = './dataset/generated/expanded_curriculum.json'
VISUALS_DIR = './dataset/generated/visuals/'
AUDIO_DIR = './dataset/generated/synthetic_audio/'

# Instantiate the engines ONCE at startup
print("Initializing Tutor Components...")
recognizer = ChildSpeechRecognizer()
bkt_engine = AdaptiveTutorBKT(CURRICULUM_PATH)
tutor_llm = SocraticTutorLLM()
print("All systems go!")

# --- HELPER FUNCTIONS ---

def start_session(age_band):
    """Initializes the session and serves the first question."""
    # Start with a random skill for the chosen age group
    first_q = bkt_engine.get_next_question(target_age_band=age_band)
    
    # Construct paths
    img_path = os.path.join(VISUALS_DIR, f"{first_q['visual']}.png")
    # For the prototype, we default to English audio, but we can toggle this
    audio_path = os.path.join(AUDIO_DIR, f"{first_q['id']}_en.wav")
    
    return (
        first_q,            # State: current_question
        img_path,           # UI: Image
        first_q['stem_en'], # UI: Question Text
        audio_path,         # UI: Question Audio
        "",                 # UI: Feedback (clear it)
        gr.update(visible=True),  # Show the Game Area
        gr.update(visible=False)  # Hide the setup
    )

def process_answer(audio_input, current_q, lang_choice):
    """The core loop: Transcribe -> Grade -> Update BKT -> Generate Feedback."""
    if audio_input is None:
        return "Please record your answer first!", None, None, current_q

    # 1. ASR Transcription & Grading
    # Whisper expects 'en', 'fr', or 'kin'
    expected_answer = str(current_q['answer_int'])
    asr_result = recognizer.evaluate_audio(audio_input, expected_answer, lang_choice)
    
    if asr_result["status"] == "error":
        return f"Error: {asr_result['message']}", None, None, current_q
    
    is_correct = asr_result["is_correct"]
    child_said = asr_result["transcript"]

    # 2. Update the Brain (BKT)
    skill = current_q['skill']
    new_mastery = bkt_engine.update_mastery(skill, is_correct)

    # 3. Get Socratic Feedback from LLM
    feedback = tutor_llm.generate_feedback(
        current_q['stem_en'], 
        expected_answer, 
        child_said, 
        is_correct
    )
    
    full_feedback = f"You said: '{child_said}'\n\n{feedback}"
    
    return full_feedback, gr.update(interactive=False), gr.update(visible=True), current_q

def next_question(current_q, age_band):
    """Serves the next question based on updated BKT mastery."""
    next_q = bkt_engine.get_next_question(target_age_band=age_band)
    
    img_path = os.path.join(VISUALS_DIR, f"{next_q['visual']}.png")
    audio_path = os.path.join(AUDIO_DIR, f"{next_q['id']}_en.wav")
    
    return (
        next_q, 
        img_path, 
        next_q['stem_en'], 
        audio_path, 
        "", 
        gr.update(interactive=True), 
        gr.update(visible=False)
    )

# --- GRADIO UI LAYOUT ---

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    # Persistent State
    current_question = gr.State()
    
    gr.Markdown("# 🍎 My Friendly Math Tutor")
    gr.Markdown("Help the child learn math with pictures and talking!")

    # 1. SETUP AREA
    with gr.Row(visible=True) as setup_row:
        with gr.Column():
            age_select = gr.Radio(["5-6", "6-7", "7-8", "8-9"], label="Child's Age Band", value="6-7")
            lang_select = gr.Radio(["en", "fr", "kin"], label="Language", value="en")
            start_btn = gr.Button("🚀 Start Learning!", variant="primary")

    # 2. GAME AREA
    with gr.Column(visible=False) as game_area:
        with gr.Row():
            # Visual Aid (Left)
            with gr.Column(scale=1):
                visual_display = gr.Image(label="Look at this:", interactive=False)
                question_audio = gr.Audio(label="Listen to the question", autoplay=True)
            
            # Interaction (Right)
            with gr.Column(scale=1):
                question_text = gr.Markdown("## Question will appear here")
                answer_mic = gr.Audio(sources=["microphone"], type="filepath", label="Click to Record your Answer")
                submit_btn = gr.Button("Check my Answer", variant="primary")
                
                feedback_display = gr.Textbox(label="Tutor Feedback", interactive=False, lines=4)
                next_btn = gr.Button("Next Question ➡️", visible=False)

    # --- EVENT LOGIC ---
    
    start_btn.click(
        fn=start_session,
        inputs=[age_select],
        outputs=[current_question, visual_display, question_text, question_audio, feedback_display, game_area, setup_row]
    )

    submit_btn.click(
        fn=process_answer,
        inputs=[answer_mic, current_question, lang_select],
        outputs=[feedback_display, submit_btn, next_btn, current_question]
    )

    next_btn.click(
        fn=next_question,
        inputs=[current_question, age_select],
        outputs=[current_question, visual_display, question_text, question_audio, feedback_display, submit_btn, next_btn]
    )

if __name__ == "__main__":
    demo.launch(share=True) # Share=True creates a public link for the judges!