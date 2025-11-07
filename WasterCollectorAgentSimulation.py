# -*- coding: utf-8 -*-
"""
Garbage Collector Agent Simulation
Author: Mohammed Safique Hossain
Date-11-05-2025
------------------------------

How to run (interactive):
    python gc_sim.py

How to run (as a module):
    from gc_sim import run
    out = run(20, day_type="garbage", seed=7)
    print(out["total_fines_$"])
"""

from dataclasses import dataclass, field
from typing import List, Optional
import random

# -------- Base Classes -------- #

class Thing:
    def __repr__(self):
        return f"<{getattr(self, '__name__', self.__class__.__name__)}>"

class Agent(Thing):
    def __init__(self, program=None):
        self.alive = True
        self.program = program or (lambda percept: "NoOp")
        self.performance = 0

class Environment:
    def __init__(self):
        self.things = []
        self.agents = []
        self.time = 0

    def percept(self, agent):
        raise NotImplementedError

    def execute_action(self, agent, action):
        raise NotImplementedError

    def is_done(self):
        return not any(agent.alive for agent in self.agents)

    def step(self):
        if self.is_done():
            return
        actions = []
        for agent in self.agents:
            if agent.alive:
                actions.append(agent.program(self.percept(agent)))
            else:
                actions.append("NoOp")
        for (agent, action) in zip(self.agents, actions):
            self.execute_action(agent, action)
        self.time += 1

    def run(self, steps=1000):
        for _ in range(steps):
            if self.is_done():
                break
            self.step()

    def add_thing(self, thing, location=None):
        thing.location = location
        self.things.append(thing)
        if isinstance(thing, Agent):
            self.agents.append(thing)

# -------- Domain -------- #

@dataclass
class BinState:
    garbage: int = 0
    recycle: int = 0

@dataclass
class LocationState:
    garbage_bin: BinState = field(default_factory=BinState)
    recycle_bin: BinState = field(default_factory=BinState)

class GarbageCollector(Agent):
    def __init__(self, day_type: str):
        assert day_type in ("garbage", "recycle")
        self.day_type = day_type
        self.location = 0
        super().__init__(program=self._program)

    def _program(self, percept):
        loc_idx, loc_state = percept
        target_bin = loc_state.garbage_bin if self.day_type == "garbage" else loc_state.recycle_bin
        target_count = target_bin.garbage if self.day_type == "garbage" else target_bin.recycle
        return "collect" if target_count > 0 else "move"

