from collections import Counter
from typing import List, Tuple

def aggregate_answers(answer_list: List[str]) -> Tuple[str, dict]:
    counter = Counter(answer_list)
    if not counter:
        return '', {}
    most_common, freq = counter.most_common(1)[0]
    return most_common, dict(counter)