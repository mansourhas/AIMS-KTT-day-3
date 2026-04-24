import gradio as gr
import os

# --- IMPORT YOUR ENGINES ---
USE_MOCK = True # Set to False for the real demo

from bkt_engine import AdaptiveTutorBKT

if USE_MOCK:
    from mock_socratic_tutor import SocraticTutorLLM
else:
    from socratic_tutor import SocraticTutorLLM
    from asr_pipeline import ChildSpeechRecognizer

# --- CONFIGURATION ---
CURRICULUM_PATH = './dataset/generated/expanded_curriculum.json'
VISUALS_DIR = './dataset/generated/visuals/'
AUDIO_DIR = './dataset/generated/synthetic_audio/'

bkt_engine = AdaptiveTutorBKT(CURRICULUM_PATH)
tutor_llm = SocraticTutorLLM()

if not USE_MOCK:
    print("Loading real ASR Model...")
    recognizer = ChildSpeechRecognizer()

def normalize_answer(text):
    text = str(text).lower().strip()
    num_map = {
        "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
        "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14", "fifteen": "15",
        "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19", "twenty": "20"
    }
    return num_map.get(text, text)

# Helper list to populate the dropdown menu
question_choices = [f"{q['id']}: {q['stem_en']} (Diff: {q['difficulty']})" for q in bkt_engine.curriculum]

# --- CORE LOGIC ---

def start_session(age_band, lang):
    first_q = bkt_engine.get_next_question(target_age_band=age_band)
    img_path = os.path.join(VISUALS_DIR, f"{first_q['visual']}.png")
    audio_path = os.path.join(AUDIO_DIR, f"{first_q['id']}_{lang}.wav")
    question_display = first_q.get(f"stem_{lang}", first_q['stem_en'])

    return (
        first_q, img_path, f"### {question_display}", audio_path,
        "", 
        "*(Waiting for your answer...)*", 
        gr.update(visible=True), # Show game area
        gr.update(visible=False), # Hide setup row
        gr.update(value="", interactive=True), # Clear text input
        gr.update(value="Check my Answer", interactive=True, variant="primary"), # Reset submit button
        gr.update(interactive=False, variant="secondary") # Disable next button
    )

def process_answer(audio_input, text_input, current_q, lang):
    # 1. Input Validation
    if not text_input and not audio_input:
        return (
            "⚠️ Please type or record an answer!", 
            "*(No input detected)*",
            gr.update(interactive=True), # Keep submit active
            gr.update(interactive=False), # Keep next disabled
            current_q
        )

    expected = str(current_q['answer_int'])
    child_said = ""
    is_correct = False

    # 2. Extract Answer
    if text_input:
        child_said = text_input.strip()
        is_correct = (normalize_answer(child_said) == expected)
    else:
        if USE_MOCK:
            child_said = "five" 
            is_correct = (normalize_answer(child_said) == expected)
        else:
            asr_result = recognizer.evaluate_audio(audio_input, expected, lang)
            if asr_result["status"] == "error":
                return (f"ASR Error: {asr_result['message']}", "*(Error)*", gr.update(interactive=True), gr.update(interactive=False), current_q)
            
            child_said = asr_result["transcript"]
            if normalize_answer(child_said) == expected:
                is_correct = True
            else:
                is_correct = asr_result["is_correct"]

    # 3. Transparency Debug Output
    grade_icon = "✅ PASS" if is_correct else "❌ FAIL"
    debug_text = f"**Expected:** {expected} | **Heard:** '{child_said}' | **Result:** {grade_icon}"

    # 4. BKT & Feedback
    bkt_engine.update_mastery(current_q['skill'], is_correct)
    feedback = tutor_llm.generate_feedback(current_q['stem_en'], expected, child_said, is_correct)
    
    # --- FIXED BUTTON STATE LOGIC ---
    if is_correct:
        submit_update = gr.update(value="✅ Correct!", interactive=False, variant="secondary")
        next_update = gr.update(interactive=True, variant="primary") # Enable Next button and make it blue!
    else:
        submit_update = gr.update(value="🔄 Try Again", interactive=True, variant="secondary")
        next_update = gr.update(interactive=False, variant="secondary") # Keep Next button disabled
    # --------------------------------

    return (
        feedback, debug_text, submit_update, next_update, current_q
    )

