"""Assignment 13 · Package split: template solution.

The old single-file module, reduced to a shim: existing code that does
`import exercise` / `from exercise import slugify` keeps working, but is told to move on.
"""

import warnings

from wordtools import __version__, slugify, top_words, word_count  # noqa: F401  (re-exported)

warnings.warn(
    "importing from 'exercise' is deprecated; use 'wordtools' instead",
    DeprecationWarning,
    stacklevel=2,           # point the warning at the importing code, not at this line
)

__all__ = ["slugify", "top_words", "word_count"]
