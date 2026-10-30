# Assignment 11 · Word counter

> **Lesson:** [08 · Dictionaries and sets](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~1 h

## Goal

Analyse a piece of text: which words does it use, how often, and which are the most frequent?
This is the same counting pattern that search engines and spam filters start from.

## What to write

| Function | Returns |
|---|---|
| `words(text)` | a list of the words in `text`: lower case, punctuation `.,!?;:"'()` stripped from both ends, empty pieces dropped |
| `word_counts(text)` | a dict `word → number of times it appears` |
| `most_common(text, n)` | a list of the `n` most frequent `(word, count)` tuples, most frequent first; ties sorted alphabetically |
| `group_by_length(text)` | a dict `length → sorted list of the distinct words with that length` |

## Examples

```python
>>> words("The cat sat. The CAT ran!")
['the', 'cat', 'sat', 'the', 'cat', 'ran']
>>> word_counts("The cat sat. The CAT ran!")
{'the': 2, 'cat': 2, 'sat': 1, 'ran': 1}
>>> most_common("The cat sat. The CAT ran!", 3)
[('cat', 2), ('the', 2), ('ran', 1)]
>>> group_by_length("The cat sat on a mat")
{3: ['cat', 'mat', 'sat', 'the'], 2: ['on'], 1: ['a']}
```

## Hints

<details>
<summary>Hint 1: cleaning words</summary>

`text.lower().split()` splits on whitespace. Then `.strip('.,!?;:"\'()')` removes those characters
from both ends of each piece. A piece like `"--"` or `"!"` becomes `""`; skip it (`if word:`).
</details>

<details>
<summary>Hint 2: counting</summary>

Reuse `words(text)` and the counting pattern from the lesson: `counts[word] = counts.get(word, 0) + 1`.
</details>

<details>
<summary>Hint 3: most frequent first, ties alphabetically</summary>

Sort `counts.items()` with a `key` that returns a tuple. Tuples compare item by item, so
`key=lambda pair: (-pair[1], pair[0])` sorts by count descending (the minus sign flips the order),
and then by word ascending. Then slice `[:n]`.
</details>

<details>
<summary>Hint 4: group_by_length</summary>

Loop over the **distinct** words (`set(words(text))` or the keys of `word_counts`). Use the grouping
pattern. At the end, sort each list.
</details>

## Check your work

```bash
pytest beginner/08-dicts-and-sets/assignments/11-word-counter -v
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/08-dicts-and-sets/assignments/11-word-counter/exercise.py),
then tick off assignment 11 in the [progress checklist](../../../../README.md#progress-checklist).
