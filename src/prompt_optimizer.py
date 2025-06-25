import argparse
import json
from pathlib import Path
import ollama
from config import Config
from utils import save_json, current_timestamp
from data_loader import load_tasks

def identify_failures(results_dir: Path, tasks):
    failures = []
    for task in tasks:
        task_id = task.get('id')
        truth = str(task.get('answer', '')).strip()
        log_path = results_dir / f"{task_id}.json"
        if not log_path.exists():
            continue
        with open(log_path, 'r', encoding='utf-8') as f:
            entry = json.load(f)
        pred = str(entry.get('aggregated_answer', '')).strip()
        if pred.lower() != truth.lower():
            failures.append({
                'task_id': task_id,
                'problem': task.get('problem'),
                'ground_truth': truth,
                'predicted': pred,
                'paths': entry.get('paths', []),
            })
    return failures

def construct_optimizer_prompt(failures, current_prompt_text, max_cases=5):
    prompt = (
        "You are a prompt engineering assistant. The current prompt template is below. "
        "It is used to solve structured reasoning tasks, but some cases have failed. "
        "Suggest refinements or additional few-shot examples to improve correctness."
        "\n\nCurrent prompt template:\n```" + current_prompt_text + "```\n\n"
    )
    if failures:
        prompt += "Here are example failures (problem, ground truth, prediction, reasoning paths):\n"
        for case in failures[:max_cases]:
            prompt += f"\nProblem: {case['problem']}"
            prompt += f"\nGround Truth: {case['ground_truth']}"
            prompt += f"\nPredicted: {case['predicted']}"
            prompt += "\nReasoning Paths:\n"
            for path in case['paths']:
                prompt += "- ```" + path.replace('```', "```") + "```\n"
            prompt += "\n"
    prompt += "Provide a revised prompt template, clearly indicating placeholders (e.g., {problem})."
    return prompt

def optimize_prompt(domain: str, prompt_file: Path, failures, output_prompt_file: Path):
    model_name = 'gemma3:4b-it-qat'
    if not model_name:
        raise ValueError("OLLAMA_OPTIMIZER_MODEL_NAME not set in environment.")
    current_text = prompt_file.read_text(encoding='utf-8')
    opt_prompt = construct_optimizer_prompt(failures, current_text)
    try:
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': opt_prompt}],
        )
        if hasattr(response, 'message') and hasattr(response.message, 'content'):
            new_prompt = response.message.content.strip()
        elif isinstance(response, dict) and 'message' in response and 'content' in response['message']:
            new_prompt = response['message']['content'].strip()
        else:
            new_prompt = str(response).strip()
    except Exception as e:
        raise RuntimeError(f"Ollama prompt optimization error: {e}")
    output_prompt_file.parent.mkdir(parents=True, exist_ok=True)
    output_prompt_file.write_text(new_prompt, encoding='utf-8')
    log = {
        'timestamp': current_timestamp(),
        'domain': domain,
        'input_prompt_file': str(prompt_file),
        'output_prompt_file': str(output_prompt_file),
        'failures_sample_count': len(failures),
        'new_prompt_excerpt': new_prompt[:200] + '...' if len(new_prompt) > 200 else new_prompt,
    }
    log_dir = Path('logs/optimization') / domain
    log_dir.mkdir(parents=True, exist_ok=True)
    save_json(log, log_dir / f"opt_{current_timestamp().replace(':','-')}.json")
    print(f"Saved optimized prompt to {output_prompt_file}")

def main():
    parser = argparse.ArgumentParser(description="Prompt optimizer using Ollama")
    parser.add_argument('--domain', type=str, required=True)
    parser.add_argument('--prompt_file', type=str, required=True)
    parser.add_argument('--results_dir', type=str, required=True)
    parser.add_argument('--output_prompt_file', type=str, required=True)
    args = parser.parse_args()
    tasks = load_tasks(args.domain, Path('tasks'))
    failures = identify_failures(Path(args.results_dir), tasks)
    if not failures:
        print("No failures detected; prompt may not need optimization.")
        return
    optimize_prompt(args.domain, Path(args.prompt_file), failures, Path(args.output_prompt_file))

if __name__ == '__main__':
    main()