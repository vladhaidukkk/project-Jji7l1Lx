from typing import Any, Callable

from bot.common import Field
from rapidfuzz import fuzz
from rapidfuzz.distance import ScoreAlignment

def extract_score(field_res: ScoreAlignment) -> float:
    """Extract the numeric score from a ScoreAlignment result.

    Args:
        field_res: The alignment result returned by a rapidfuzz comparison.

    Returns:
        The score value if ``field_res`` is not None, otherwise ``0.0``.
    """
    return field_res.score if field_res else 0.0

def fuzzy_search(query: str, field_value: Field | list[Field] | str) -> tuple[float, ScoreAlignment | None]:
    """Perform a fuzzy partial-ratio search of *query* against a field value.

    When *field_value* is a list, every element is compared and the highest
    scoring match is returned.

    Args:
        query: The search string to look for.
        field_value: A single :class:`~bot.common.Field`, a list of
            :class:`~bot.common.Field` objects, or a plain string to search
            within.

    Returns:
        A tuple of ``(score, alignment)`` where *score* is a float in the range
        ``[0, 100]`` and *alignment* is the corresponding
        :class:`~rapidfuzz.distance.ScoreAlignment` object, or ``None`` if no
        comparison could be performed.
    """
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
    """Sort *matches* by score in descending order and return at most *limit* items.

    Args:
        matches: The list of match objects to sort.
        limit: Maximum number of items to return.
        sort_key: A callable that accepts a match object and returns a float
            score used for ordering.

    Returns:
        A sorted, length-limited list of match objects.
    """
    matches.sort(key=sort_key, reverse=True)
    return matches[:limit]
