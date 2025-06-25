import argparse
import csv
from pathlib import Path
import json
from data_loader import load_tasks

def main():
    parser = argparse.ArgumentParser(description="Evaluate pipeline results")
    parser.add_argument('--domain', type=str, required=True)
    parser.add_argument('--results_dir', type=str, required=True)
    parser.add_argument('--metrics_file', type=str, required=True)
    args = parser.parse_args()
    tasks = load_tasks(args.domain, Path('tasks'))
    results_dir = Path(args.results_dir)
    total = 0
    correct = 0
    rows = []
    for task in tasks:
        task_id = task.get('id')
        truth = str(task.get('answer', '')).strip().lower()
        log_path = results_dir / f"{task_id}.json"
        if not log_path.exists():
            continue
        with open(log_path, 'r', encoding='utf-8') as f:
            entry = json.load(f)
        pred = str(entry.get('aggregated_answer', '')).strip().lower()
        is_correct = (pred == truth)
        total += 1
        if is_correct:
            correct += 1
        rows.append({'domain': args.domain, 'task_id': task_id, 'predicted': pred, 'ground_truth': truth, 'correct': is_correct})
    accuracy = correct / total if total > 0 else 0.0
    metrics_file = Path(args.metrics_file)
    write_header = not metrics_file.exists()
    with open(metrics_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['domain', 'task_id', 'predicted', 'ground_truth', 'correct', 'accuracy_overall'])
        if write_header:
            writer.writeheader()
        for row in rows:
            row_out = row.copy()
            row_out['accuracy_overall'] = accuracy
            writer.writerow(row_out)
    print(f"Evaluation completed for domain {args.domain}: accuracy {accuracy:.2%}")

if __name__ == '__main__':
    main()