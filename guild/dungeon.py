"""Day 3, Dev C: two pieces, both TODOs.

1. An infinite dungeon generator built from yield-from delegation to a
   per-floor sub-generator.
2. A contextlib.contextmanager-style transaction. Look at
   exceptions.batch_validation (in exceptions.py) first — it's a complete,
   working example of exactly this pattern (a generator wrapped in
   @contextmanager) — before writing this one from scratch.
"""

from __future__ import annotations

from collections.abc import Generator, Iterator
from contextlib import ExitStack, contextmanager


def floor_encounters(floor_number: int, dungeon_log: list[str]) -> Iterator[dict]:
    """One floor's worth of encounters.

    Requirements:
      - Append "Entering floor N" to dungeon_log at the start.
      - Build a small list of encounter dicts for this floor (a monster
        and a loot chest at minimum; add a trap every 3rd floor — your
        call on the exact shape, keep it consistent with dungeon_floors
        below and with the tests).
      - For each encounter: `action = yield encounter`. If action ==
        "retreat", append a log line and `return "retreated"` immediately.
      - If the loop finishes without a retreat, append a "cleared" log
        line and `return "cleared"`.
      - Wrap the body in try/finally, appending a "Leaving floor N" log
        line in the finally block — this needs to run whether the floor
        ends via retreat, via clearing it, or via the caller closing the
        whole dungeon mid-floor.
    """
    dungeon_log.append(f"Entering floor {floor_number}")

    encounters = [
        {
            "floor": floor_number,
            "type": "monster",
            "name": f"Monster {floor_number}",
        },
        {
            "floor": floor_number,
            "type": "loot_chest",
            "loot": f"{floor_number * 5} golds",
        },
    ]
    if floor_number % 3 == 0:
        encounters.append(
            {
                "floor": floor_number,
                "type": "trap",
                "damage": 2 * floor_number,
            }
        )

    try:
        for encounter in encounters:
            action = yield encounter
            if action == "retreat":
                dungeon_log.append(f"Party retreats mid-floor {floor_number}")
                return "retreated"

        dungeon_log.append(f"Floor {floor_number} cleared")
        return "cleared"

    finally:
        dungeon_log.append(f"Leaving floor {floor_number}")


def dungeon_floors(dungeon_log: list[str]) -> Iterator[dict]:
    """An intentionally endless generator — there is no fixed last
    floor, only a floor the party chooses to stop at.

    Requirements:
      - Loop forever, incrementing a floor_number each iteration.
      - Delegate to floor_encounters via `yield from` — capture its
        return value (`result = yield from floor_encounters(...)`).
        This is what lets you find out *why* the floor ended (cleared vs.
        retreated) without any extra signalling mechanism — yield from
        forwards every .send() call through to the sub-generator AND
        surfaces its return value once it's exhausted.
      - If the result is "retreated", log a "returns to town" line and
        `return` (ending the whole dungeon run).
      - Wrap the while loop in try/finally, logging "Dungeon generator
        closed." in the finally block — reached both by the `return`
        above and by GeneratorExit (i.e. the caller calling .close()).
    """
    floor_number: int = 1

    try:
        while True:
            result = yield from floor_encounters(floor_number, dungeon_log)
            if result == "retreated":
                dungeon_log.append("Party returns to town.")
                return
            floor_number += 1
    finally:
        dungeon_log.append("Dungeon generator closed.")


@contextmanager
def guild_transaction(
    treasury: dict[str, int],
) -> Generator[dict[str, int], None, None]:
    """Simulates a database transaction over an in-memory treasury
    dict — mutations inside the `with` block are kept if the block
    completes without error, and rolled back to the pre-block snapshot if
    it raises.

    Requirements:
      - Take a snapshot (a copy) of `treasury` before yielding it.
      - `yield treasury` so the caller can mutate it directly inside the
        `with` block.
      - If an exception occurs inside the block, restore `treasury` to
        the snapshot's contents, then re-raise the exception — do NOT
        suppress it. (Suppressing would mean *not* re-raising; that would
        be the wrong choice here, and worth being able to explain why.)

    Bonus: Nested transactions, extend the treasury system to support: a
    savepoint, transaction nested inside another transaction where the inner
    one can roll back independently without undoing the outer one's changes
    (if the outer one goes on the succeed). Use `contextlib.ExitStack` to
    manage an arbitray depth of nested `guild_transaction` calls rather than
    hard-coding two levels.
    """
    if "_snapshots" not in treasury:
        treasury["_snapshots"] = []

    snapshot: dict[str, int] = {
        k: v for k, v in treasury.items() if not k.startswith("_")
    }
    treasury["_snapshots"].append(snapshot)

    def rollback():
        for k in list(treasury.keys()):
            if not k.startswith("_"):
                del treasury[k]
        treasury.update(treasury["_snapshots"].pop())

        # Clean up _snapshots if empty
        if not treasury["_snapshots"]:
            del treasury["_snapshots"]

    with ExitStack() as stack:
        stack.callback(rollback)
        try:
            yield treasury
        except Exception:
            raise
        else:
            treasury["_snapshots"].pop()
            if not treasury["_snapshots"]:
                del treasury["_snapshots"]
            stack.pop_all()
