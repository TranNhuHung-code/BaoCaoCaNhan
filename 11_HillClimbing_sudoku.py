# -*- coding: utf-8 -*-
"""
11_HillClimbing_sudoku.py
======================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: LOCAL SEARCH
Thuật toán trình bày: Hill Climbing (Steepest-Ascent)
Bài toán áp dụng: Giải Sudoku 9x9
"""

import tkinter as tk
from tkinter import messagebox
import time
import threading

from sudoku_utils import SIZE, BOX, generate_puzzle
from hill_climbing_solver import HillClimbingSolver


# ===================== CẤU HÌNH MÀU SẮC (Cyberpunk Theme) =====================
BG = "#080816"              
CARD = "#141630"            
ACCENT = "#00C6FF"          
TXT = "#D7DAE8"             
TXT_D = "#646987"           
TXT_B = "#FFFFFF"           

COLOR_CLUE_TEXT = "#A0A5D0"
COLOR_CLUE_BG = "#2A2D54"
COLOR_FILLED_BG = "#1A1C38"
COLOR_BETTER_BG = "#00E473"        
COLOR_BETTER_TEXT = "#000000"
COLOR_RESTART_FLASH = "#FF325A"
COLOR_SOLVED_BG = "#00E473"
COLOR_SOLVED_TEXT = "#000000"

FONT_CELL = ("Segoe UI", 18, "bold")
FONT_LABEL = ("Segoe UI", 12)
FONT_TITLE = ("Segoe UI", 16, "bold")


class HillClimbingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("11 - Hill Climbing (Local Search)")
        self.root.configure(bg=BG)

        self.puzzle, self.real_solution = generate_puzzle(num_clues=32, seed=None)
        self.solver = HillClimbingSolver(self.puzzle)

        self.steps = []
        self.current_step_idx = 0
        self.is_playing = False
        self.play_speed_ms = 100

        self.solved_board = None
        self.solve_stats = None

        self._build_ui()
        self._render_board(self.puzzle, is_initial=True)

    def _build_ui(self):
        title = tk.Label(self.root, text="11 - Hill Climbing | Sudoku 9x9",
                          font=FONT_TITLE, bg=BG, fg=ACCENT)
        title.pack(pady=(12, 4))

        subtitle = tk.Label(
            self.root,
            text="Nhóm 3: Local Search   |   Đồ án cuối kỳ môn Trí Tuệ Nhân Tạo",
            font=FONT_LABEL, bg=BG, fg=TXT_D
        )
        subtitle.pack(pady=(0, 10))

        grid_frame = tk.Frame(self.root, bg="#2A2D54", bd=2)
        grid_frame.pack(padx=12, pady=8)

        self.cell_labels = [[None] * SIZE for _ in range(SIZE)]
        for r in range(SIZE):
            for c in range(SIZE):
                pad_top = 3 if r % BOX == 0 else 1
                pad_left = 3 if c % BOX == 0 else 1
                pad_bottom = 3 if r == SIZE - 1 else 1
                pad_right = 3 if c == SIZE - 1 else 1

                cell = tk.Label(
                    grid_frame, text="", width=3, height=1,
                    font=FONT_CELL, bg=COLOR_FILLED_BG, fg=TXT_B,
                    relief="flat", borderwidth=0
                )
                cell.grid(row=r, column=c,
                          padx=(pad_left, pad_right), pady=(pad_top, pad_bottom),
                          sticky="nsew")
                self.cell_labels[r][c] = cell

        control_frame = tk.Frame(self.root, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        control_frame.pack(pady=10)

        self.btn_solve = tk.Button(control_frame, text="▶ Giải bằng Hill Climbing",
                                    command=self.on_solve_click,
                                    font=FONT_LABEL, bg="#0066FF", fg=TXT_B,
                                    activebackground="#0052CC", relief="flat", padx=10, pady=6)
        self.btn_solve.grid(row=0, column=0, padx=6, pady=6)

        self.btn_play = tk.Button(control_frame, text="⏵ Phát lại từng bước",
                                   command=self.on_play_click, state="disabled",
                                   font=FONT_LABEL, bg="#00E473", fg="black",
                                   activebackground="#00C463", relief="flat", padx=10, pady=6)
        self.btn_play.grid(row=0, column=1, padx=6)

        self.btn_skip = tk.Button(control_frame, text="⏭ Bỏ qua",
                                   command=self.on_skip_click, state="disabled",
                                   font=FONT_LABEL, bg=TXT_D, fg=TXT_B,
                                   activebackground="#4B5563", relief="flat", padx=10, pady=6)
        self.btn_skip.grid(row=0, column=2, padx=6)

        self.btn_new = tk.Button(control_frame, text="↻ Đề mới",
                                  command=self.on_new_puzzle_click,
                                  font=FONT_LABEL, bg="#FF325A", fg=TXT_B,
                                  activebackground="#CC2848", relief="flat", padx=10, pady=6)
        self.btn_new.grid(row=0, column=3, padx=6)

        speed_frame = tk.Frame(self.root, bg=BG)
        speed_frame.pack(pady=(0, 6))
        tk.Label(speed_frame, text="Tốc độ phát lại:", font=FONT_LABEL,
                 bg=BG, fg=TXT_B).pack(side="left", padx=(0, 8))
        self.speed_scale = tk.Scale(speed_frame, from_=1, to=200, orient="horizontal",
                                     length=220, bg=BG, fg=TXT_B,
                                     troughcolor=CARD, highlightthickness=0,
                                     command=self._on_speed_change)
        self.speed_scale.set(self.play_speed_ms)
        self.speed_scale.pack(side="left")

        self.info_label = tk.Label(self.root, text="Nhấn 'Giải bằng Hill Climbing' để bắt đầu.",
                                    font=FONT_LABEL, bg=BG, fg=TXT_B,
                                    justify="left")
        self.info_label.pack(pady=(4, 12))

    def _on_speed_change(self, val):
        self.play_speed_ms = int(val)

    def _render_board(self, board, highlight=None, is_initial=False):
        for r in range(SIZE):
            for c in range(SIZE):
                val = board[r][c]
                is_clue = self.puzzle[r][c] != 0
                label = self.cell_labels[r][c]

                label.config(text=str(val) if val != 0 else "")

                if is_clue:
                    label.config(bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT)
                elif is_initial:
                    label.config(bg=COLOR_FILLED_BG, fg=TXT_B)
                else:
                    label.config(bg=COLOR_FILLED_BG, fg=TXT_B)

        if highlight:
            r, c1, c2, action = highlight
            if r != -1 and c1 != -1 and c2 != -1:
                label1 = self.cell_labels[r][c1]
                label2 = self.cell_labels[r][c2]
                if action == 'accept_better':
                    label1.config(bg=COLOR_BETTER_BG, fg=COLOR_BETTER_TEXT)
                    label2.config(bg=COLOR_BETTER_BG, fg=COLOR_BETTER_TEXT)

    def _run_solver_thread(self):
        t0 = time.time()
        self.solved_board, self.steps, self.solve_stats = self.solver.solve()
        t1 = time.time()

        def on_done():
            self.btn_solve.config(state="normal", text="▶ Giải bằng Hill Climbing")
            msg = f"Đã chạy ngầm xong trong {round(t1 - t0, 3)}s."
            if self.solved_board:
                msg += f"\nTìm thấy lời giải! (Số restart: {self.solve_stats['restarts']})"
            else:
                msg += f"\nKhông hội tụ (Kẹt ở Local Optimum). Số restart: {self.solve_stats['restarts']}."
            
            self.info_label.config(text=msg)
            
            if self.steps:
                self.btn_play.config(state="normal")
                self.btn_skip.config(state="normal")

        self.root.after(0, on_done)

    def on_solve_click(self):
        self.btn_solve.config(state="disabled", text="Đang giải ngầm...")
        self.btn_play.config(state="disabled")
        self.btn_skip.config(state="disabled")
        self.info_label.config(text="Hệ thống đang chạy Hill Climbing. Vui lòng đợi...")
        threading.Thread(target=self._run_solver_thread, daemon=True).start()

    def on_play_click(self):
        if not self.steps: return
        if self.is_playing:
            self.is_playing = False
            self.btn_play.config(text="⏵ Tiếp tục")
            self.info_label.config(text="Đã tạm dừng.")
        else:
            self.is_playing = True
            self.btn_play.config(text="⏸ Tạm dừng")
            if self.current_step_idx >= len(self.steps):
                self.current_step_idx = 0
            self._play_next_step()

    def _play_next_step(self):
        if not self.is_playing: return

        if self.current_step_idx < len(self.steps):
            step = self.steps[self.current_step_idx]
            
            if step.action_type == 'restart':
                self.info_label.config(text=f"Kẹt ở Local Optimum. RESTART! (Xung đột = {step.h_value})")
                for r in range(SIZE):
                    for c in range(SIZE):
                        if self.puzzle[r][c] == 0:
                            self.cell_labels[r][c].config(bg=COLOR_RESTART_FLASH)
            elif step.action_type == 'stuck':
                self.info_label.config(text=f"Kẹt (Stuck)! Xung đột = {step.h_value}")
                self._render_board(step.board)
            else:
                self._render_board(step.board, highlight=(step.row, step.col1, step.col2, step.action_type))
                self.info_label.config(
                    text=f"Tìm thấy neighbor tốt hơn! Đổi 2 ô. "
                         f"Xung đột hiện tại: {step.h_value}"
                )
            
            self.current_step_idx += 1
            self.root.after(self.play_speed_ms, self._play_next_step)
        else:
            self.is_playing = False
            self.btn_play.config(text="⏵ Phát lại từ đầu", state="normal")
            if self.solved_board:
                self._render_board(self.solved_board)
                for r in range(SIZE):
                    for c in range(SIZE):
                        if self.puzzle[r][c] == 0:
                            self.cell_labels[r][c].config(bg=COLOR_SOLVED_BG, fg=COLOR_SOLVED_TEXT)
                self.info_label.config(text="HOÀN THÀNH: Đã giải thành công!")
            else:
                self.info_label.config(text="HOÀN THÀNH: Không hội tụ (kẹt Local Optimum).")

    def on_skip_click(self):
        self.is_playing = False
        self.btn_play.config(text="⏵ Phát lại từ đầu", state="normal")
        self.current_step_idx = len(self.steps)
        
        if self.solved_board:
            self._render_board(self.solved_board)
            for r in range(SIZE):
                for c in range(SIZE):
                    if self.puzzle[r][c] == 0:
                        self.cell_labels[r][c].config(bg=COLOR_SOLVED_BG, fg=COLOR_SOLVED_TEXT)
            self.info_label.config(text="Đã nhảy đến kết quả. Giải thành công!")
        else:
            last_board = self.steps[-1].board if self.steps else self.puzzle
            self._render_board(last_board)
            self.info_label.config(text="Đã nhảy đến kết quả. KHÔNG HỘI TỤ.")

    def on_new_puzzle_click(self):
        self.is_playing = False
        self.puzzle, self.real_solution = generate_puzzle(num_clues=32, seed=None)
        self.solver = HillClimbingSolver(self.puzzle)
        self.steps = []
        self.current_step_idx = 0
        self.solved_board = None
        self.solve_stats = None

        self._render_board(self.puzzle, is_initial=True)
        self.btn_solve.config(state="normal", text="▶ Giải bằng Hill Climbing")
        self.btn_play.config(state="disabled", text="⏵ Phát lại từng bước")
        self.btn_skip.config(state="disabled")
        self.info_label.config(text="Đã tạo đề mới. Nhấn 'Giải bằng Hill Climbing' để bắt đầu.")

def main():
    root = tk.Tk()
    app = HillClimbingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
