from typing import Any, Optional

from rapidfuzz import fuzz
from rapidfuzz.distance import ScoreAlignment


def fuzzy_search(query: str, field_value: str) -> tuple[float, ScoreAlignment]:
    field_res = fuzz.partial_ratio_alignment(query, value.value)
    name_score = field_res.score if field_res else 0.0
    return name_score, field_res

# Sort matches by highest score
def sort_and_limit_matches(matches: list[Any], limit: int) -> list[Any]:
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:limit]
