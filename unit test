import unittest
import tkinter as tk
from final import Match3Game

class TestMatch3Game(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Prevent UI from showing during tests
        self.game = Match3Game(self.root)
        self.game.time_left = 10  # Give time for timer-related functions

    def test_initialize_board_fills_board(self):
        self.game.initialize_board()
        for row in self.game.board:
            for cell in row:
                self.assertIn(cell, self.game.colors + [self.game.obstacle_color])

    def test_find_matches_horizontal(self):
        self.game.board = [[None]*8 for _ in range(8)]
        self.game.board[2][1:4] = ["blue", "blue", "blue"]
        matches = self.game.find_matches()
        self.assertIn((2,1), matches)
        self.assertIn((2,2), matches)
        self.assertIn((2,3), matches)

    def test_find_matches_vertical(self):
        self.game.board = [[None]*8 for _ in range(8)]
        for i in range(3):
            self.game.board[i][5] = "green"
        matches = self.game.find_matches()
        self.assertIn((0,5), matches)
        self.assertIn((1,5), matches)
        self.assertIn((2,5), matches)

    def test_swap_back_undoes_swap(self):
        self.game.board[0][0] = "red"
        self.game.board[0][1] = "green"

        # Manually swap to simulate game behavior
        self.game.board[0][0], self.game.board[0][1] = self.game.board[0][1], self.game.board[0][0]

        # Now swap back
        self.game.swap_back(0, 0, 0, 1)

        self.assertEqual(self.game.board[0][0], "red")
        self.assertEqual(self.game.board[0][1], "green")

    def test_remove_matches_and_score(self):
        self.game.board = [[None]*8 for _ in range(8)]
        self.game.board[1][0:3] = ["purple"]*3
        matches = self.game.find_matches()
        score_before = self.game.score
        self.game.remove_matches_and_continue(matches)
        self.assertGreater(self.game.score, score_before)
        for i in range(3):
            self.assertIsNone(self.game.board[1][i])

    def test_drop_gems_fills_empty(self):
        self.game.board[7][0] = None
        self.game.drop_gems()
        self.assertIsNotNone(self.game.board[7][0])

    def test_check_post_drop_matches_triggers_again(self):
        self.game.board[0][0:3] = ["red", "red", "red"]
        self.game.check_post_drop_matches()
        self.assertFalse(self.game.in_action)  # Should reset after clearing

    def test_advance_level_resets_state(self):
        self.game.level = 1
        self.game.score = 999
        self.game.advance_level()
        self.assertEqual(self.game.level, 2)
        self.assertEqual(self.game.score, 0)

    def test_restart_game_resets_all(self):
        self.game.level = 5
        self.game.score = 999
        self.game.hints_left = 0
        self.game.restart_game()
        self.assertEqual(self.game.level, 1)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.hints_left, 3)

    def test_show_hint_highlights_move(self):
        # Create a clear move
        self.game.board = [[None]*8 for _ in range(8)]
        self.game.board[0][0] = "blue"
        self.game.board[0][1] = "red"
        self.game.board[0][2] = "blue"
        self.game.board[1][1] = "blue"
        self.game.hints_left = 1
        self.game.show_hint()
        self.assertEqual(len(self.game.hint_cells), 2)
        self.assertEqual(self.game.hints_left, 0)

    def tearDown(self):
        self.root.destroy()

if __name__ == "__main__":
    unittest.main()
