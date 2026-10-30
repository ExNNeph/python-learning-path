"""Tests for assignment 12. Run: pytest beginner/08-dicts-and-sets/assignments/12-common-friends -v"""

import copy

import pytest


@pytest.fixture
def network():
    return {
        "ada": {"grace", "linus", "guido"},
        "grace": {"ada", "guido", "ken"},
        "linus": {"ada"},
        "guido": {"ada", "grace"},
        "ken": {"grace", "barbara"},
    }


def test_mutual_friends(ex, network):
    assert ex.mutual_friends(network, "ada", "grace") == {"guido"}


def test_mutual_friends_none(ex, network):
    assert ex.mutual_friends(network, "linus", "ken") == set()


def test_mutual_friends_unknown_person(ex, network):
    assert ex.mutual_friends(network, "ada", "nobody") == set()


def test_suggestions(ex, network):
    assert ex.suggestions(network, "linus") == {"grace", "guido"}


def test_suggestions_excludes_self_and_friends(ex, network):
    assert ex.suggestions(network, "ada") == {"ken"}


def test_suggestions_for_person_without_entry(ex, network):
    assert ex.suggestions(network, "barbara") == set()


def test_everyone(ex, network):
    assert ex.everyone(network) == {"ada", "barbara", "grace", "guido", "ken", "linus"}


def test_everyone_empty(ex):
    assert ex.everyone({}) == set()


def test_is_mutual_false(ex, network):
    assert ex.is_mutual(network) is False


def test_is_mutual_true(ex):
    assert ex.is_mutual({"a": {"b"}, "b": {"a", "c"}, "c": {"b"}}) is True


def test_is_mutual_one_sided(ex):
    assert ex.is_mutual({"a": {"b"}, "b": set()}) is False


def test_network_is_not_changed(ex, network):
    before = copy.deepcopy(network)
    ex.mutual_friends(network, "ada", "grace")
    ex.suggestions(network, "linus")
    ex.everyone(network)
    ex.is_mutual(network)
    assert network == before
