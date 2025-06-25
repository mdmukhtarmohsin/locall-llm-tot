import argparse
from pathlib import Path
import json
from tqdm import tqdm
from config import Config
from data_loader import load_tasks
from tree_of_thoughts import generate_reasoning_paths
from self_consistency import aggregate_answers
from utils import parse_answer_from_text, append_json, current_timestamp

def main():
    parser = argparse.ArgumentParser(description="Run prompt-engineering pipeline using Ollama")
    parser.add_argument('--domain', type=str, required=True)
    parser.add_argument('--prompt_file', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--num_paths', type=int, default=5)
    args = parser.parse_args()

    tasks = load_tasks(args.domain, Path('tasks'))
    with open(args.prompt_file, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for item in tqdm(tasks, desc='Tasks'):
        task_id = item.get('id', '')
        problem = item.get('problem', '')
        prompt = prompt_template.replace('{problem}', problem)
        paths = generate_reasoning_paths(prompt, num_paths=args.num_paths)
        answers = [parse_answer_from_text(path) for path in paths]
        aggregated, dist = aggregate_answers(answers)
        log_entry = {
            'timestamp': current_timestamp(),
            'task_id': task_id,
            'problem': problem,
            'paths': paths,
            'parsed_answers': answers,
            'aggregated_answer': aggregated,
            'distribution': dist,
        }
        append_json(log_entry, output_dir / f"{task_id}.json")
    # Save summary metadata
    summary_path = output_dir / 'summary.json'
    summary = {'domain': args.domain, 'timestamp': current_timestamp()}
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Finished. Logs saved to {output_dir}")

if __name__ == '__main__':
    main()