"""Day 1 shared build: a class with full comparison, equality, repr, and
set support — the "Money class" pattern (currency + amount) from the
program, adapted to the guild domain (an inventory item with a value and
a rarity tier).

Rarity and __init__ are given. Your job is the dunder methods below.
Remember the pairing rule: __eq__ and __hash__ must always be defined
together and stay consistent, or Item becomes unusable in sets/dicts.
"""
from __future__ import annotations

from functools import total_ordering
from enum import IntEnum


class Rarity(IntEnum):
    """IntEnum so rarities compare naturally (COMMON < RARE < LEGENDARY)
    without any extra work — this is used by Item.__lt__ below.
    """
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5


@total_ordering
class Item:
    """An inventory item, ordered first by rarity then by value.

    @total_ordering fills in the remaining comparison operators once you
    provide __eq__ and __lt__ — you don't need to implement __le__/__gt__/
    __ge__ yourself.
    """

    def __init__(self, name: str, rarity: Rarity, value: int):
        self.name = name
        self.rarity = rarity
        self.value = value

    def __repr__(self) -> str:
        """TODO (Day 1): an unambiguous, reconstructable representation —
        should look like: Item(name='Iron Sword', rarity=COMMON, value=10)
        """
        raise NotImplementedError("TODO (Day 1): implement __repr__")

    def __str__(self) -> str:
        """TODO (Day 1): a human-readable line — should look like:
        Iron Sword (Common, 10g)
        Think about why this differs from __repr__ and when each is used.
        """
        raise NotImplementedError("TODO (Day 1): implement __str__")

    def __eq__(self, other: object) -> bool:
        """
        Will compare name, rarity and value between two Items
        """
        if not isinstance(other, Item):
            raise NotImplementedError("Non Items comparison not implemented")
        return self.name == other.name and self.rarity == other.rarity and self.value == other.value

    def __hash__(self) -> int:
        """
        Will hash Item using name, rarity and value
        """
        return hash((self.name, self.rarity, self.value))

    def __lt__(self, other: object) -> bool:
        """TODO (Day 1): order by rarity first, then value as a tiebreaker.
        Return NotImplemented if `other` isn't an Item.
        """
        raise NotImplementedError("TODO (Day 1): implement __lt__")

    def __bool__(self) -> bool:
        """TODO (Day 1): an Item is "truthy" if it has any value at all —
        a zero-value junk item should be falsy.
        """
        raise NotImplementedError("TODO (Day 1): implement __bool__")
