"""Tests for assignment 03. Run: pytest advanced/03-the-data-model/assignments/03-vector -v"""

import pytest


def test_needs_components(ex):
    with pytest.raises(ValueError):
        ex.Vector()


def test_repr_and_str(ex):
    v = ex.Vector(1, 2.5)
    assert repr(v) == "Vector(1, 2.5)"
    assert str(v) == "(1, 2.5)"
    assert repr([ex.Vector(3)]) == "[Vector(3)]"


def test_format(ex):
    v = ex.Vector(1, 2.5)
    assert f"{v:.1f}" == "(1.0, 2.5)"
    assert f"{v:>4}" == "(   1,  2.5)"
    assert f"{v}" == "(1, 2.5)"


def test_len_index_iter_unpack(ex):
    v = ex.Vector(3, 4, 5)
    assert len(v) == 3
    assert (v[0], v[-1]) == (3, 5)
    assert list(v) == [3, 4, 5]
    x, y, z = v
    assert (x, y, z) == (3, 4, 5)


def test_slice_returns_vector(ex):
    part = ex.Vector(1, 2, 3)[1:]
    assert isinstance(part, ex.Vector)
    assert part == ex.Vector(2, 3)


def test_index_out_of_range(ex):
    with pytest.raises(IndexError):
        ex.Vector(1)[1]


def test_equality(ex):
    assert ex.Vector(1, 2) == ex.Vector(1, 2)
    assert ex.Vector(1, 2) != ex.Vector(2, 1)
    assert ex.Vector(1, 2) != ex.Vector(1, 2, 0)


def test_equality_with_other_types_is_false(ex):
    assert ex.Vector(3, 4) != (3, 4)
    assert not ex.Vector(3, 4) == [3, 4]
    assert ex.Vector(1) != None  # noqa: E711


def test_eq_returns_notimplemented(ex):
    assert ex.Vector(1).__eq__("x") is NotImplemented


def test_hash(ex):
    assert hash(ex.Vector(1, 2)) == hash(ex.Vector(1, 2))
    assert len({ex.Vector(1, 2), ex.Vector(1, 2), ex.Vector(2, 1)}) == 2
    assert {ex.Vector(0, 1): "up"}[ex.Vector(0, 1)] == "up"


def test_is_immutable_in_practice(ex):
    v = ex.Vector(1, 2)
    with pytest.raises(TypeError):
        v[0] = 5


def test_add_and_sub(ex):
    assert ex.Vector(3, 4) + ex.Vector(1, 2) == ex.Vector(4, 6)
    assert ex.Vector(3, 4) - ex.Vector(1, 2) == ex.Vector(2, 2)


def test_add_does_not_change_operands(ex):
    v, w = ex.Vector(1, 1), ex.Vector(2, 2)
    v + w
    assert (v, w) == (ex.Vector(1, 1), ex.Vector(2, 2))


@pytest.mark.parametrize("op", ["add", "sub", "matmul"])
def test_length_mismatch(ex, op):
    import operator
    with pytest.raises(ValueError, match="same length"):
        getattr(operator, op)(ex.Vector(1, 2), ex.Vector(1, 2, 3))


@pytest.mark.parametrize("other", [5, (1, 2), "ab"])
def test_add_non_vector_is_type_error(ex, other):
    with pytest.raises(TypeError):
        ex.Vector(1, 2) + other
    with pytest.raises(TypeError):
        other + ex.Vector(1, 2)


def test_scalar_multiplication_both_sides(ex):
    assert ex.Vector(3, 4) * 2 == ex.Vector(6, 8)
    assert 2 * ex.Vector(3, 4) == ex.Vector(6, 8)
    assert 0.5 * ex.Vector(2, 4) == ex.Vector(1.0, 2.0)


def test_division(ex):
    assert ex.Vector(3, 4) / 2 == ex.Vector(1.5, 2.0)


def test_multiply_by_non_number_is_type_error(ex):
    with pytest.raises(TypeError):
        ex.Vector(1, 2) * "x"
    with pytest.raises(TypeError):
        ex.Vector(1, 2) / ex.Vector(1, 2)


def test_dot_product(ex):
    assert ex.Vector(3, 4) @ ex.Vector(1, 2) == 11
    assert ex.Vector(1, 0) @ ex.Vector(0, 1) == 0


def test_neg_abs_bool(ex):
    assert -ex.Vector(1, -2) == ex.Vector(-1, 2)
    assert abs(ex.Vector(3, 4)) == 5.0
    assert isinstance(abs(ex.Vector(3, 4)), float)
    assert abs(ex.Vector(1, 2, 2)) == 3.0
    assert bool(ex.Vector(0, 0)) is False
    assert bool(ex.Vector(0, 0.1)) is True


def test_sum_needs_start_vector(ex):
    vectors = [ex.Vector(1, 1), ex.Vector(2, 2)]
    assert sum(vectors, ex.Vector(0, 0)) == ex.Vector(3, 3)