class KennedyStreet(Environment):
    def __init__(self, num_locations: int, day_type: str,
                 p_item: float = 0.6, p_contam: float = 0.25, p_miss: float = 0.1,
                 seed: Optional[int] = None):
        super().__init__()
        assert num_locations > 0, "num_locations must be > 0"
        assert day_type in ("garbage", "recycle")
        if seed is not None:
            random.seed(seed)

        self.num_locations = num_locations
        self.day_type = day_type
        self.p_item = p_item
        self.p_contam = p_contam
        self.p_miss = p_miss

        self.street: List[LocationState] = [self._init_location() for _ in range(num_locations)]
        self.logs: List[str] = []
        self.fine_uncollected: int = 0
        self.fine_contamination: int = 0
        self.inspection_done: bool = False

    def _init_location(self) -> LocationState:
        ls = LocationState()
        # Correct items
        if random.random() < self.p_item:
            ls.garbage_bin.garbage += 1
        if random.random() < self.p_item:
            ls.recycle_bin.recycle += 1
        # Contamination
        if random.random() < self.p_contam:
            ls.garbage_bin.recycle += 1
        if random.random() < self.p_contam:
            ls.recycle_bin.garbage += 1
        return ls

    def percept(self, agent: GarbageCollector):
        return (agent.location, self.street[agent.location])

    def execute_action(self, agent: GarbageCollector, action: str):
        if action == "collect":
            if random.random() < self.p_miss:
                self.logs.append(f"[step {self.time+1}] Missed {self.day_type} pickup at location {agent.location}.")
            else:
                if self.day_type == "garbage":
                    count = self.street[agent.location].garbage_bin.garbage
                    self.street[agent.location].garbage_bin.garbage = 0
                else:
                    count = self.street[agent.location].recycle_bin.recycle
                    self.street[agent.location].recycle_bin.recycle = 0
                self.logs.append(f"[step {self.time+1}] Collected {self.day_type} at location {agent.location} (items: {count}).")
        elif action == "move":
            next_loc = min(agent.location + 1, self.num_locations - 1)
            self.logs.append(f"[step {self.time+1}] Moving from {agent.location} to {next_loc}.")
            agent.location = next_loc

        # Stop after last index is reached and the agent tries to move again (no more positions)
        if agent.location == self.num_locations - 1 and action != "collect":
            agent.alive = False

    def inspect_and_fine(self):
        if self.inspection_done:
            return
        uncollected_locations = []
        contamination_locations = []

        for i, ls in enumerate(self.street):
            # Uncollected: only the serviced bin
            if self.day_type == "garbage":
                if ls.garbage_bin.garbage > 0:
                    self.fine_uncollected += 100
                    uncollected_locations.append(i)
                # Contamination: only recyclables in garbage-bin
                if ls.garbage_bin.recycle > 0:
                    self.fine_contamination += 200
                    contamination_locations.append(i)
            else:  # recycle day
                if ls.recycle_bin.recycle > 0:
                    self.fine_uncollected += 100
                    uncollected_locations.append(i)
                # Contamination: only garbage in recycle-bin
                if ls.recycle_bin.garbage > 0:
                    self.fine_contamination += 200
                    contamination_locations.append(i)

        for loc in uncollected_locations:
            self.logs.append(f"[inspection] Fine $100 at location {loc} for uncollected {self.day_type}.")

        if self.day_type == "garbage":
            for loc in contamination_locations:
                self.logs.append(f"[inspection] Fine $200 at location {loc} for contamination "
                                 f"(garbage-bin has recycle).")
        else:
            for loc in contamination_locations:
                self.logs.append(f"[inspection] Fine $200 at location {loc} for contamination "
                                 f"(recycle-bin has garbage).")

        self.inspection_done = True
        return {
            "uncollected_locations": uncollected_locations,
            "contamination_locations": contamination_locations,
            "fine_uncollected_$": self.fine_uncollected,
            "fine_contamination_$": self.fine_contamination,
            "total_fines_$": self.fine_uncollected + self.fine_contamination
        }

# -------- Public API -------- #

def run(num_locations: int, day_type: str = "garbage", seed: Optional[int] = None,
        p_item: float = 0.6, p_contam: float = 0.25, p_miss: float = 0.1):
    env = KennedyStreet(num_locations, day_type, p_item, p_contam, p_miss, seed=seed)
    agent = GarbageCollector(day_type)
    env.add_thing(agent, 0)
    env.run(steps=num_locations)     # agent will traverse 0..N-1
    fines = env.inspect_and_fine()
    summary = {
        "num_locations": num_locations,
        "day_type": day_type,
        **fines,
        "logs": env.logs
    }
    return summary

# -------- Interactive CLI -------- #

def _prompt_day():
    print("Which waste collector? Garbage or Recycle")
    while True:
        t = input("> ").strip().lower()
        if t.startswith("g"): return "garbage"
        if t.startswith("r"): return "recycle"
        if t in ("garbage", "recycle"): return t
        print("Please type 'Garbage' or 'Recycle'.")

def _prompt_n():
    print("How long location?")
    try:
        n = int(input("> ").strip())
        if n <= 0: raise ValueError()
        return n
    except Exception:
        print("Invalid number. Defaulting to 20.")
        return 20

def main():
    day = _prompt_day()
    n = _prompt_n()
    print(f"\n--- Running {day.capitalize()} Collection ---")
    print(f"Locations: 0 .. {n-1}\n")
    out = run(n, day_type=day, seed=25)  # set seed to an int for reproducible runs
    for line in out["logs"]:
        print(line)
    print("\n--- Summary ---")
    for k, v in out.items():
        if k != "logs":
            print(f"{k}: {v}")

if __name__ == "__main__":
    main()
