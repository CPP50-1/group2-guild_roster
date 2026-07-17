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

from typing import Any, Dict, Iterator, List

from .models import Character


# --- Dev A: OrderedSet ------------------------------------------------------

class OrderedSet:
    """A set that remembers insertion order. Backed by a dict (Python 3.7+
    dicts are insertion-ordered) purely for its keys — this is what gives
    O(1) membership instead of the O(n) a list would need. Use only the
    keys of self._data; never store meaningful values in them.
    """

    def __init__(self, items: Iterator[Any] = ()):
        self._data: Dict[Any, None] = {}
        for item in items:
            self.add(item)

    def add(self, item: Any) -> None:
        """TODO (Day 2): add item, no-op if it's already present."""
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.add")

    def discard(self, item: Any) -> None:
        """TODO (Day 2): remove item if present; do nothing if it isn't."""
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.discard")

    def __contains__(self, item: Any) -> bool:
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.__contains__")

    def __iter__(self) -> Iterator[Any]:
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.__iter__")

    def __len__(self) -> int:
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.__len__")

    def __repr__(self) -> str:
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.__repr__")

    def __eq__(self, other: object) -> bool:
        """TODO (Day 2): two OrderedSets are equal if they contain the
        same items in the same order.
        """
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.__eq__")


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
        """(Day 2): build a cache key from (type name, level,
        difficulty). If it's already in self._cache, increment
        self.cache_hits and return the cached value. Otherwise compute a
        result (any deterministic formula is fine — e.g.
        (character.level * 7 + difficulty * 13) % 100), store it in the
        cache, and return it. Increment self.calls every time this is
        called, regardless of hit or miss.
        """
        self.calls += 1
        key = (character.describe_role(), character.name, character.level, difficulty)

        if key in self._cache:
            self.cache_hits += 1
        else :
            self._cache[key] = int((character.level * 7 + difficulty*13)% 100)
        return self._cache[key]


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
        """(Day 2): an iterator must be iterable (return itself)."""
        return self

    def __next__(self) -> Character:
        """(Day 2): return the next character, advance the index,
        raise StopIteration once you've gone past the end.
        """
        if self._index >= len(self._characters):
            raise StopIteration

        current_character = self._characters[self._index]
        self._index += 1
        return current_character


class Roster:
    """A guild's roster of characters, supporting the full container
    protocol: indexing, assignment, deletion, membership, length, and
    iteration.
    """

    def __init__(self, characters: Iterator[Character] = ()):
        self._characters: List[Character] = list(characters)

    def __getitem__(self, index: int) -> Character:
        return self._characters[index]

    def __setitem__(self, index: int, value: Character) -> None:
        """(Day 2): reject non-Character values with a TypeError."""
        if not isinstance(value, Character):
            raise TypeError(f"{value.__class__.__name__} is not a Character")
        self._characters[index] = value

    def __delitem__(self, index: int) -> None:
        self._characters.remove(self._characters[index])

    def __contains__(self, item: Character) -> bool:
        return item in self._characters

    def __len__(self) -> int:
        return len(self._characters)

    def __iter__(self) -> RosterIterator:
        """(Day 2): return a RosterIterator over this roster's
        characters — this is the connection between the container
        protocol and the from-scratch iterator class above.
        """
        return RosterIterator(self._characters)

    def __repr__(self) -> str:
        first_results = []
        is_bigger_than_five = len(self._characters) > 5
        for i in range(max(5, len(self._characters))):
            first_results.append(self._characters[i])
        first_results = "\n".join(first_results)
        return f"{first_results} and {len(self._characters) - 5} more" if is_bigger_than_five else f"{first_results}"

    def add(self, character: Character) -> None:
        self._characters.append(character)

    def alive_characters(self) -> Iterator[Character]:
        """(Day 2): a generator (use `yield`) that yields only the
        characters that are currently "truthy" (relies on Character's
        __bool__ from Day 1). Compare, once done, how much shorter this
        is than RosterIterator above — same protocol, very different
        amount of code.
        """
        for character in self._characters:
            if character:
                yield character


    def sorted_by_level(self) -> List[Character]:
        """(Day 2): return characters sorted by level. Should need
        no key= argument at all if Character.__lt__ (Day 1) is correct.
        """
        return sorted(self._characters)
