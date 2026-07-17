"""Day 2 workshop targets, one per developer:

    Dev A -> OrderedSet      (custom unique-item structure)
    Dev B -> StatCalculator  (memoized callable, state held between calls)
    Dev C -> Roster          (full container protocol + iterator protocol
                              from scratch, i.e. __iter__ returning a real
                              iterator object with __next__, not a generator)

Constructors that just store their arguments are given; the actual
protocol methods are TODOs.
"""
from __future__ import annotations

from typing import Dict, Iterator, List

from .models import Character


# --- Dev A: OrderedSet ------------------------------------------------------

class OrderedSet:
    """A set that remembers insertion order. Backed by a dict (Python 3.7+
    dicts are insertion-ordered) purely for its keys — this is what gives
    O(1) membership instead of the O(n) a list would need. Use only the
    keys of self._data; never store meaningful values in them.
    """

    def __init__(self, items: Iterator[any] = ()):
        self._data: dict[any, None] = {}
        for item in items:
            self.add(item)

    def add(self, item: any) -> None:
        """(Day 2): add item, no-op if it's already present."""
        if item in self:
            return

        self._data[item] = None

    def discard(self, item: any) -> None:
        """(Day 2): remove item if present; do nothing if it isn't."""
        if item not in self:
            return

        self._data.pop(item)

    def __contains__(self, item: any) -> bool:
        return item in self._data

    def __iter__(self) -> Iterator[any]:
        # Delegates to dict's ordered keys via yields
        yield from self._data

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"OrderedSet([{', '.join(repr(item) for item in self)}])"

    def __eq__(self, other: object) -> bool:
        """(Day 2): two OrderedSets are equal if they contain the
        same items in the same order.
        """
        if not isinstance(other, Iterator[any]):
            return False

        if len(self) != len(other):
            return False

        # early out on first missmatch
        return all(a == b for a, b in zip(self, other))

    def __or__(self, other: OrderedSet) -> OrderedSet:
        result = OrderedSet()
        # Adding common items first, then self's, then other's.
        for item in self:
            if item in other:
                result.add(item)

        for item in self:
            result.add(item)

        for item in other:
            result.add(item)

        return result

    def __and__(self, other: OrderedSet) -> OrderedSet:
        result = OrderedSet()
        for item in self:
            if item in other:
                result.add(item)
        return result

    def __sub__(self, other: OrderedSet) -> OrderedSet:
        result = OrderedSet()
        for item in self:
            if item not in other:
                result.add(item)
        return result



# --- Dev B: memoized callable ------------------------------------------------

class StatCalculator:
    """A callable object that caches results by argument, for an
    expensive/derived stat computation.
    """

    def __init__(self):
        self._cache: Dict[tuple, int] = {}
        self.calls = 0
        self.cache_hits = 0

    def __call__(self, character: Character, difficulty: int) -> int:
        """TODO (Day 2): build a cache key from (type name, level,
        difficulty). If it's already in self._cache, increment
        self.cache_hits and return the cached value. Otherwise compute a
        result (any deterministic formula is fine — e.g.
        (character.level * 7 + difficulty * 13) % 100), store it in the
        cache, and return it. Increment self.calls every time this is
        called, regardless of hit or miss.
        """
        raise NotImplementedError("TODO (Day 2): implement StatCalculator.__call__")


# --- Dev C: full container protocol + iterator protocol from scratch -------

class RosterIterator:
    """A standalone iterator object for Roster, built from scratch rather
    than via a generator function — this is what Day 2's "__iter__ and
    __next__ from scratch" specifically asks for.
    """

    def __init__(self, characters: List[Character]):
        self._characters = characters
        self._index = 0

    def __iter__(self) -> "RosterIterator":
        """TODO (Day 2): an iterator must be iterable (return itself)."""
        raise NotImplementedError("TODO (Day 2): implement RosterIterator.__iter__")

    def __next__(self) -> Character:
        """TODO (Day 2): return the next character, advance the index,
        raise StopIteration once you've gone past the end.
        """
        raise NotImplementedError("TODO (Day 2): implement RosterIterator.__next__")


class Roster:
    """A guild's roster of characters, supporting the full container
    protocol: indexing, assignment, deletion, membership, length, and
    iteration.
    """

    def __init__(self, characters: Iterator[Character] = ()):
        self._characters: List[Character] = list(characters)

    def __getitem__(self, index: int) -> Character:
        raise NotImplementedError("TODO (Day 2): implement Roster.__getitem__")

    def __setitem__(self, index: int, value: Character) -> None:
        """TODO (Day 2): reject non-Character values with a TypeError."""
        raise NotImplementedError("TODO (Day 2): implement Roster.__setitem__")

    def __delitem__(self, index: int) -> None:
        raise NotImplementedError("TODO (Day 2): implement Roster.__delitem__")

    def __contains__(self, item: Character) -> bool:
        raise NotImplementedError("TODO (Day 2): implement Roster.__contains__")

    def __len__(self) -> int:
        raise NotImplementedError("TODO (Day 2): implement Roster.__len__")

    def __iter__(self) -> RosterIterator:
        """TODO (Day 2): return a RosterIterator over this roster's
        characters — this is the connection between the container
        protocol and the from-scratch iterator class above.
        """
        raise NotImplementedError("TODO (Day 2): implement Roster.__iter__")

    def __repr__(self) -> str:
        raise NotImplementedError("TODO (Day 2): implement Roster.__repr__")

    def add(self, character: Character) -> None:
        raise NotImplementedError("TODO (Day 2): implement Roster.add")

    def alive_characters(self) -> Iterator[Character]:
        """TODO (Day 2): a generator (use `yield`) that yields only the
        characters that are currently "truthy" (relies on Character's
        __bool__ from Day 1). Compare, once done, how much shorter this
        is than RosterIterator above — same protocol, very different
        amount of code.
        """
        raise NotImplementedError("TODO (Day 2): implement Roster.alive_characters")

    def sorted_by_level(self) -> List[Character]:
        """TODO (Day 2): return characters sorted by level. Should need
        no key= argument at all if Character.__lt__ (Day 1) is correct.
        """
        raise NotImplementedError("TODO (Day 2): implement Roster.sorted_by_level")
