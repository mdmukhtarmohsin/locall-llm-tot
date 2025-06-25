# Prompt Engineering Pipeline with Local Ollama LLM

A modular pipeline for structured reasoning tasks (e.g., multi-step math, logic puzzles, code debugging) using Tree-of-Thought (ToT), Self-Consistency aggregation, and automated prompt optimization—all powered by your local Ollama LLM instance.

## Repository Structure

```
├── README.md
├── requirements.txt
├── tasks/
│   └── math_multi_step.json        # Sample domain task definitions (id, problem, answer)
├── prompts/
│   ├── initial_prompts/
│   │   └── math_multi_step_prompt.txt
│   └── optimized_prompts/
│       └── math_multi_step/v1.txt  # Versioned optimized prompts
├── logs/
│   ├── reasoning_paths/            # Per-task reasoning JSON logs
│   │   └── math_multi_step/
│   │       ├── math1.json
│   │       └── math2.json
│   └── optimization/
│       └── math_multi_step/
│           └── opt_2025-06-25T12-00-00.json
├── evaluation/
│   ├── metrics.csv                 # Aggregated metrics per run/version
│   └── reflection.md               # Qualitative analysis and trade-offs
└── src/
    ├── config.py                   # Reads Ollama model settings
    ├── data_loader.py              # Loads tasks from `tasks/`
    ├── utils.py                    # Helpers: JSON I/O, timestamping
    ├── tree_of_thought.py          # Generates N reasoning paths via Ollama sampling
    ├── self_consistency.py         # Aggregates answers by majority vote
    ├── prompt_engineering.py       # Main pipeline runner
    ├── prompt_optimizer.py         # Automated prompt refinement using Ollama
    └── evaluate.py                 # Computes accuracy and appends to metrics
```

## Setup

1. **Install dependencies** (ensure Ollama Python client is installed):

   ```bash
   pip3 install -r requirements.txt
   ```

2. **Pull or serve your Ollama model**:

   ```bash
   ollama pull your_model_name
   ```

3. **Configure environment variables** (optional):

   ```bash
   export OLLAMA_MODEL_NAME=your_model_name
   export OLLAMA_OPTIMIZER_MODEL_NAME=your_optimizer_model_name
   ```

## Usage

### 1. Run the ToT + Self-Consistency Pipeline

Generate multiple reasoning paths and aggregate answers:

```bash
python3 src/prompt_engineering.py \
  --domain math_multi_step \
  --prompt_file prompts/initial_prompts/math_multi_step_prompt.txt \
  --output_dir logs/reasoning_paths/math_multi_step \
  --num_paths 5
```

- `--num_paths`: Number of branches to sample per task (default: 3).
- Outputs per-task JSON logs (`{id}.json`) with fields:

  - `paths`: list of reasoning strings
  - `aggregated_answer`: consensus answer

### 2. Evaluate Results

Compute accuracy and append metrics:

```bash
python3 src/evaluate.py \
  --domain math_multi_step \
  --results_dir logs/reasoning_paths/math_multi_step \
  --metrics_file evaluation/metrics.csv
```

- Creates `evaluation/metrics.csv` if missing.
- Columns: `timestamp`, `domain`, `prompt_version`, `num_tasks`, `accuracy`

### 3. Automated Prompt Optimization

Detect failures and refine prompts via local LLM:

```bash
python3 src/prompt_optimizer.py \
  --domain math_multi_step \
  --prompt_file prompts/initial_prompts/math_multi_step_prompt.txt \
  --results_dir logs/reasoning_paths/math_multi_step \
  --output_prompt_file prompts/optimized_prompts/math_multi_step/v1.txt
```

- Failsafe: If no failures detected, prints a message and exits.
- Saves revised prompt template to the versioned file.
- Logs metadata under `logs/optimization/<domain>/opt_<timestamp>.json`.

### 4. Rerun with Optimized Prompt

Point `prompt_engineering.py` at the optimized prompt:

```bash
python3 src/prompt_engineering.py \
  --domain math_multi_step \
  --prompt_file prompts/optimized_prompts/math_multi_step/v1.txt \
  --output_dir logs/reasoning_paths/math_multi_step/v1
```

Repeat evaluation to measure improvements.

## Evaluation & Reflection

- **Metrics** in `evaluation/metrics.csv`:

  - Task accuracy
  - Prompt version
  - Number of failures

- **Qualitative Notes** in `evaluation/reflection.md`:

  - Coherence and hallucination rates
  - Impact of ToT + Self-Consistency
  - Effectiveness of automated optimization
  - Trade-offs: complexity vs. accuracy vs. compute cost

## Adding New Domains

1. Create `tasks/<domain>.json` with entries `{id, problem, answer}`.
2. Add a prompt template at `prompts/initial_prompts/<domain>_prompt.txt`.
3. Run steps 1–4 replacing `math_multi_step` with your new domain.

---
