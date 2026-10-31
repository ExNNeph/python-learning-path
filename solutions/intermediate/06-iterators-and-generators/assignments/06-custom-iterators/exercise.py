"""Assignment 06 · Custom iterators: template solution."""

import math

# Unique marker objects. `is` comparison against them can never be confused with a real
# item, not even None, 0 or "".
_EMPTY = object()
_NO_DEFAULT = object()


class Countdown:
    """A single-use iterator: start, start - 1, ..., 1."""

    def __init__(self, start):
        self.current = start

    def __iter__(self):
        # An iterator returns itself, so `for` (which calls iter()) can use it directly.
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


class FloatRange:
    """A reusable iterable: start, start + step, ... while < stop."""

    def __init__(self, start, stop, step=1.0):
        if step <= 0:
            raise ValueError("step must be positive")
        self.start, self.stop, self.step = start, stop, step

    def __len__(self):
        # Count first, then compute each value as start + i * step: no error builds up
        # from adding the step again and again.
        return max(0, math.ceil((self.stop - self.start) / self.step))

    def __iter__(self):
        # A generator method: each call (each `for` loop) returns a NEW generator,
        # which is what makes the range reusable.
        for i in range(len(self)):
            yield float(self.start + i * self.step)


class Peekable:
    """An iterator over any iterable that can look one item ahead with peek()."""

    def __init__(self, iterable):
        self._iterator = iter(iterable)     # works for lists, strings, files, generators ...
        self._buffer = _EMPTY

    def __iter__(self):
        return self

    def __next__(self):
        if self._buffer is not _EMPTY:      # an item was peeked: hand it out first
            item, self._buffer = self._buffer, _EMPTY
            return item
        return next(self._iterator)         # StopIteration passes through unchanged

    def peek(self, default=_NO_DEFAULT):
        """Return the next item without consuming it."""
        if self._buffer is _EMPTY:
            try:
                self._buffer = next(self._iterator)
            except StopIteration:
                # The marker default lets us tell "no default" apart from peek(None).
                if default is _NO_DEFAULT:
                    raise
                return default
        return self._buffer


if __name__ == "__main__":
    print(list(Countdown(5)))
    print(list(FloatRange(0, 2, 0.25)))
    words = Peekable(["the", "quick", "brown", "fox"])
    for word in words:
        print(word, "→ next:", words.peek(None))
