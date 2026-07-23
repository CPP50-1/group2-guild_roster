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


def register_character(cls):
    """Class decorator alternative: the Day 5 theory names class decorators
    as a simpler alternative to metaclasses for some use cases. Write a
    @register_character class decorator that does the same registration
    GuildMeta does (add the class to a registry dict by name), without a
    metaclass at all. Get it working, then write down two or three sentences
    on when you'd reach for the decorator instead of the metaclass, what can
    a metaclass do that a class decorator structurally can't?
    """
    # Use a class decorator (@register_character) when you only need to do
    # something basic AFTER the class is built, like saving it in a list.
    # Use a metaclass (GuildMeta) when you need to change how the class is
    # built. A decorator can only see the finished class; a metaclass can
    # also make sure every subclass follows the same rules automatically.
    if cls is not Character:
        if not isinstance(cls.base_hp, int):
            raise TypeError("Health must be integer")

        class_name = cls.__name__
        if class_name not in register_character.registry:
            register_character.registry[cls.__name__] = cls

    return cls


register_character.registry: dict[str, Type[Character]] = {}


class GuildMeta(type):
    """(Day 5): a metaclass that automatically registers every
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
        new_class = super().__new__(mcs, name, bases, namespace, **kwargs)
        if bases:
            if type(namespace.get("base_hp", 0)) is not int:
                raise TypeError("Health must be integer")
            else:
                mcs.registry[name] = new_class
        return new_class

     #    ** Instantiate by name: ** add a method to `GuildMeta`( or a helper function) that takes a
     # class name string and constructs an instance,
     # e.g. `GuildMeta.create("Warrior", name="Grom", level=3)`, looking the
     # class up in `GuildMeta.registry` rather than importing it directly.This
     # is close to how Odoo actually instantiates models by their `_name` string at runtime,
    # and is worth comparing side - by - side with a plain ` if / elif ` chain doing the same dispatch by hand, which one scales better as the number of subclasses grows?
    @classmethod
    def create(cls, class_name, **kwargs):
        new_class = cls.registry.get(class_name)
        return new_class(**kwargs) if new_class else None


class CachedProperty:
    # Explain why this only works because it's a *non-data* descriptor, what would break if it also defined `__set__`?
    #
    # It would become a data descriptor. calling __get__ at every call instead of reading __dict__, because Python checks
    # the data descriptor before checking the instance dict.
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = obj.level * 5 * (obj.base_hp % 4)
        obj.__dict__["total_power"] = value
        return value


# (Day 5, last step): once GuildMeta works, change the line below to:
#     class Character(metaclass=GuildMeta):
class Character(metaclass=GuildMeta):
    """Base class for every playable character."""

    name = StringField(max_length=50)
    hp = IntField(minimum=0)
    level = IntField(minimum=1, maximum=100)
    total_power = CachedProperty()
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
        """(Day 1): order by level — this is what lets a Roster
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


@register_character
class Warrior(Character):
    base_hp = 15

    def describe_role(self) -> str:
        return "Warrior"


@register_character
class Mage(Character):
    base_hp = 8

    def describe_role(self) -> str:
        return "Mage"


@register_character
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
    """(Day 4): adds taunt/aggro behavior.

    describe_role() must call super().describe_role() and append
    " + Tank" — same cooperative-chain requirement as HealerMixin above.

    taunt(enemies): for this exercise, a simplified placeholder is fine —
    e.g. just return list(enemies). The mechanism (MRO), not combat
    balance, is the point.
    """

    taunt_radius: int = 3

    def describe_role(self) -> str:
        return super().describe_role() + " + Tank"

    def taunt(self, enemies) -> list:
        return list(enemies)


@register_character
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
        # using __dict__ will prevent infinite calls to __setattr__ that self._log = [] would not
        self.__dict__["_log"] = []
        super().__init__(*args, **kwargs)

    def __setattr__(self, name: str, value) -> None:
        self._log.append(f"{name} = {value!r}")
        super().__setattr__(name, value)

    @property
    def log(self) -> list:
        return list(self._log)


@register_character
class LoggedMage(LoggableMixin, Mage):
    """Demo combination used by the test suite / workshop walkthrough."""
