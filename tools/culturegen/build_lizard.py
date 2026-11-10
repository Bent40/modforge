"""Build the hand-designed lizardman huts (levels 1-5) into a loose Structurize pack plus previews.

    python3 -m tools.culturegen.build_lizard [out_pack_dir] [preview_dir]
"""
import sys

from .build_dwarf import build
from .hand_lizard import lizard_dojo, lizard_hall, lizard_house

HUTS = [
    ("townhall", lizard_hall, {}, "minecolonies:blockhuttownhall", (13 // 2 + 2, 4, 2), "fundamentals"),
    ("residence", lizard_house, {}, "minecolonies:blockhutcitizen", (4, 3, 2), "fundamentals"),
    ("combatacademy", lizard_dojo, {}, "minecolonies:blockhutcombatacademy", (13 // 2 + 2, 3), "military"),
]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "drafts/lizard-culture/pack/lizard_preview"
    pdir = sys.argv[2] if len(sys.argv) > 2 else "drafts/lizard-culture/previews/levels"
    print("\n".join(build(out, pdir, HUTS, "lizard")))
