from typing import Any, Callable, Optional

from rapidfuzz import fuzz
from rapidfuzz.distance import ScoreAlignment


def fuzzy_search(query: str, field_value: Any) -> tuple[float, ScoreAlignment]:
    field_res = fuzz.partial_ratio_alignment(query, field_value.value)
    field_score = field_res.score if field_res else 0.0
    return field_score, field_res

# Sort matches by highest score
def sort_and_limit_matches(matches: list[Any], limit: int, sort_key: Callable[[Any], float]) -> list[Any]:
    matches.sort(key=sort_key, reverse=True)
    return matches[:limit]
