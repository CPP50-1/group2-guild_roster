import pytest

from guild.items import Item, Rarity


def test_repr_and_str_differ():
    item = Item("Iron Sword", Rarity.COMMON, 10)
    assert repr(item) == "Item(name='Iron Sword', rarity=<Rarity.COMMON: 1>, value=10)"
    assert str(item) == "Iron Sword (Common, 10g)"


def test_equality_and_hash_consistency():
    a = Item("Iron Sword", Rarity.COMMON, 10)
    b = Item("Iron Sword", Rarity.COMMON, 10)
    c = Item("Iron Sword", Rarity.RARE, 10)
    assert a == b
    assert hash(a) == hash(b)
    assert a != c


def test_set_support_relies_on_hash_and_eq():
    a = Item("Iron Sword", Rarity.COMMON, 10)
    b = Item("Iron Sword", Rarity.COMMON, 10)  # equal to a
    c = Item("Steel Sword", Rarity.UNCOMMON, 25)
    bag = {a, b, c}
    assert len(bag) == 2  # a and b collapse into one


def test_ordering_by_rarity_then_value():
    common = Item("Rock", Rarity.COMMON, 1)
    rare_cheap = Item("Gem Shard", Rarity.RARE, 5)
    rare_expensive = Item("Gem", Rarity.RARE, 50)
    assert common < rare_cheap < rare_expensive
    assert sorted([rare_expensive, common, rare_cheap]) == [common, rare_cheap, rare_expensive]


def test_bool_reflects_value():
    assert bool(Item("Gold Coin", Rarity.COMMON, 1)) is True
    assert bool(Item("Broken Twig", Rarity.COMMON, 0)) is False

def test_add_valid():
    a = Item("Iron Sword", Rarity.COMMON, 15)
    b = Item("Iron Sword", Rarity.COMMON, 10)  # equal to a
    c = a + b
    assert (c.name, c.rarity, c.value) == ("Iron Sword", Rarity.COMMON, 25)


@pytest.mark.parametrize("name", ["", None])
def test_empty_name_raises(name):
    with pytest.raises(ValueError):
        Item(name, Rarity.COMMON, 10)


@pytest.mark.parametrize("rarity", [99, "COMMON"])
def test_invalid_rarity_raises(rarity):
    with pytest.raises(TypeError):
        Item("Sword", rarity, 10)


def test_negative_value_raises():
    with pytest.raises(ValueError):
        Item("Sword", Rarity.COMMON, -5)


def test_zero_value_is_valid():
    item = Item("Junk", Rarity.COMMON, 0)
    assert item.value == 0