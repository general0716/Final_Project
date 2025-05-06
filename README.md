#  Match-3 with Obstacles

This is a Python-based tile-matching puzzle game inspired by titles like *Bejeweled* and *Candy Crush*, but with added mechanics like obstacles, level progression, combo bonuses, and a limited-use hint system.

The game is fully playable in a standalone `tkinter` GUI with no external dependencies. It was developed as a final project for a programming course.

---

##  Features

- Classic 3-in-a-row match logic with adjacent swap
- Levels with increasing score goals (+200 per level)
- Obstacle blocks starting from level 3
- Combo bonuses:
  - 4-match → clears full row or column
  - 5+ match → clears a 3x3 block
- Limited-use hint system, with hints earned on level up
- Countdown timer adds pressure to each level
- Fully resettable and replayable

---

##  Requirements

This game is written in **Python 3.7+** and only requires standard libraries:

```bash
python3 match3_game.py
```

No installation or pip packages are required. It uses:

- `tkinter` (for GUI)
- `random` (for board generation)

---

##  How to Play

1. Clone or download the repo.
2. Open the `match3_game.py` file in any IDE or terminal.
3. Run the file:
   ```bash
   python match3_game.py
   ```
4. Use your mouse to select and swap two adjacent blocks.
5. Match 3+ of the same color to eliminate them and score points.

---

##  Game Progression

| Level | Goal Score | Obstacles Introduced | Bonus Hint? |
|-------|------------|----------------------|-------------|
| 1     | 300        | ❌                   | ✅ (3 total) |
| 2     | 500        | ❌                   | ✅ (+1)      |
| 3+    | +200/level | ✅                   | ✅ (+1)      |

---

##  Bonus & Combo Rules

- **Match 4**: Triggers either a row or column clear.
- **Match 5+**: Clears a 3x3 area around the match.
- Each bonus also gives additional score.

---

##  Hint System

Clicking the **Hint** button will show a valid swap with a blue highlight. You start with 3 hints and earn +1 per level.

---

##  Development Notes

- All logic is contained in a single class: `Match3Game`
- Easy to extend: supports adding sound, tile images, animations, etc.
- Fully GUI-based, cross-platform
- Code has been thoroughly tested for match logic, edge cases, and level transitions

The game interface is shown below：

![image](https://github.com/user-attachments/assets/1311c65c-dadb-41fd-a340-960b53a2c846)



