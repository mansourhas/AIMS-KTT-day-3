
# My Friendly Math Tutor

Adaptive multilingual numeracy tutor for early learners (P1-P3), built for the AIMS KTT challenge.

The project combines:
- Curriculum and synthetic asset generation
- Bayesian Knowledge Tracing (BKT) for adaptation
- Speech recognition + fuzzy answer matching
- Socratic feedback (real LLM or mock)
- Gradio demo UI

## What This Repo Contains

- `scripts/`: data and asset generation scripts
- `src/`: core runtime logic (ASR, BKT, tutor, UI)
- `dataset/seeds/`: provided seed data
- `dataset/generated/`: generated curriculum, visuals, synthetic audio, KT logs
- `kt_eval.ipynb`: BKT vs Elo evaluation notebook
- `process_log.md`: timeline and AI-usage documentation
- `SIGNED.md`: honor code declaration

## Architecture Overview

### 1) Adaptive Engine (`src/bkt_engine.py`)
- Implements Bayesian Knowledge Tracing over 5 skills:
	- counting
	- addition
	- subtraction
	- number_sense
	- word_problem
- Tracks per-skill mastery and serves next questions near the learner's zone of proximal development.
- Supports age-band filtering (`5-6`, `6-7`, `7-8`, `8-9`).

### 2) ASR + Grading (`src/asr_pipeline.py`)
- Uses `openai/whisper-tiny` through `transformers.pipeline`.
- Normalizes transcript/target text and grades with fuzzy matching (`difflib.SequenceMatcher`, threshold 0.75).
- Includes a batch test mode against `dataset/seeds/child_utt_sample_seed.csv`.

### 3) Socratic Feedback
- `src/socratic_tutor.py`: real local LLM path using `microsoft/Phi-3-mini-4k-instruct` in 4-bit (`bitsandbytes`).
- `src/mock_socratic_tutor.py`: lightweight mock tutor for fast demo/testing.

### 4) Demo UI (`src/gradio_ui.py`)
- Child-friendly Gradio workflow with:
	- age-band selection
	- language selection (`en`, `fr`, `kin`)
	- image + audio question prompt
	- microphone or text answer input
	- tutor feedback + next question loop

## Setup

Use Python 3.10+ (3.13 recommended).

```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirment.txt
```

Notes:
- `bitsandbytes` is only needed for real LLM mode (`src/socratic_tutor.py`). and it doesn't support windows properly.

## Quick Start

If generated assets already exist in `dataset/generated/`, launch directly:

```bash
python src/gradio_ui.py
```

## Full Reproducible Pipeline

Run from project root in this order:

1. Generate expanded curriculum
```bash
python scripts/generate_curriculum.py
```

2. Generate visuals
```bash
python scripts/generate_visuals.py
```

3. Generate synthetic question audio (choose one)
```bash
# Fast path (gTTS for en/fr and sw fallback for kin)
python scripts/make_synthetic_child.py

# Higher-quality Kinyarwanda path (Meta MMS kin model)
python scripts/make_synthetic_child_mm.py
```

4. Link audio paths into curriculum metadata
```bash
python scripts/link_audio.py
```

5. Generate KT interaction logs for evaluation
```bash
python scripts/generate_kt_logs.py
```

6. Launch demo UI
```bash
python src/gradio_ui.py
```

## Evaluation

Open and run:
- `kt_eval.ipynb`

The notebook compares:
- Elo baseline predictions
- BKT predictions

Using:
- `dataset/generated/kt_interaction_logs.csv`

## Useful Test Commands

Batch-test ASR on seed utterances:
```bash
python scripts/mock_child_audio.py
python src/asr_pipeline.py
```

Smoke-test BKT engine:
```bash
python src/bkt_engine.py
```

Smoke-test Socratic tutor (real LLM mode):
```bash
python src/socratic_tutor.py
```

## Current Demo Behavior (Important)

- The Gradio app currently imports `mock_socratic_tutor` by default for low-latency demo behavior.
- In `process_answer`, microphone input is placeholder-handled unless text is provided; full ASR integration in the UI loop is not wired by default.
- ASR is implemented separately in `src/asr_pipeline.py` and can be integrated into UI if needed.

## Project Deliverables

- Curriculum generation: `scripts/generate_curriculum.py`
- Visual grounding assets: `scripts/generate_visuals.py`
- Synthetic child-like audio: `scripts/make_synthetic_child.py`, `scripts/make_synthetic_child_mm.py`
- Adaptive logic (BKT): `src/bkt_engine.py`
- ASR + fuzzy grading: `src/asr_pipeline.py`
- Demo app: `src/gradio_ui.py`
- KT evaluation notebook: `kt_eval.ipynb`
- Process log: `process_log.md`
- Honor code: `SIGNED.md`
- shows the tutor working on colab `KTT day3.ipynb`
- genarate the report for the gardains `generate_report.py`
- for the gernerat report sample `reports/repor.pdf`

## License / Submission Note

Prepared as a hackathon/evaluation project submission. See `SIGNED.md` for declaration and `process_log.md` for development log.