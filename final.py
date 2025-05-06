import tkinter as tk
import random

class Match3Game:
    def __init__(self, root, rows=8, cols=8, cell_size=40):
        # Initialize game parameters
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.colors = ["red", "green", "blue", "yellow", "purple", "orange"]
        self.obstacle_color = "gray"

        # Game state variables
        self.level = 1
        self.level_goal = 300
        self.time_left = 150
        self.score = 0
        self.selected = None
        self.in_action = False
        self.hints_left = 3
        self.hint_cells = []

        # Create game board (2D list)
        self.board = [[None] * self.cols for _ in range(self.rows)]

        # UI setup
        self.label = tk.Label(root)
        self.label.pack(pady=5)
        self.canvas = tk.Canvas(root, width=self.cols*cell_size, height=self.rows*cell_size, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.hint_button = tk.Button(root, text=f"Hint ({self.hints_left})", command=self.show_hint)
        self.hint_button.pack(pady=5)

        self.level_complete_button = None
        self.restart_button = None

        # Start game
        self.initialize_board()
        self.draw_board()
        self.update_timer()

    def initialize_board(self):
        """Initializes the game board with random colored gems and inserts obstacles from level 3 onward."""
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
        """Renders the current state of the board on the canvas."""
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
        """Decreases time_left each second and ends the game if time runs out."""
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
        """Handles tile selection and swapping on canvas click."""
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
        """Swaps two tiles back if the move didn’t result in a match."""
        self.board[r1][c1], self.board[r2][c2] = self.board[r2][c2], self.board[r1][c1]
        self.in_action = False
        self.draw_board()

    def find_matches(self):
        """Finds and returns all matching tiles of 3 or more, and registers bonus effects."""
        self.bonus_matches = []
        matches = set()

        # Horizontal match detection
        for r in range(self.rows):
            c = 0
            while c < self.cols - 2:
                if self.board[r][c] in [None, self.obstacle_color]:
                    c += 1
                    continue
                run_color = self.board[r][c]
                run = [c]
                j = c + 1
                while j < self.cols and self.board[r][j] == run_color:
                    run.append(j)
                    j += 1
                if len(run) >= 3:
                    for x in run:
                        matches.add((r, x))  # Add matched cells for removal
                    if len(run) == 4:
                        self.bonus_matches.append((r, run[1], 'horizontal'))  # Mid-point bonus
                    elif len(run) >= 5:
                        self.bonus_matches.append((r, run[2], 'bomb'))
                c = j

        # Vertical match detection
        for c in range(self.cols):
            r = 0
            while r < self.rows - 2:
                if self.board[r][c] in [None, self.obstacle_color]:
                    r += 1
                    continue
                run_color = self.board[r][c]
                run = [r]
                i = r + 1
                while i < self.rows and self.board[i][c] == run_color:
                    run.append(i)
                    i += 1
                if len(run) >= 3:
                    for y in run:
                        matches.add((y, c))  # Add matched cells for removal
                    if len(run) == 4:
                        self.bonus_matches.append((run[1], c, 'vertical'))
                    elif len(run) >= 5:
                        self.bonus_matches.append((run[2], c, 'bomb'))
                r = i

        return matches

    def remove_matches_and_continue(self, matches):
        """Removes all matched tiles and applies bonus effects before continuing."""
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
        """Makes gems fall into empty spaces and generates new ones at the top."""
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
        # Fill empty spots
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
        """Checks for matches after a drop and proceeds accordingly."""
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
        """Advances to the next level with updated parameters."""
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
        """Resets the game to its initial state."""
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
        """Provides a hint by highlighting a possible move."""
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
