import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline

# pip install transformers torch accelerate bitsandbytes


# In your SocraticTutorLLM or ChildSpeechRecognizer classes
# Add a check to only load if not already loaded
class SocraticTutorLLM:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SocraticTutorLLM, cls).__new__(cls)
            # Put your loading logic here
        return cls._instance
    def __init__(self, model_id="microsoft/Phi-3-mini-4k-instruct"):
        print(f"Loading Quantized LLM ({model_id})...")
        
        # We no longer need to manually patch the config if we use native code
        # but we'll keep the BitsAndBytes configuration for 4-bit support.
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        # IMPORTANT: Set trust_remote_code=False to use the native Transformers implementation
        # which is compatible with your current version of DynamicCache.
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            device_map="auto", 
            quantization_config=quantization_config,
            trust_remote_code=False 
        )
        
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
        )
        print("Socratic Tutor LLM loaded successfully!")

    def generate_feedback(self, question_text, expected_answer, child_transcript, is_correct):
        system_prompt = (
            "You are a warm, patient, and encouraging math tutor for a 6-year-old child. "
            "Help them learn using the Socratic method. Keep it to 1-2 simple sentences."
        )

        if is_correct:
            user_prompt = f"The child got it right! They said '{child_transcript}' for '{question_text}'. Praise them!"
        else:
            user_prompt = f"The child said '{child_transcript}' for '{question_text}'. The answer is {expected_answer}. Give a tiny hint without telling the answer."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        # FIXED: Removed pad_token_id and adjusted parameters to avoid deprecation warnings
        outputs = self.pipe(
            prompt,
            max_new_tokens=50,
            temperature=0.7,
            do_sample=True,
            return_full_text=False
        )
        
        return outputs[0]["generated_text"].strip()

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