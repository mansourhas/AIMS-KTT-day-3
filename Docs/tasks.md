Here is a clear, grouped checklist of the required tasks based on the hackathon brief. 

### 1. Data & Curriculum Setup
* [cite_start]**Author the Curriculum:** Create a full curriculum of at least 60 items using the provided JSON schema and the 5 sub-skills[cite: 28].
* [cite_start]**Generate Child Audio:** Create child-voiced utterances by pitch-shifting the provided audio datasets (+3 to +6 semitones) and applying classroom noise from MUSAN[cite: 32].
* [cite_start]**Pre-render TTS:** Render Text-to-Speech lines locally using Coqui-TTS or Piper TTS and cache them to the disk (this cache does not count towards the footprint limit)[cite: 29, 30].

### 2. Core Machine Learning & Models
* [cite_start]**Language Model Fine-tuning:** Fine-tune a small LLM with QLORA / LORA adapters on a numeracy instruction set[cite: 37]. 
* [cite_start]**LLM Quantization:** Merge the adapters and quantize the model to int4 (using GGUF or AWQ)[cite: 38].
* [cite_start]**Knowledge Tracing:** Implement Bayesian Knowledge Tracing (BKT) or Deep Knowledge Tracing (DKT) with a tiny GRU[cite: 35]. 
* [cite_start]**KT Evaluation:** Compare the KT model against an Elo-style baseline on a held-out replay and report the AUC[cite: 36].
* [cite_start]**Multilingual ASR:** Implement detection for Kinyarwanda, French, English, or mixed responses[cite: 39]. [cite_start]The system must reply in the dominant language and embed the secondary language for number words if the child code-switches[cite: 39, 40].
* [cite_start]**Visual Grounding:** Create at least one item type requiring the model to count objects in an image (e.g., using `owlvit-tiny` or a hand-crafted baseline)[cite: 41, 42].

### 3. Application Pipeline & Infrastructure
* [cite_start]**Inference Pipeline:** Build the end-to-end on-device pipeline handling visual/audio presentation, tap/voice responses, scoring, and localized audio feedback[cite: 33].
* [cite_start]**Database Integration:** Set up an encrypted local SQLite database for progress tracking[cite: 43]. 
* [cite_start]**Privacy Sync:** Implement upstream data syncing using differential privacy on aggregated stats[cite: 44].
* [cite_start]**Optimize Constraints:** Ensure the app footprint stays strictly at or below 75 MB (excluding TTS cache)[cite: 45]. [cite_start]Optimize for a latency target of under 2.5 seconds per cycle on a CPU[cite: 34].

### 4. Product Adaptation & UX Design
* [cite_start]**First-Time UX:** Design the very first 90 seconds of the app for a 6-year-old opening it for the first time, including what happens if they remain silent[cite: 91, 92, 93].
* [cite_start]**Deployment Model:** Propose how a low-cost Android tablet can be shared across 3 children at a community center, detailing user switching, privacy, and reboot degradation[cite: 97, 98].
* [cite_start]**Parent Report Design:** Design a weekly 1-page report that a non-literate parent can understand in 60 seconds (using icons, simple bars, or voiced summaries)[cite: 99].
* [cite_start]**Stretch Goal (Optional):** Add a dyscalculia early-warning system that prompts parents to talk to a teacher if the learner plateaus[cite: 102].

### 5. Mandatory Code Deliverables & Hosting
* [cite_start]**The App (`demo.py`):** Build a child-facing Gradio demo with microphone input[cite: 49].
* [cite_start]**The Package (`tutor/`):** Create the Python package containing your model, curriculum loader, and adaptive logic[cite: 48].
* [cite_start]**Reporting Scripts:** Write `parent_report.py` to generate the weekly 1-pager[cite: 50]. [cite_start]Create `footprint_report.md` showing the live size of your components[cite: 51].
* [cite_start]**Evaluation Notebook:** Provide `kt_eval.ipynb` showing your knowledge-tracing AUC evaluation[cite: 52].
* [cite_start]**Process Documentation:** Complete `process_log.md` detailing your hour-by-hour timeline, LLM tool usage, prompts used/discarded, and your hardest decision[cite: 53, 114].
* [cite_start]**Honor Code:** Create a `SIGNED.md` file at the root of your repo with your name, date, and the copied honor code text[cite: 75, 81].
* [cite_start]**Hosting:** Push all code to a public GitHub/GitLab repository[cite: 69]. [cite_start]Host models on Hugging Face, Ollama, or Drive[cite: 71, 72]. [cite_start]Ensure data generation scripts are in the repo[cite: 73].