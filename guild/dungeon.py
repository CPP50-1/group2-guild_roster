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
from contextlib import contextmanager


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
    raise NotImplementedError("TODO (Day 3): implement floor_encounters")


def dungeon_floors(dungeon_log: List[str]) -> Iterator[Dict]:
    """TODO: an intentionally endless generator — there is no fixed last
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
    raise NotImplementedError("TODO (Day 3): implement dungeon_floors")


# --- TODO (Day 3): guild treasury transaction --------------------------------

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
    """
    raise NotImplementedError("TODO (Day 3): implement guild_transaction")
