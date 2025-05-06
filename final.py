import tkinter as tk
import random

class Match3Game:
    def __init__(self, root, rows=8, cols=8, cell_size=40, colors=None):
        self.level = 1
        self.level_goal = 300
        self.time_left = 150  # 初始时间更长
        self.level_complete_button = None  # 按钮容器
        self.level_complete_label = None

        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size

        if colors is None:
            colors = ["red", "green", "blue", "yellow", "purple", "orange"]
        self.colors = colors

        self.board = [[None] * cols for _ in range(rows)]
        self.score = 0
        self.selected = None
        self.in_action = False
        self.time_left = 120  # 2 minutes
        self.high_score = 0
        self.restart_button = None

        for r in range(rows):
            for c in range(cols):
                while True:
                    gem = random.choice(self.colors)
                    if c >= 2 and gem == self.board[r][c-1] == self.board[r][c-2]:
                        continue
                    if r >= 2 and gem == self.board[r-1][c] == self.board[r-2][c]:
                        continue
                    self.board[r][c] = gem
                    break

        self.label = tk.Label(root, text="Score: 0 | Time left: 120s | Level: 1 | Goal: 100")
        self.label.pack(pady=5)
        canvas_width = cols * cell_size
        canvas_height = rows * cell_size
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.draw_board()
        self.update_timer()

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
        if self.selected is not None:
            sr, sc = self.selected
            x0 = sc * self.cell_size
            y0 = sr * self.cell_size
            x1 = (sc + 1) * self.cell_size
            y1 = (sr + 1) * self.cell_size
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="yellow", width=3)
        self.label.config(
            text=f"Score: {self.score} | Time left: {self.time_left}s | Level: {self.level} | Goal: {self.level_goal}")

    def update_timer(self):
        # 如果已经通关了（time_left 被设为 -1），则不要继续计时
        if self.time_left <= 0:
            if self.level_complete_button is None:
                # 没有通关，只是时间到了
                self.in_action = True
                self.canvas.unbind("<Button-1>")
                self.label.config(text=f"Game Over! Final Score: {self.score}")
                self.restart_button = tk.Button(self.root, text="Play Again", command=self.restart_game)
                self.restart_button.pack(pady=10)
            return  # 无论哪种情况，终止后续计时

        # 正常倒计时进行
        self.time_left -= 1
        self.label.config(
            text=f"Score: {self.score} | Time left: {self.time_left}s | Level: {self.level} | Goal: {self.level_goal}")
        self.root.after(1000, self.update_timer)

    def on_canvas_click(self, event):
        if self.in_action:
            return
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        if self.selected is None:
            self.selected = (row, col)
            self.draw_board()
        else:
            if (row, col) == self.selected:
                self.selected = None
                self.draw_board()
            else:
                sr, sc = self.selected
                if abs(sr - row) + abs(sc - col) == 1:
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
        matches = set()
        for r in range(self.rows):
            c = 0
            while c < self.cols:
                if self.board[r][c] is None:
                    c += 1
                    continue
                run_color = self.board[r][c]
                j = c + 1
                while j < self.cols and self.board[r][j] == run_color:
                    j += 1
                if j - c >= 3:
                    for x in range(c, j):
                        matches.add((r, x))
                c = j
        for c in range(self.cols):
            r = 0
            while r < self.rows:
                if self.board[r][c] is None:
                    r += 1
                    continue
                run_color = self.board[r][c]
                i = r + 1
                while i < self.rows and self.board[i][c] == run_color:
                    i += 1
                if i - r >= 3:
                    for y in range(r, i):
                        matches.add((y, c))
                r = i
        return matches

    def advance_level(self):
        if self.level_complete_button:
            self.level_complete_button.destroy()
            self.level_complete_button = None

        if self.level_complete_label:
            self.level_complete_label.destroy()
            self.level_complete_label = None

        self.level += 1
        self.level_goal += 200  # 每关目标提升
        self.time_left = 150
        self.score = 0  # 新关卡重新计分
        self.selected = None
        self.in_action = False

        for r in range(self.rows):
            for c in range(self.cols):
                while True:
                    gem = random.choice(self.colors)
                    if c >= 2 and gem == self.board[r][c - 1] == self.board[r][c - 2]:
                        continue
                    if r >= 2 and gem == self.board[r - 1][c] == self.board[r - 2][c]:
                        continue
                    self.board[r][c] = gem
                    break

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.draw_board()
        self.update_timer()

    def remove_matches_and_continue(self, matches):
        for (r, c) in matches:
            self.board[r][c] = None
        self.score += len(matches) * 10
        self.draw_board()
        self.root.after(200, self.drop_gems)
        # 若已达目标分数，且按钮未创建，则创建按钮并停止计时
        if self.score >= self.level_goal:
            if self.level_complete_button is None:
                self.in_action = True
                self.canvas.unbind("<Button-1>")

                # 🔸 添加醒目的通关提示标签
                self.level_complete_label = tk.Label(self.root, text="🎉 Congratulations! Level Complete! 🎉",
                                                     font=("Helvetica", 18, "bold"), fg="green")
                self.level_complete_label.pack(pady=10)

                self.level_complete_button = tk.Button(self.root, text="Next Level ▶", command=self.advance_level)
                self.level_complete_button.pack(pady=10)
                self.time_left = -1  # 停止计时
            return

    def drop_gems(self):
        moved = False
        for c in range(self.cols):
            for r in range(self.rows - 1, 0, -1):
                if self.board[r][c] is None and self.board[r-1][c] is not None:
                    self.board[r][c] = self.board[r-1][c]
                    self.board[r-1][c] = None
                    moved = True
        if moved:
            self.draw_board()
            self.root.after(50, self.drop_gems)
        else:
            for c in range(self.cols):
                for r in range(self.rows):
                    if self.board[r][c] is None:
                        self.board[r][c] = random.choice(self.colors)
            self.draw_board()
            new_matches = self.find_matches()
            if new_matches:
                self.root.after(100, self.remove_matches_and_continue, new_matches)
            else:
                self.in_action = False


    def restart_game(self):
        self.score = 0
        self.level = 1
        self.level_goal = 300
        self.time_left = 150
        self.selected = None
        self.in_action = False

        for r in range(self.rows):
            for c in range(self.cols):
                while True:
                    gem = random.choice(self.colors)
                    if c >= 2 and gem == self.board[r][c - 1] == self.board[r][c - 2]:
                        continue
                    if r >= 2 and gem == self.board[r - 1][c] == self.board[r - 2][c]:
                        continue
                    self.board[r][c] = gem
                    break

        self.canvas.bind("<Button-1>", self.on_canvas_click)

        if self.restart_button:
            self.restart_button.destroy()
            self.restart_button = None
        if self.level_complete_button:
            self.level_complete_button.destroy()
            self.level_complete_button = None

        self.draw_board()
        self.update_timer()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Joy of Elimination - Match-3 Game")
    game = Match3Game(root)
    root.mainloop()

