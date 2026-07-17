import pytest

from guild.dungeon import dungeon_floors, guild_transaction


def test_dungeon_is_effectively_endless_until_retreat():
    log = []
    dungeon = dungeon_floors(log)

    encounter = next(dungeon)
    assert encounter["floor"] == 1

    # Advance through several floors without ever retreating.
    for _ in range(10):
        encounter = dungeon.send("continue")
    assert encounter["floor"] >= 4  # multiple floors have passed
    assert "Entering floor 1" in log


def test_dungeon_retreat_ends_generator_cleanly():
    log = []
    dungeon = dungeon_floors(log)
    next(dungeon)
    with pytest.raises(StopIteration):
        dungeon.send("retreat")
    assert any("retreats mid-floor" in line for line in log)
    assert "Party returns to town." in log
    assert "Dungeon generator closed." in log


def test_dungeon_close_triggers_cleanup_via_generator_exit():
    log = []
    dungeon = dungeon_floors(log)
    next(dungeon)
    dungeon.close()
    assert "Dungeon generator closed." in log


def test_guild_transaction_commits_on_success():
    treasury = {"gold": 100}
    with guild_transaction(treasury) as t:
        t["gold"] -= 30
    assert treasury["gold"] == 70


def test_guild_transaction_rolls_back_on_error():
    treasury = {"gold": 100}
    with pytest.raises(ValueError):
        with guild_transaction(treasury) as t:
            t["gold"] -= 30
            raise ValueError("insufficient permissions")
    assert treasury["gold"] == 100  # rolled back


def test_nested_transaction_both_commit():
    """Outer and inner both succeed - both changes persist."""
    treasury = {"gold": 100}

    with guild_transaction(treasury):
        treasury["gold"] -= 30  # outer: 70
        with guild_transaction(treasury):
            treasury["gold"] -= 10  # inner: 60

    assert treasury["gold"] == 60


def test_nested_transaction_inner_rolls_back():
    """Inner fails, outer succeeds - outer's changes preserved."""
    treasury = {"gold": 100}

    with guild_transaction(treasury):
        treasury["gold"] -= 30  # outer: 70
        with pytest.raises(ValueError):
            with guild_transaction(treasury):
                treasury["gold"] -= 10  # inner: 60
                raise ValueError("inner fail")
        # After inner rollback, should be back to outer's state (70)

    assert treasury["gold"] == 70


def test_nested_transaction_outer_rolls_back_after_inner_commit():
    """Inner succeeds, outer fails - everything rolls back."""
    treasury = {"gold": 100}

    with pytest.raises(ValueError):
        with guild_transaction(treasury):
            treasury["gold"] -= 30  # outer: 70
            with guild_transaction(treasury):
                treasury["gold"] -= 10  # inner: 60
            raise ValueError("outer fail")

    assert treasury["gold"] == 100  # fully rolled back


def test_deep_nesting_three_levels():
    """Three levels of nesting - arbitrary depth works."""
    treasury = {"gold": 100}

    with guild_transaction(treasury) as t1:
        t1["gold"] -= 10  # 90
        with guild_transaction(treasury) as t2:
            t2["gold"] -= 10  # 80
            with guild_transaction(treasury) as t3:
                t3["gold"] -= 10  # 70

    assert treasury["gold"] == 70


def test_nested_transaction_metadata_isolation():
    """Metadata keys (_snapshots) don't leak to user code."""
    treasury = {"gold": 100}

    with guild_transaction(treasury):
        with guild_transaction(treasury):
            pass

    # User keys only
    assert set(treasury.keys()) == {"gold"}
    assert "_snapshots" not in treasury
