import pytest

from guild.models import (
    CachedProperty,
    Character,
    GuildMeta,
    HealerMixin,
    LoggedMage,
    Mage,
    Paladin,
    Rogue,
    TankMixin,
    Warrior,
    register_character,
)


def test_metaclass_registers_concrete_subclasses():
    assert GuildMeta.registry["Warrior"] is Warrior
    assert GuildMeta.registry["Mage"] is Mage
    assert GuildMeta.registry["Rogue"] is Rogue
    assert GuildMeta.registry["Paladin"] is Paladin


def test_metaclass_rejects_non_int_base_hp():
    with pytest.raises(TypeError):

        class Broken2(Character):
            base_hp = "not an int"


def test_dunder_repr_and_str():
    w = Warrior("Grom", level=2)
    assert repr(w) == "Warrior(name='Grom', level=2, hp=30)"
    assert str(w) == "Grom the Warrior (Lv.2, 30 HP)"


def test_dunder_eq_and_hash():
    a = Warrior("Grom", level=2)
    b = Warrior("Grom", level=2)
    c = Warrior("Thok", level=2)
    assert a == b
    assert hash(a) == hash(b)
    assert a != c


def test_dunder_lt_orders_by_level():
    low = Warrior("Grom", level=1)
    high = Warrior("Grommash", level=10)
    assert low < high


def test_dunder_bool_reflects_hp():
    w = Warrior("Grom", level=1)
    assert bool(w) is True
    w.hp = 0
    assert bool(w) is False


def test_paladin_mro_order():
    assert Paladin.__mro__[:5] == (Paladin, HealerMixin, TankMixin, Warrior, Character)


def test_paladin_describe_role_cooperative_chain():
    p = Paladin("Uther", level=1)
    assert p.describe_role() == "Warrior + Tank + Healer"


def test_healer_mixin_heals_target():
    healer = Paladin("Uther", level=5)
    target = Mage("Jaina", level=5)
    target.hp = 1
    new_hp = healer.heal(target)
    assert new_hp == 1 + healer.heal_power


def test_loggable_mixin_tracks_assignments():
    m = LoggedMage("Jaina", level=1)
    m.hp = 5
    assert any("hp = 5" in entry for entry in m.log)


# --- CachedProperty (non-data descriptor) -----------------------------------


def test_character_total_power_computes_on_first_access():
    w = Warrior("Grom", level=2)
    assert w.total_power == 2 * 5 * (15 % 4)  # 2 * 5 * 3 = 30


def test_character_total_power_caches_result():
    w = Warrior("Grom", level=2)
    _ = w.total_power  # compute & cache
    assert "total_power" in w.__dict__
    assert w.__dict__["total_power"] == 30


def test_character_total_power_recomputes_after_delete():
    w = Warrior("Grom", level=2)
    first = w.total_power  # 30
    del w.total_power
    second = w.total_power  # recomputes — still 30 since level/base_hp unchanged
    assert first == second


def test_character_class_has_descriptor_not_int():
    assert isinstance(Character.__dict__["total_power"], CachedProperty)


def test_total_power_depends_on_level_and_base_hp():
    low = Warrior("A", level=1)  # 1 * 5 * (15%4) = 1 * 5 * 3 = 15
    high = Warrior("B", level=10)  # 10 * 5 * (15%4) = 10 * 5 * 3 = 150
    assert low.total_power == 15
    assert high.total_power == 150


def test_cached_property_returns_self_on_class_access():
    assert isinstance(Character.total_power, CachedProperty)


def test_mro_conflict():
    class A(HealerMixin, TankMixin):
        pass

    class B(TankMixin, HealerMixin):
        pass

    with pytest.raises(TypeError, match="consistent method resolution order"):

        class C(A, B):
            pass


def test_register_character_registers_concrete_subclasses():
    assert register_character.registry["Warrior"] is Warrior
    assert register_character.registry["Mage"] is Mage
    assert register_character.registry["Rogue"] is Rogue
    assert register_character.registry["Paladin"] is Paladin


def test_register_character_rejects_non_int_base_hp():
    with pytest.raises(TypeError):

        @register_character
        class Broken(Character):
            base_hp = "not an int"


def test_register_character_skips_base_class():
    assert "Character" not in register_character.registry
