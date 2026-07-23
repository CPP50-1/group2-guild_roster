"""Day 1 shared build: a class with full comparison, equality, repr, and
set support — the "Money class" pattern (currency + amount) from the
program, adapted to the guild domain (an inventory item with a value and
a rarity tier).

Rarity and __init__ are given. Your job is the dunder methods below.
Remember the pairing rule: __eq__ and __hash__ must always be defined
together and stay consistent, or Item becomes unusable in sets/dicts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from functools import total_ordering


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
@dataclass(frozen=True)
class Item:
    """An inventory item, ordered first by rarity then by value.

    @total_ordering fills in the remaining comparison operators once you
    provide __eq__ and __lt__ — you don't need to implement __le__/__gt__/
    __ge__ yourself.
    """

    name: str
    rarity: Rarity
    value: int

    def __str__(self) -> str:
        """
        Human-readable representation of Item
                should look like: Iron Sword (Common, 10g)
        """
        return f"{self.name} ({self.rarity.name.capitalize()}, {self.value}g)"

    def __lt__(self, other: object) -> bool:
        """(Day 1): order by rarity first, then value as a tiebreaker.
        Return NotImplemented if `other` isn't an Item.
        """
        if not isinstance(other, Item):
            return NotImplemented
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
            raise ValueError("Items must have the same name and rarity")

        return Item(self.name, self.rarity, self.value + other.value)

    def __post_init__(self):
        if not self.name:
            raise ValueError("name cannot be empty")

        if self.rarity not in Rarity:
            raise TypeError("rariry is not part of Rariry enum")

        if self.value < 0:
            raise ValueError("value should be supperior to 0")
