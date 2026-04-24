import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline

# pip install transformers torch accelerate bitsandbytes

class SocraticTutorLLM:
    def __init__(self, model_id="microsoft/Phi-3-mini-4k-instruct"):
        """
        Initializes the Quantized LLM. 
        Using 4-bit quantization (bitsandbytes) ensures it fits in small VRAM 
        and simulates the 'on-device' constraint of the hackathon brief.
        """
        print(f"Loading Quantized LLM ({model_id}). This will take a moment...")
        
        
        # Load the model in 4-bit precision to save memory and increase speed
        # Define the quantization configuration
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

        print(f"Loading Quantized LLM ({model_id})...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            device_map="auto", 
            quantization_config=quantization_config, # Pass the config here instead
            trust_remote_code=True
        )
        print("Socratic Tutor LLM loaded successfully!")

    def generate_feedback(self, question_text, expected_answer, child_transcript, is_correct):
        """
        Generates Socratic, low-literacy feedback based on the child's attempt.
        """
        # The System Prompt is the secret sauce. 
        # It forces the LLM to behave like a primary school teacher and NEVER just give the answer.
        system_prompt = (
            "You are a warm, patient, and encouraging math tutor for a 6-year-old child. "
            "Your goal is to help them learn using the Socratic method. \n"
            "RULES:\n"
            "1. Keep it extremely short (1 to 2 simple sentences). The child has low literacy.\n"
            "2. Use simple, everyday words.\n"
            "3. If the child is wrong, NEVER tell them the direct answer. Ask a gentle guiding question.\n"
            "4. If the child is right, praise them enthusiastically.\n"
            "5. Do NOT use complex math jargon."
        )

        if is_correct:
            user_prompt = f"The question was: '{question_text}'. The expected answer was {expected_answer}. The child said '{child_transcript}', which is CORRECT. Give them a short, happy compliment."
        else:
            user_prompt = f"The question was: '{question_text}'. The expected answer was {expected_answer}. The child said '{child_transcript}', which is WRONG. Give them a gentle, helpful hint or ask a simpler guiding question to help them figure it out. Do not give the answer {expected_answer}."

        # Format for instruction-tuned models (Phi-3 / Llama-3 format)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        prompt = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )

        # Generate the response
        outputs = self.pipe(
            prompt,
            max_new_tokens=50, # Keep it very short so TTS doesn't take forever to speak it
            temperature=0.3,   # Low temp = more predictable, less hallucination
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # Extract just the generated text
        generated_text = outputs[0]["generated_text"][len(prompt):].strip()
        return generated_text

# ==========================================
# BATCH TESTING LOGIC
# ==========================================
def main():
    tutor = SocraticTutorLLM()
    
    print("\n--- Testing Socratic Tutor LLM ---")
    
    # Scenario 1: The child gets it right
    q_text = "What is 4 apples plus 5 apples?"
    expected = "9"
    child_said = "nine"
    is_correct = True
    
    print(f"\nQuestion: {q_text}")
    print(f"Child said: '{child_said}' (Correct: {is_correct})")
    feedback = tutor.generate_feedback(q_text, expected, child_said, is_correct)
    print(f"Tutor Response: {feedback}")

    # Scenario 2: The child gets it wrong
    q_text = "If a basket has 12 beans and you eat 7, how many remain?"
    expected = "5"
    child_said = "ten"
    is_correct = False
    
    print(f"\nQuestion: {q_text}")
    print(f"Child said: '{child_said}' (Correct: {is_correct})")
    feedback = tutor.generate_feedback(q_text, expected, child_said, is_correct)
    print(f"Tutor Response: {feedback}")

if __name__ == "__main__":
    main()