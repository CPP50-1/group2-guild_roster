"""Day 3, Dev A: a turn-based combat coroutine.

Usage sketch once implemented:

    log = []
    fight = battle(character, log)
    state = next(fight)                # prime the generator
    state = fight.send("attack")       # player acts, generator advances
    state = fight.throw(AmbushError()) # simulate an interrupt mid-battle
    fight.close()                      # abandon the fight cleanly
"""

from __future__ import annotations

from typing import Dict, Generator, List

from .exceptions import GuildError
from .models import Character, Mage, Warrior, Rogue

from itertools import permutations
from random import randint


class AmbushError(GuildError):
    """Raised into the battle generator to simulate a mid-fight ambush —
    exercises Generator.throw() specifically.
    """

    pass


def battle(
    character: Character,
    combat_log: List[str],
    enemy_name: str = "Goblin",
    enemy_hp: int = 30,
    enemy_attack: int = 5,
) -> Generator[Dict, str, None]:
    try:
        combat_log.append(f"{enemy_name} appears!")
        while character.hp > 0 and enemy_hp > 0:
            state_snapshot = {"character_hp": character.hp, "enemy_hp": enemy_hp}
            action = yield state_snapshot

            if action == "attack":
                enemy_hp -= character.level * 2
                combat_log.append(
                    f"{enemy_name} got pummeled{f'! They have {enemy_hp} HP remaining.' if enemy_hp > 0 else ' to death!'}"
                )

            elif action == "heal":
                max_hp = character.base_hp * character.level
                character.hp = min(character.hp + character.level * 2, max_hp)
                combat_log.append(
                    f"{character.name} is feeling better! HP is now {character.hp}."
                )

            elif action == "flee":
                combat_log.append(f"{character.name} flees the battle!")
                return

            else:
                combat_log.append(f"Action {action} is not recognized.")
                # continue (?)

            if enemy_hp > 0:
                character.hp -= enemy_attack
                combat_log.append(
                    f"Ouch! {character.name} is {f'now down to {character.hp} HP' if character.hp > 0 else f'knocked unconscious!'}"
                )
                if character.hp <= 0:
                    state_snapshot["outcome"] = "defeat"

        yield {"outcome": "victory" if enemy_hp <= 0 else "defeat"}

    except AmbushError:
        combat_log.append(f"A sneaky {enemy_name} hit you before you could react!")
        character.hp -= enemy_attack
        yield {"ambushed": True}

    finally:
        combat_log.append("Combat generator closed.")

    """(Day 3): a generator-based combat loop.
    
    Requirements:
      - Append a "X appears!" style line to combat_log at the start.
      - Loop while both character_hp and enemy_hp are above 0. Each
        iteration: `action = yield {...state snapshot...}`, then handle
        action in ("attack", "heal", "flee") plus a fallback for unknown
        actions. "attack" reduces enemy_hp; "heal" restores some
        character_hp (capped at character.base_hp * character.level);
        "flee" should `return` immediately (ending the generator).
      - After a successful attack, if the enemy is still alive, it hits
        back (reduce character_hp by enemy_attack).
      - When the loop ends naturally (someone hit 0 hp), yield one final
        state dict with an "outcome" key ("victory" or "defeat").
      - Wrap the whole thing in try/except AmbushError: catching an
        ambush thrown in via .throw() should apply damage and yield a
        state dict with "ambushed": True.
      - Use `finally` to append a "Combat generator closed." line to
        combat_log — this must run whether the generator ends via
        `return`, naturally, or via .close() (which raises GeneratorExit
        at the suspended yield point). Do not `yield` from inside a
        finally block that's handling GeneratorExit — that will raise a
        RuntimeError.

    `combat_log` is a list supplied by the caller (not returned) because
    generator locals disappear once the frame ends — this is why the log
    needs to live outside the generator itself.
    """


# bonus method
def party_battle(
    characters: tuple[Character, ...],
    combat_log: List[str],
    enemy_name: str = "Goblin",
    enemy_hp: int = 30,
    enemy_attack: int = 5,
) -> Generator[Dict, str, None | int]:
    try:
        combat_log.append(f"{enemy_name} appears!")
        while (
            characters[0].hp > 0 or characters[1].hp > 0 or characters[2].hp > 0
        ) and enemy_hp > 0:
            for character in characters:
                if character.hp <= 0:
                    continue
                else:
                    state_snapshot = {
                        "character_hp": character.hp,
                        "enemy_hp": enemy_hp,
                    }
                    action = yield state_snapshot

                    if action == "attack":
                        enemy_hp -= character.level * 2
                        combat_log.append(
                            f"{enemy_name} got pummeled{f'! They have {enemy_hp} HP remaining.' if enemy_hp > 0 else ' to death!'}"
                        )

                    elif action == "heal":
                        max_hp = character.base_hp * character.level
                        character.hp = min(character.hp + character.level * 2, max_hp)
                        combat_log.append(
                            f"{character.name} is feeling better! HP is now {character.hp}."
                        )

                    elif action == "flee":
                        combat_log.append(f"{character.name} flees the battle!")
                        return None

                    else:
                        combat_log.append(f"Action {action} is not recognized.")
                        # continue (?)

            if enemy_hp > 0:
                random_target = characters[randint(0, 2)]
                while random_target.hp <= 0:
                    random_target = characters[randint(0, 2)]
                random_target.hp -= enemy_attack
                combat_log.append(
                    f"Ouch! {random_target.name} is {f'now down to {random_target.hp} HP' if random_target.hp > 0 else f'knocked unconscious!'}"
                )

        final_score = sum(character.hp for character in characters) - enemy_hp

        yield {
            "outcome": "victory" if enemy_hp <= 0 else "defeat",
            "final_score": final_score,
        }

        return final_score

    except AmbushError:
        random_target = characters[randint(0, 2)]
        combat_log.append(
            f"A sneaky {enemy_name} hit {random_target} before you could react!"
        )
        random_target.hp -= enemy_attack
        yield {"ambushed": True}

    finally:
        combat_log.append("Combat generator closed.")


# bonus: generating all combinations of 3-character parties and rate them.
# I chose final HP across the battlefield (negative if enemies win) as measurement.


def determine_best_party(
    party: List[Character] | None,
) -> List[tuple[int, tuple[Character, ...]]]:
    if party is None:
        party = [Warrior(name="Grom"), Mage(name="Jaina"), Rogue(name="Valeera")]
    rankings = []

    for permutation in permutations(party):
        for char in permutation:
            char.hp = char.base_hp * char.level

        combat_log = []
        battle_gen = party_battle(characters=permutation, combat_log=combat_log)

        final_snapshot = {}
        for snapshot in battle_gen:
            final_snapshot = snapshot  # Keeps overwriting until it holds the last one (which is the one we need here)

        score = final_snapshot.get("final_score", 0)
        rankings.append((score, permutation))

    rankings.sort(reverse=True, key=lambda entry: entry[0])

    return rankings
