"""The core Character model.

Three separate TODOs live in this file, for three different days — read
the notes at each one carefully, they're not all unlocked at the same time:

  - Day 1: Character's dunder methods (__repr__, __eq__, __hash__, __lt__,
    __bool__) — same idea as Item in items.py, applied to a class other
    exercises will already be using.
  - Day 4: HealerMixin / TankMixin / LoggableMixin — the mixin & MRO
    workshop.
  - Day 5: GuildMeta — the registry metaclass. Character does NOT use it
    yet (see the class statement below) — wiring it in is literally your
    last Day 5 step, once GuildMeta itself works.

fields.py (StringField/IntField) is already working, so Character's
fields below will validate correctly from Day 1 onward regardless of
which of the above TODOs you've reached.
"""

from __future__ import annotations

from typing import Dict, Type

from .fields import IntField, StringField


class GuildMeta(type):
    """TODO (Day 5): a metaclass that automatically registers every
    concrete Character subclass by name — direct analogue of how Odoo's
    ORM collects model classes into its model registry at class-creation
    time, not at instantiation time.

    Two things your __new__ needs to do, after creating the class via
    super().__new__(...):
      1. Skip registration for the base Character class itself (it has no
         `bases`, i.e. `bases == ()`).
      2. For every other (concrete) subclass: validate that it has an int
         `base_hp` class attribute (directly or inherited) — raise
         TypeError if not — then add it to `GuildMeta.registry` keyed by
         class name.

    Once this works, go to the bottom of this file and change
    `class Character:` to `class Character(metaclass=GuildMeta):` — the
    registry is useless to Character until that line changes.
    """

    registry: Dict[str, Type["Character"]] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        raise NotImplementedError("TODO (Day 5): implement GuildMeta.__new__")


# TODO (Day 5, last step): once GuildMeta works, change the line below to:
#     class Character(metaclass=GuildMeta):
class Character:
    """Base class for every playable character."""

    name = StringField(max_length=50)
    hp = IntField(minimum=0)
    level = IntField(minimum=1, maximum=100)

    base_hp: int = 10  # overridden by every concrete subclass

    def __init__(self, name: str, level: int = 1):
        self.name = name
        self.level = level
        self.hp = self.base_hp * level

    def describe_role(self) -> str:
        return "Adventurer"

    # --- Day 1 dunder set -------------------------------------------------

    def __repr__(self) -> str:
        """(Day 1): should look like
        Warrior(name='Grom', level=2, hp=30)
        """
        return f"{self.__class__.__name__}(name={self.name!r}, level={self.level}, hp={self.hp})"

    def __str__(self) -> str:
        """(Day 1): should look like
        Grom the Warrior (Lv.2, 30 HP)
        """
        return (
            f"{self.name} the {self.__class__.__name__} (Lv.{self.level}, {self.hp} HP)"
        )

    def __eq__(self, other: object) -> bool:
        """Two Characters are equal when they're the same
        concrete type, AND have the same name AND the same level.
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.level == other.level and self.name == other.name

    def __hash__(self) -> int:
        """Must stay consistent with __eq__ above."""
        return hash((self.__class__, self.name, self.level))

    def __lt__(self, other: object) -> bool:
        """ (Day 1): order by level — this is what lets a Roster
        (Day 2) be sorted() directly with no key= needed.
        (Day 2 is handled in roster.py)
        """
        if not isinstance(other, Character):
            return NotImplemented
        return self.level < other.level

    def __bool__(self) -> bool:
        """(Day 1): a character is "truthy" while alive (hp > 0)."""
        return self.hp > 0

    def __format__(self, format_spec: str) -> str:
        if format_spec.lower() == "short":
            return self.name
        # Default return. Also works as `if format_spec.lower() in ["full", "long"]:`
        return str(self)


class Warrior(Character):
    base_hp = 15

    def describe_role(self) -> str:
        return "Warrior"


class Mage(Character):
    base_hp = 8

    def describe_role(self) -> str:
        return "Mage"


class Rogue(Character):
    base_hp = 10

    def describe_role(self) -> str:
        return "Rogue"


# --- Day 4 mixins: horizontal reuse without deep inheritance ---------------


class HealerMixin:
    """(Day 4, Dev A/whoever owns this): adds healing behavior.

    describe_role() must call super().describe_role() and append
    " + Healer" to whatever it returns — this is deliberate: it's one
    half of the cooperative MRO chain exercised by Paladin below. Do not
    hard-code a return value; the whole point breaks if you do.

    heal(target, amount=None): heals `target` by `amount` (or by
    self.heal_power if amount is None), capped at target's max HP
    (target.base_hp * target.level). Returns the target's new hp.
    """

    heal_power: int = 5

    def describe_role(self) -> str:
        return super().describe_role() + " + Healer"

    def heal(self, target: "Character", amount: int = None) -> int:
        if amount is None:
            amount = self.heal_power
        hp_ceil = target.base_hp * target.level
        target.hp = min(hp_ceil, target.hp + amount)
        return target.hp


class TankMixin:
    """TODO (Day 4): adds taunt/aggro behavior.

    describe_role() must call super().describe_role() and append
    " + Tank" — same cooperative-chain requirement as HealerMixin above.

    taunt(enemies): for this exercise, a simplified placeholder is fine —
    e.g. just return list(enemies). The mechanism (MRO), not combat
    balance, is the point.
    """

    taunt_radius: int = 3

    def describe_role(self) -> str:
        raise NotImplementedError("TODO (Day 4): implement TankMixin.describe_role")

    def taunt(self, enemies) -> list:
        raise NotImplementedError("TODO (Day 4): implement TankMixin.taunt")


class Paladin(HealerMixin, TankMixin, Warrior):
    """The deliberate mixin conflict. Once HealerMixin and TankMixin are
    implemented above, run Paladin.__mro__ and Paladin("x").describe_role()
    and be ready to explain, step by step, why the result is what it is —
    and what would change if TankMixin were listed before HealerMixin in
    the class statement above.
    """

    base_hp = 20


# --- Day 4 (independent mixin, not part of the conflict above) ------------


class LoggableMixin:
    """(Day 4): logs every attribute assignment on the
    instance into self._log (a list of strings).

    Two things to get right:
      1. __init__ needs to set up self._log = [] BEFORE calling
         super().__init__(...), and must do so via self.__dict__ directly
         (not `self._log = []`) to avoid triggering your own __setattr__
         override recursively before _log exists.
      2. __setattr__ should append an entry (e.g. f"{name} = {value!r}")
         for every assignment except to _log itself, then still actually
         perform the assignment via super().__setattr__(...).

    `log` should be a read-only property returning a copy of the list
    (not the live list itself).
    """
    _log: list

    def __init__(self, *args, **kwargs):
        self.__dict__["_log"] = [] # using __dict__ will prevent infinite calls to __setattr__ that self._log = [] would not
        super().__init__(*args, **kwargs)

    def __setattr__(self, name: str, value) -> None:
        self._log.append(f"{name} = {value!r}")
        super().__setattr__(name, value)

    @property
    def log(self) -> list:
        return list(self._log)


class LoggedMage(LoggableMixin, Mage):
    """Demo combination used by the test suite / workshop walkthrough."""
