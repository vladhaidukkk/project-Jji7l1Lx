from typing import Any, Callable

from bot.common import Field
from rapidfuzz import fuzz
from rapidfuzz.distance import ScoreAlignment

def extract_score(field_res: ScoreAlignment) -> float:
    return field_res.score if field_res else 0.0

def fuzzy_search(query: str, field_value: Field | list[Field] | str) -> tuple[float, ScoreAlignment | None]:
    if type(field_value) is list:
        max_score = 0.0
        max_res: ScoreAlignment | None = None
        for field in field_value:
            current_res = fuzz.partial_ratio_alignment(query, field.value)
            current_score = extract_score(current_res)
            if current_score > max_score:
                max_score = current_score
                max_res = current_res
    else:
        if type(field_value) is str:
            max_res = fuzz.partial_ratio_alignment(query, field_value)
            max_score = extract_score(max_res)
        elif isinstance(field_value, Field):
            max_res = fuzz.partial_ratio_alignment(query, field_value.value)
            max_score =extract_score(max_res)
        else:
            return (0.0, None)

    return (max_score, max_res)

# Sort matches by highest score
def sort_and_limit_matches(matches: list[Any], limit: int, sort_key: Callable[[Any], float]) -> list[Any]:
    matches.sort(key=sort_key, reverse=True)
    return matches[:limit]
