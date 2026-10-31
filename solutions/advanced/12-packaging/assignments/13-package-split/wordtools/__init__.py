"""Small tools for words: slugs, counts and frequencies."""

from .stats import top_words
from .text import slugify, word_count

__all__ = ["slugify", "top_words", "word_count"]
__version__ = "1.0.0"
