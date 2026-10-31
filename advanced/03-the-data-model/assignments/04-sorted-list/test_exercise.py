"""Tests for assignment 04. Run: pytest advanced/03-the-data-model/assignments/04-sorted-list -v"""

import random

import pytest


def test_sorts_on_creation(ex):
    assert list(ex.SortedList([5, 1, 4])) == [1, 4, 5]
    assert list(ex.SortedList()) == []


def test_add_keeps_order(ex):
    s = ex.SortedList([5, 1, 4])
    for item in (3, 0, 9, 4):
        s.add(item)
    assert list(s) == [0, 1, 3, 4, 4, 5, 9]


def test_add_returns_none(ex):
    assert ex.SortedList().add(1) is None


def test_random_adds_stay_sorted(ex):
    rng = random.Random(7)
    numbers = [rng.randint(-50, 50) for _ in range(300)]
    s = ex.SortedList()
    for n in numbers:
        s.add(n)
    assert list(s) == sorted(numbers)


def test_repr(ex):
    assert repr(ex.SortedList([3, 1, 2])) == "SortedList([1, 2, 3])"
    assert repr(ex.SortedList(["b", "a"])) == "SortedList(['a', 'b'])"


def test_len_and_bool(ex):
    assert len(ex.SortedList([3, 1])) == 2
    assert not ex.SortedList()
    assert ex.SortedList([0])


def test_indexing(ex):
    s = ex.SortedList([30, 10, 20])
    assert (s[0], s[1], s[-1]) == (10, 20, 30)
    with pytest.raises(IndexError):
        s[3]


def test_slicing_returns_sorted_list(ex):
    s = ex.SortedList([5, 1, 4, 3])
    part = s[1:3]
    assert isinstance(part, ex.SortedList)
    assert list(part) == [3, 4]
    assert list(s[::-1]) == [1, 3, 4, 5]   # still sorted: a SortedList can only be sorted


def test_contains(ex):
    s = ex.SortedList([5, 1, 4])
    assert 4 in s
    assert 2 not in s
    assert 99 not in s
    assert 4 in ex.SortedList([4])
    assert 1 not in ex.SortedList()


def test_contains_uses_binary_search(ex):
    s = ex.SortedList(range(100_000))
    comparisons = []

    class Spy(int):
        # an int that counts how often it is compared with ==; a linear scan would need ~77 000
        def __eq__(self, other):
            comparisons.append(1)
            return int(self) == other
        __hash__ = int.__hash__

    assert Spy(77_777) in s
    assert len(comparisons) < 50


def test_iter_and_reversed(ex):
    s = ex.SortedList([2, 3, 1])
    assert list(iter(s)) == [1, 2, 3]
    assert list(reversed(s)) == [3, 2, 1]


def test_remove(ex):
    s = ex.SortedList([3, 1, 3, 2])
    s.remove(3)
    assert list(s) == [1, 2, 3]
    with pytest.raises(ValueError):
        s.remove(42)


def test_index_and_count(ex):
    s = ex.SortedList([4, 1, 4, 2, 4])
    assert s.index(4) == 2
    assert s.count(4) == 3
    assert s.count(7) == 0
    with pytest.raises(ValueError):
        s.index(7)


def test_equality(ex):
    assert ex.SortedList([2, 1]) == ex.SortedList([1, 2])
    assert ex.SortedList([1]) != ex.SortedList([1, 1])
    assert ex.SortedList([1, 2]) != [1, 2]
    assert ex.SortedList([1]).__eq__([1]) is NotImplemented


def test_add_operator(ex):
    a = ex.SortedList([1, 5])
    result = a + ex.SortedList([3])
    assert result == ex.SortedList([1, 3, 5])
    assert list(a + [2, 6]) == [1, 2, 5, 6]
    assert list(a) == [1, 5]


def test_no_item_assignment(ex):
    s = ex.SortedList([1, 2])
    with pytest.raises(TypeError):
        s[0] = 10


def test_key(ex):
    words = ex.SortedList(["pear", "fig", "banana"], key=len)
    assert list(words) == ["fig", "pear", "banana"]
    words.add("kiwi")
    assert list(words) == ["fig", "pear", "kiwi", "banana"]
    assert repr(words) == "SortedList(['fig', 'pear', 'kiwi', 'banana'])"


def test_key_contains_compares_items_not_keys(ex):
    words = ex.SortedList(["fig", "pear"], key=len)
    assert "fig" in words
    assert "bar" not in words          # same length as "fig", but a different word
    assert words.count("fig") == 1
    with pytest.raises(ValueError):
        words.remove("bar")


def test_key_is_kept_by_slices_and_add(ex):
    words = ex.SortedList(["ccc", "a", "bb"], key=len)
    part = words[:2]
    part.add("dddd")
    part.add("")
    assert list(part) == ["", "a", "bb", "dddd"]
    combined = words + ["zz"]
    assert list(combined) == ["a", "bb", "zz", "ccc"]


def test_key_descending(ex):
    s = ex.SortedList([1, 3, 2], key=lambda n: -n)
    s.add(5)
    assert list(s) == [5, 3, 2, 1]
    assert 2 in s and 4 not in s
