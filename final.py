import tkinter as tk
import random

class Match3Game:
    def __init__(self, root, rows=8, cols=8, cell_size=40):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.colors = ["red", "green", "blue", "yellow", "purple", "orange"]
        self.obstacle_color = "gray"

        self.level = 1
        self.level_goal = 300
        self.time_left = 150
        self.score = 0
        self.selected = None
        self.in_action = False
        self.hints_left = 3
        self.hint_cells = []

        self.board = [[None] * self.cols for _ in range(self.rows)]

        self.label = tk.Label(root)
        self.label.pack(pady=5)
        self.canvas = tk.Canvas(root, width=self.cols*cell_size, height=self.rows*cell_size, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.hint_button = tk.Button(root, text=f"Hint ({self.hints_left})", command=self.show_hint)
        self.hint_button.pack(pady=5)

        self.level_complete_button = None
        self.restart_button = None

        self.initialize_board()
        self.draw_board()
        self.update_timer()

    def initialize_board(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.board[r][c] = random.choice(self.colors)
        if self.level >= 3:
            count = min(self.level, self.rows * self.cols)
            placed = 0
            while placed < count:
                r = random.randint(0, self.rows - 1)
                c = random.randint(0, self.cols - 1)
                if self.board[r][c] != self.obstacle_color:
                    self.board[r][c] = self.obstacle_color
                    placed += 1
        while True:
            matches = self.find_matches()
            if not matches:
                break
            for r, c in matches:
                if self.board[r][c] != self.obstacle_color:
                    self.board[r][c] = random.choice(self.colors)

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                gem = self.board[r][c]
                if gem is None:
                    continue
                x0 = c * self.cell_size + 5
                y0 = r * self.cell_size + 5
                x1 = (c + 1) * self.cell_size - 5
                y1 = (r + 1) * self.cell_size - 5
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=gem, outline="black")
        if self.selected:
            sr, sc = self.selected
            x0 = sc * self.cell_size
            y0 = sr * self.cell_size
            x1 = (sc + 1) * self.cell_size
            y1 = (sr + 1) * self.cell_size
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="yellow", width=3)
        for (r, c) in self.hint_cells:
            x0 = c * self.cell_size
            y0 = r * self.cell_size
            x1 = (c + 1) * self.cell_size
            y1 = (r + 1) * self.cell_size
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="blue", width=3)
        self.label.config(
            text=f"Score: {self.score} | Time left: {self.time_left}s | Level: {self.level} | Goal: {self.level_goal}"
        )

    def update_timer(self):
        if self.time_left <= 0:
            if self.level_complete_button is None:
                self.in_action = True
                self.canvas.unbind("<Button-1>")
                self.label.config(text=f"Game Over! Final Score: {self.score}")
                self.restart_button = tk.Button(self.root, text="Play Again", command=self.restart_game)
                self.restart_button.pack(pady=10)
            return
        self.time_left -= 1
        self.draw_board()
        self.root.after(1000, self.update_timer)

    def on_canvas_click(self, event):
        if self.in_action:
            return
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        if self.board[row][col] == self.obstacle_color:
            return
        if self.selected is None:
            self.selected = (row, col)
            self.hint_cells = []
            self.draw_board()
        else:
            sr, sc = self.selected
            if (row, col) == (sr, sc):
                self.selected = None
                self.draw_board()
            elif abs(sr - row) + abs(sc - col) == 1 and self.board[row][col] != self.obstacle_color:
                self.in_action = True
                self.selected = None
                self.board[sr][sc], self.board[row][col] = self.board[row][col], self.board[sr][sc]
                self.draw_board()
                matches = self.find_matches()
                if matches:
                    self.root.after(100, self.remove_matches_and_continue, matches)
                else:
                    self.root.after(300, self.swap_back, sr, sc, row, col)
            else:
                self.selected = (row, col)
                self.draw_board()

    def swap_back(self, r1, c1, r2, c2):
        self.board[r1][c1], self.board[r2][c2] = self.board[r2][c2], self.board[r1][c1]
        self.in_action = False
        self.draw_board()

    def find_matches(self):
        self.bonus_matches = []  # Track bonus-eligible matches
        matches = set()
        for r in range(self.rows):
            for c in range(self.cols - 2):
                if self.board[r][c] in [None, self.obstacle_color]:
                    continue
                run = [c]
                while c + 1 < self.cols and self.board[r][c] == self.board[r][c + 1] and self.board[r][c + 1] != self.obstacle_color:
                    run.append(c + 1)
                    c += 1
                if len(run) >= 3:
                    matches.update((y, c) for y in run)
                    if len(run) == 4:
                        self.bonus_matches.append((run[0], c, 'vertical'))
                    elif len(run) >= 5:
                        self.bonus_matches.append((run[0], c, 'bomb'))
                    matches.update((r, x) for x in run)
                    if len(run) == 4:
                        self.bonus_matches.append((r, run[0], 'horizontal'))
                    elif len(run) >= 5:
                        self.bonus_matches.append((r, run[0], 'bomb'))
                    matches.update((r, x) for x in run)
        for c in range(self.cols):
            for r in range(self.rows - 2):
                if self.board[r][c] in [None, self.obstacle_color]:
                    continue
                run = [r]
                while r + 1 < self.rows and self.board[r][c] == self.board[r + 1][c] and self.board[r + 1][c] != self.obstacle_color:
                    run.append(r + 1)
                    r += 1
                if len(run) >= 3:
                    matches.update((y, c) for y in run)
                    if len(run) == 4:
                        self.bonus_matches.append((run[0], c, 'vertical'))
                    elif len(run) >= 5:
                        self.bonus_matches.append((run[0], c, 'bomb'))
                    matches.update((r, x) for x in run)
                    if len(run) == 4:
                        self.bonus_matches.append((r, run[0], 'horizontal'))
                    elif len(run) >= 5:
                        self.bonus_matches.append((r, run[0], 'bomb'))
                    matches.update((y, c) for y in run)
        return matches

    def remove_matches_and_continue(self, matches):
        # Place bonus blocks before removing
        for br, bc, bonus_type in self.bonus_matches:
            if bonus_type == 'horizontal':
                for col in range(self.cols):
                    if self.board[br][col] != self.obstacle_color:
                        self.board[br][col] = None
            elif bonus_type == 'vertical':
                for row in range(self.rows):
                    if self.board[row][bc] != self.obstacle_color:
                        self.board[row][bc] = None
            elif bonus_type == 'bomb':
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = br + dr, bc + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.board[nr][nc] != self.obstacle_color:
                                self.board[nr][nc] = None
        for r, c in matches:
            if self.board[r][c] != self.obstacle_color:
                self.board[r][c] = None
        self.score += len(matches) * 10 + len(self.bonus_matches) * 30
        self.draw_board()
        self.root.after(200, self.drop_gems)

    def drop_gems(self):
        moved = False
        for c in range(self.cols):
            for r in range(self.rows - 2, -1, -1):
                if self.board[r][c] != self.obstacle_color and self.board[r + 1][c] is None:
                    rr = r
                    while rr + 1 < self.rows and self.board[rr + 1][c] is None:
                        self.board[rr + 1][c] = self.board[rr][c]
                        self.board[rr][c] = None
                        rr += 1
                        moved = True

        # Repeat filling None cells until board is full (in case obstacles block upper cells)
        filled = False
        while True:
            filled = False
            for c in range(self.cols):
                for r in range(self.rows):
                    if self.board[r][c] is None:
                        self.board[r][c] = random.choice(self.colors)
                        filled = True
            if not any(self.board[r][c] is None for r in range(self.rows) for c in range(self.cols)):
                break

        self.draw_board()
        self.root.after(100, self.check_post_drop_matches)

    def check_post_drop_matches(self):
        matches = self.find_matches()
        if matches:
            self.root.after(100, self.remove_matches_and_continue, matches)
        elif self.score >= self.level_goal:
            self.in_action = True
            self.canvas.unbind("<Button-1>")
            self.label.config(text=f"\U0001F389 Level {self.level} complete! \U0001F389 Score: {self.score}")
            self.level_complete_button = tk.Button(self.root, text="Next Level ▶", command=self.advance_level)
            self.level_complete_button.pack(pady=10)
            self.time_left = -1
        else:
            self.in_action = False

    def advance_level(self):
        if self.level_complete_button:
            self.level_complete_button.destroy()
            self.level_complete_button = None
        self.level += 1
        self.level_goal += 200
        self.time_left = 150
        self.score = 0
        self.in_action = False
        self.hints_left += 1
        self.hint_button.config(text=f"Hint ({self.hints_left})")
        self.initialize_board()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.update_timer()

    def restart_game(self):
        if self.restart_button:
            self.restart_button.destroy()
        self.level = 1
        self.level_goal = 300
        self.time_left = 150
        self.score = 0
        self.hints_left = 3
        self.in_action = False
        self.hint_button.config(text=f"Hint ({self.hints_left})")
        self.initialize_board()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.update_timer()

    def show_hint(self):
        if self.hints_left <= 0 or self.in_action:
            return
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == self.obstacle_color:
                    continue
                for dr, dc in [(0, 1), (1, 0)]:
                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                        continue
                    if self.board[nr][nc] == self.obstacle_color:
                        continue
                    self.board[r][c], self.board[nr][nc] = self.board[nr][nc], self.board[r][c]
                    if self.find_matches():
                        self.hint_cells = [(r, c), (nr, nc)]
                        self.hints_left -= 1
                        self.hint_button.config(text=f"Hint ({self.hints_left})")
                        self.board[r][c], self.board[nr][nc] = self.board[nr][nc], self.board[r][c]
                        self.draw_board()
                        return
                    self.board[r][c], self.board[nr][nc] = self.board[nr][nc], self.board[r][c]

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Match-3 with Obstacles")
    game = Match3Game(root)
    root.mainloop()
