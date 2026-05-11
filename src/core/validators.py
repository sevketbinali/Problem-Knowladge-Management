"""Validation logic for domain entities and API inputs."""
from pydantic import ValidationError

def validate_problem_description(text: str) -> None:
    """Validate problem description length (20-2000 characters)."""
    length = len(text)
    if not (20 <= length <= 2000):
        raise ValueError(f"Problem description must be between 20 and 2000 characters. Got {length}.")


def validate_step_response(text: str) -> None:
    """Validate step response minimum length (10 characters)."""
    length = len(text)
    if length < 10:
        raise ValueError(f"Step response must be at least 10 characters. Got {length}.")


def validate_search_query(text: str) -> None:
    """Validate search query length (10-500 characters)."""
    length = len(text)
    if not (10 <= length <= 500):
        raise ValueError(f"Search query must be between 10 and 500 characters. Got {length}.")


def validate_lessons_learned(text: str) -> None:
    """Validate lessons learned word count (100-500 words)."""
    words = text.split()
    count = len(words)
    if not (100 <= count <= 500):
        raise ValueError(f"Lessons learned must be between 100 and 500 words. Got {count}.")


def validate_ishikawa_cause(text: str) -> None:
    """Validate Ishikawa cause length (1-500 characters)."""
    length = len(text)
    if not (1 <= length <= 500):
        raise ValueError(f"Ishikawa cause must be between 1 and 500 characters. Got {length}.")
