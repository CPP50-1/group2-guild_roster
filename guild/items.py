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
        """
        Unambiguous, reconstructable representation of Item.
            should look like: Item(name='Iron Sword', rarity=COMMON, value=10)
        """
        return f"{self.__class__.__name__}(name={self.name!r}, rarity={self.rarity.name}, value={self.value})"

    def __str__(self) -> str:
        """
        Human-readable representation of Item
                should look like: Iron Sword (Common, 10g)
        """
        return f"{self.name} ({self.rarity.name.capitalize()}, {self.value}g)"

    def __eq__(self, other: object) -> bool:
        """(Day 1): two Items are equal when name, rarity AND value
        all match. Remember to return NotImplemented (not False) if
        `other` isn't an Item.
        """
        if not isinstance(other, Item):
            raise TypeError("Non Items comparison not implemented")
        return self.rarity == other.rarity and self.value == other.value and self.name == other.name

    def __hash__(self) -> int:
        """(Day 1): must stay consistent with __eq__ above — equal
        Items must hash equal, or sets/dicts of Item will misbehave.
        """
        return hash((self.name, self.rarity, self.value))

    def __lt__(self, other: object) -> bool:
        """(Day 1): order by rarity first, then value as a tiebreaker.
        Return NotImplemented if `other` isn't an Item.
        """
        if not isinstance(other, Item):
            raise TypeError(f"{other.__class__.__name__} is not a {self.__class__.__name__}")
        return (self.rarity, self.value) < (self.rarity, other.value)

    def __bool__(self) -> bool:
        """(Day 1): an Item is "truthy" if it has any value at all —
        a zero-value junk item should be falsy.
        """
        # Consider self.value != 0 if negative values need to be treated as truthy.
        return self.value > 0

    def __add__(self, other: object) -> Item:
        """(Day 1 bonus) Add __add__ to Item: combining two Items should only be valid if
        they share the same name and rarity (i.e. they're stackable copies of
        the same item), in that case, return a new Item with the same name/
        rarity and value summed. Combining items with different name/rarity
        should raise TypeError, not silently produce nonsense.
        """
        if not isinstance(other, Item):
            raise TypeError("Non Items additions not implemented")

        if self.rarity != other.rarity or self.name != other.name:
            raise  ValueError("Items must have the same name and rarity")

        return Item(self.name, self.rarity, self.value+other.value)