def next_question(current_q, age_band, lang):
    next_q = bkt_engine.get_next_question(target_age_band=age_band)
    img_path = os.path.join(VISUALS_DIR, f"{next_q['visual']}.png")
    audio_path = os.path.join(AUDIO_DIR, f"{next_q['id']}_{lang}.wav")
    question_display = next_q.get(f"stem_{lang}", next_q['stem_en'])
    
    return (
        next_q, img_path, f"### {question_display}", audio_path,
        "", 
        "*(Waiting for your answer...)*", 
        gr.update(value="Check my Answer", interactive=True, variant="primary"), # Reset submit
        gr.update(interactive=False, variant="secondary"), # Disable next
        gr.update(value="", interactive=True) # Clear text
    )

def jump_to_question(selected_q_string, lang):
    """Allows the presenter to bypass BKT and jump straight to any question."""
    if not selected_q_string:
        return [gr.update()] * 9 # Do nothing if they click without selecting
        
    # Extract the ID from the dropdown string (e.g., "Q001: How many..." -> "Q001")
    q_id = selected_q_string.split(":")[0]
    next_q = next((q for q in bkt_engine.curriculum if q['id'] == q_id), bkt_engine.curriculum[0])
    
    img_path = os.path.join(VISUALS_DIR, f"{next_q['visual']}.png")
    audio_path = os.path.join(AUDIO_DIR, f"{next_q['id']}_{lang}.wav")
    question_display = next_q.get(f"stem_{lang}", next_q['stem_en'])
    
    return (
        next_q, img_path, f"### {question_display}", audio_path,
        "", "*(Jumped to specific question via Debug Menu)*", 
        gr.update(value="Check my Answer", interactive=True, variant="primary"),
        gr.update(interactive=False, variant="secondary"),
        gr.update(value="", interactive=True)
    )

# --- UI LAYOUT ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    current_question = gr.State()

    gr.Markdown("# 🍎 My Friendly Math Tutor")

    with gr.Row(visible=True) as setup_row:
        with gr.Column():
            age_select = gr.Radio(["5-6", "6-7", "7-8", "8-9"], label="Child's Age Band", value="6-7")
            lang_select = gr.Radio(["en", "fr", "kin"], label="Preferred Language", value="en")
            start_btn = gr.Button("🚀 Start Learning!", variant="primary")

    with gr.Column(visible=False) as game_area:
        
        # --- NEW: DEBUG DROP-DOWN ---
        with gr.Accordion("🛠️ Presenter Debug Menu (Jump to Question)", open=False):
            with gr.Row():
                debug_q_select = gr.Dropdown(choices=question_choices, label="Select specific question...", scale=4)
                jump_btn = gr.Button("Jump", scale=1)
        # -----------------------------

        with gr.Row():
            with gr.Column(scale=1):
                visual_display = gr.Image(label="Look at this:", interactive=False)
                question_audio = gr.Audio(label="Listen to the question", autoplay=True)
            
            with gr.Column(scale=1):
                question_text = gr.Markdown("### Question will appear here")
                
                with gr.Row():
                    answer_mic = gr.Audio(sources=["microphone"], type="filepath", label="Speak")
                    answer_text = gr.Textbox(placeholder="...or type number", label="Type")
                
                submit_btn = gr.Button("Check my Answer", variant="primary")
                
                transcript_display = gr.Markdown("*(Waiting for your answer...)*")
                feedback_display = gr.Textbox(label="Tutor Feedback", interactive=False)
                
                # The next button is now permanently visible, but we toggle 'interactive'
                next_btn = gr.Button("Next Question ➡️", interactive=False, variant="secondary")

    # --- EVENTS ---
    start_btn.click(
        fn=start_session,
        inputs=[age_select, lang_select],
        outputs=[current_question, visual_display, question_text, question_audio, feedback_display, transcript_display, game_area, setup_row, answer_text, submit_btn, next_btn]
    )

    submit_btn.click(
        fn=process_answer,
        inputs=[answer_mic, answer_text, current_question, lang_select],
        outputs=[feedback_display, transcript_display, submit_btn, next_btn, current_question]
    )

    next_btn.click(
        fn=next_question,
        inputs=[current_question, age_select, lang_select],
        outputs=[current_question, visual_display, question_text, question_audio, feedback_display, transcript_display, submit_btn, next_btn, answer_text]
    )
    
    jump_btn.click(
        fn=jump_to_question,
        inputs=[debug_q_select, lang_select],
        outputs=[current_question, visual_display, question_text, question_audio, feedback_display, transcript_display, submit_btn, next_btn, answer_text]
    )

demo.launch()