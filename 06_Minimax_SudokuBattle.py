# -*- coding: utf-8 -*-
"""
06_Minimax_SudokuBattle.py
============================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: ADVERSARIAL SEARCH (Tìm kiếm đối kháng)
Thuật toán trình bày: Minimax (có giới hạn độ sâu)
Bài toán áp dụng: "SUDOKU BATTLE" — biến thể 2 người chơi (Người vs Agent)

----------------------------------------------------------------------
LUẬT CHƠI "SUDOKU BATTLE":
    - Người và Agent luân phiên điền số vào bảng Sudoku.
    - Mỗi lượt, bên đến lượt chọn 1 ô trống và điền 1 số (1-9).
    - Hết ô trống, bên nào điền ĐÚNG (so với lời giải thật) NHIỀU HƠN thì THẮNG.
    - Agent dùng MINIMAX có giới hạn độ sâu + hàm đánh giá để chọn nước đi tối ưu.
    - Người chơi được xem là MIN (worst-case), Agent là MAX.

CÁCH CHƠI:
    1. Click vào 1 ô trống trên bàn cờ để chọn ô.
    2. Nhập số 1-9 vào ô nhập, nhấn "Xác nhận" hoặc Enter.
    3. Đến lượt Agent: tự động suy luận bằng Minimax và điền số.
    4. Xem log suy luận của Agent ở khung bên phải.

CÁCH CHẠY:
    python 06_Minimax_SudokuBattle.py

YÊU CẦU: Python 3.x có sẵn tkinter.
----------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import messagebox
import time
import threading

from sudoku_utils import SIZE, BOX, generate_puzzle
from minimax_solver import MinimaxSudokuBattle

# ===================== CẤU HÌNH MÀU SẮC (Cyberpunk Theme) =====================
BG          = "#080816"
CARD        = "#141630"
ACCENT      = "#00C6FF"
TXT         = "#D7DAE8"
TXT_D       = "#646987"
TXT_B       = "#FFFFFF"

COLOR_CLUE_BG      = "#2A2D54"
COLOR_CLUE_TEXT    = "#A0A5D0"
COLOR_EMPTY_BG     = "#1A1C38"
COLOR_SELECTED_BG  = "#0066FF"

# Màu ô đã điền
COLOR_HUMAN_CORRECT_BG   = "#00E473"   # Xanh lá — người điền đúng
COLOR_HUMAN_CORRECT_TEXT = "#000000"
COLOR_HUMAN_WRONG_BG     = "#FFBE00"   # Vàng — người điền sai
COLOR_HUMAN_WRONG_TEXT   = "#4A3800"

COLOR_AGENT_CORRECT_BG   = "#1d4ed8"   # Xanh dương — agent điền đúng
COLOR_AGENT_CORRECT_TEXT = "#FFFFFF"
COLOR_AGENT_WRONG_BG     = "#FF325A"   # Đỏ — agent điền sai
COLOR_AGENT_WRONG_TEXT   = "#FFFFFF"

FONT_CELL   = ("Segoe UI", 16, "bold")
FONT_LABEL  = ("Segoe UI", 11)
FONT_TITLE  = ("Segoe UI", 16, "bold")
FONT_SCORE  = ("Segoe UI", 13, "bold")
FONT_LOG    = ("Consolas", 9)


class MinimaxBattleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("06 - Sudoku Battle: Minimax (Người vs Agent)")
        self.root.configure(bg=BG)
        self.root.geometry("1160x700")

        self._init_game_state()
        self._build_ui()
        self._render_board()
        self._update_score_label()
        self._update_turn_indicator()

    # ------------------------------------------------------------------
    def _init_game_state(self):
        self.puzzle, self.real_solution = generate_puzzle(num_clues=48, seed=None)
        self.game = MinimaxSudokuBattle(
            self.puzzle, self.real_solution,
            search_depth=3, candidate_cells_per_turn=6
        )
        self.selected_cell    = None
        self.is_human_turn    = True
        self.is_agent_thinking = False
        self.game_over        = False
        # Theo dõi ai điền từng ô để tô màu đúng sau khi render lại
        self.cell_owner  = {}   # (r,c) -> 'human' | 'agent'
        self.cell_correct = {}  # (r,c) -> True | False

    # ------------------------------------------------------------------
    def _build_ui(self):
        # --- Header ---
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill=tk.X, pady=(12, 4))

        tk.Label(header, text="Sudoku Battle: You vs Minimax AI",
                 font=FONT_TITLE, bg=BG, fg=ACCENT).pack()
        tk.Label(header,
                 text="Nhóm 6: Adversarial Search  |  Minimax (độ sâu 3)  |  "
                      "Bạn (🟢Xanh) đi trước — AI (🔵Xanh dương) đi sau",
                 font=FONT_LABEL, bg=BG, fg=TXT_D).pack()

        # --- Body ---
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=15, pady=6)

        # ====== CỘT TRÁI: Bàn cờ + điều khiển ======
        left = tk.Frame(body, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.Y)

        # Thanh điểm
        score_frame = tk.Frame(left, bg=CARD,
                                highlightbackground=ACCENT, highlightthickness=1)
        score_frame.pack(fill=tk.X, padx=4, pady=(0, 8))

        self.human_score_label = tk.Label(
            score_frame, text="👤 Người: 0",
            font=FONT_SCORE, bg=CARD, fg=COLOR_HUMAN_CORRECT_BG)
        self.human_score_label.pack(side=tk.LEFT, padx=20, pady=8)

        self.turn_label = tk.Label(
            score_frame, text="⟵ Lượt của bạn",
            font=FONT_LABEL, bg=CARD, fg=TXT_B)
        self.turn_label.pack(side=tk.LEFT, expand=True)

        self.agent_score_label = tk.Label(
            score_frame, text="🤖 Agent: 0",
            font=FONT_SCORE, bg=CARD, fg=COLOR_AGENT_CORRECT_BG)
        self.agent_score_label.pack(side=tk.RIGHT, padx=20, pady=8)

        # Bảng Sudoku
        grid_outer = tk.Frame(left, bg=CARD,
                               highlightbackground=ACCENT, highlightthickness=1)
        grid_outer.pack(padx=4, pady=4)

        grid_frame = tk.Frame(grid_outer, bg="#2A2D54", bd=2)
        grid_frame.pack(padx=12, pady=12)

        self.cell_labels = [[None] * SIZE for _ in range(SIZE)]
        for r in range(SIZE):
            for c in range(SIZE):
                pt = 3 if r % BOX == 0 else 1
                pl = 3 if c % BOX == 0 else 1
                pb = 3 if r == SIZE - 1 else 1
                pr = 3 if c == SIZE - 1 else 1

                cell = tk.Label(
                    grid_frame, text="", width=3, height=1,
                    font=FONT_CELL, bg=COLOR_EMPTY_BG, fg=TXT_B,
                    relief="flat", borderwidth=0, cursor="hand2"
                )
                cell.grid(row=r, column=c,
                          padx=(pl, pr), pady=(pt, pb), sticky="nsew")
                cell.bind("<Button-1>",
                          lambda e, rr=r, cc=c: self.on_cell_click(rr, cc))
                self.cell_labels[r][c] = cell

        # Nhập liệu
        input_frame = tk.Frame(left, bg=BG)
        input_frame.pack(fill=tk.X, padx=4, pady=8)

        tk.Label(input_frame, text="Ô chọn:", font=FONT_LABEL,
                 bg=BG, fg=TXT_D).grid(row=0, column=0, padx=4, sticky="w")
        self.selected_cell_label = tk.Label(
            input_frame, text="(chưa chọn)", font=FONT_LABEL, bg=BG, fg=TXT_B)
        self.selected_cell_label.grid(row=0, column=1, padx=4)

        tk.Label(input_frame, text="Số (1-9):", font=FONT_LABEL,
                 bg=BG, fg=TXT_D).grid(row=0, column=2, padx=4)
        self.value_entry = tk.Entry(
            input_frame, width=4, font=FONT_LABEL,
            bg=CARD, fg=TXT_B, insertbackground=TXT_B)
        self.value_entry.grid(row=0, column=3, padx=4)
        self.value_entry.bind("<Return>", lambda e: self.on_confirm_human_move())

        btn_style = dict(font=FONT_LABEL, relief="flat", padx=10, pady=5, cursor="hand2")
        self.btn_confirm = tk.Button(
            input_frame, text="✓ Xác nhận",
            command=self.on_confirm_human_move,
            bg="#00E473", fg="black", activebackground="#00C463", **btn_style)
        self.btn_confirm.grid(row=0, column=4, padx=8)

        # Nút điều khiển
        ctrl_frame = tk.Frame(left, bg=BG)
        ctrl_frame.pack(fill=tk.X, padx=4, pady=4)

        self.btn_auto_play = tk.Button(
            ctrl_frame, text="🤖 Agent tự đánh thay bạn (1 nước)",
            command=self.on_auto_human_move,
            bg=TXT_D, fg=TXT_B, activebackground="#4B5563", **btn_style)
        self.btn_auto_play.pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(
            ctrl_frame, text="↻ Trận mới",
            command=self.on_new_game_click,
            bg="#FF325A", fg=TXT_B, activebackground="#CC2848", **btn_style
        ).pack(side=tk.LEFT)

        # Info
        self.info_label = tk.Label(
            left, text="Lượt của Bạn! Click chọn ô, nhập số rồi xác nhận (hoặc Enter).",
            font=FONT_LABEL, bg=BG, fg=ACCENT, wraplength=520, justify="left")
        self.info_label.pack(anchor="w", padx=4, pady=4)

        # Chú thích màu
        legend_frame = tk.Frame(left, bg=BG)
        legend_frame.pack(anchor="w", padx=4, pady=2)
        for color, label in [
            (COLOR_HUMAN_CORRECT_BG,  "Người đúng"),
            (COLOR_HUMAN_WRONG_BG,    "Người sai"),
            (COLOR_AGENT_CORRECT_BG,  "AI đúng"),
            (COLOR_AGENT_WRONG_BG,    "AI sai"),
            (COLOR_CLUE_BG,           "Đề bài"),
        ]:
            dot = tk.Label(legend_frame, text="■", font=("Segoe UI", 12),
                           bg=BG, fg=color)
            dot.pack(side=tk.LEFT, padx=(4, 1))
            tk.Label(legend_frame, text=label, font=("Segoe UI", 9),
                     bg=BG, fg=TXT_D).pack(side=tk.LEFT, padx=(0, 8))

        # ====== CỘT PHẢI: Log ======
        right = tk.Frame(body, bg=CARD,
                          highlightbackground=ACCENT, highlightthickness=1)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))

        tk.Label(right, text="🧠 Log suy luận Minimax của Agent",
                 font=(FONT_LABEL[0], 12, "bold"), bg=CARD, fg=TXT_B
                 ).pack(anchor="w", padx=12, pady=(8, 4))

        self.log_text = tk.Text(
            right, font=FONT_LOG, bg=BG, fg=TXT,
            state=tk.DISABLED, wrap=tk.WORD, bd=0)
        scrollbar = tk.Scrollbar(right, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                            padx=(12, 0), pady=(0, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=(0, 10))

        # Tag màu log
        self.log_text.tag_configure("human",   foreground=COLOR_HUMAN_CORRECT_BG)
        self.log_text.tag_configure("agent",   foreground=ACCENT)
        self.log_text.tag_configure("result",  foreground="#FFBE00")
        self.log_text.tag_configure("info",    foreground=TXT_D)
        self.log_text.tag_configure("win",     foreground="#00E473")
        self.log_text.tag_configure("lose",    foreground=COLOR_AGENT_WRONG_BG)

    # ------------------------------------------------------------------
    def _log(self, text, tag="info"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _update_score_label(self):
        self.human_score_label.config(
            text=f"👤 Người: {self.game.human_score}")
        self.agent_score_label.config(
            text=f"🤖 Agent: {self.game.agent_score}")

    def _update_turn_indicator(self):
        if self.game_over:
            self.turn_label.config(text="🏁 Trận đấu kết thúc")
        elif self.is_human_turn:
            self.turn_label.config(text="⟵ Lượt của bạn")
        else:
            self.turn_label.config(text="⟶ Lượt của AI")

    # ------------------------------------------------------------------
    def _render_board(self):
        for r in range(SIZE):
            for c in range(SIZE):
                val   = self.game.board[r][c]
                label = self.cell_labels[r][c]
                is_clue = self.puzzle[r][c] != 0

                label.config(text=str(val) if val != 0 else "")

                if self.selected_cell == (r, c):
                    label.config(bg=COLOR_SELECTED_BG, fg=TXT_B)
                elif is_clue:
                    label.config(bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT)
                elif val == 0:
                    label.config(bg=COLOR_EMPTY_BG, fg=TXT_B)
                elif (r, c) in self.cell_owner:
                    owner   = self.cell_owner[(r, c)]
                    correct = self.cell_correct.get((r, c), False)
                    if owner == "human":
                        bg = COLOR_HUMAN_CORRECT_BG if correct else COLOR_HUMAN_WRONG_BG
                        fg = COLOR_HUMAN_CORRECT_TEXT if correct else COLOR_HUMAN_WRONG_TEXT
                    else:
                        bg = COLOR_AGENT_CORRECT_BG if correct else COLOR_AGENT_WRONG_BG
                        fg = COLOR_AGENT_CORRECT_TEXT if correct else COLOR_AGENT_WRONG_TEXT
                    label.config(bg=bg, fg=fg)

    # ------------------------------------------------------------------
    def on_cell_click(self, row, col):
        if self.game_over or not self.is_human_turn or self.is_agent_thinking:
            return
        if self.game.board[row][col] != 0:
            return
        self.selected_cell = (row, col)
        self.selected_cell_label.config(text=f"(hàng {row+1}, cột {col+1})")
        self.value_entry.focus_set()
        self._render_board()

    def on_confirm_human_move(self):
        if self.game_over or not self.is_human_turn or self.is_agent_thinking:
            return
        if self.selected_cell is None:
            messagebox.showinfo("Chưa chọn ô", "Bạn cần click chọn 1 ô trống trước.")
            return

        raw = self.value_entry.get().strip()
        if not raw.isdigit() or not (1 <= int(raw) <= 9):
            messagebox.showinfo("Giá trị không hợp lệ",
                                "Vui lòng nhập một số nguyên từ 1 đến 9.")
            return

        value = int(raw)
        row, col = self.selected_cell

        is_correct = self.game.human_move(row, col, value)
        self.cell_owner[(row, col)]   = "human"
        self.cell_correct[(row, col)] = is_correct

        tag = "human" if is_correct else "result"
        self._log(
            f"👤 Bạn điền {value} tại (hàng {row+1}, cột {col+1}) "
            f"→ {'ĐÚNG ✓' if is_correct else 'SAI ✗'}", tag)

        self.selected_cell = None
        self.selected_cell_label.config(text="(chưa chọn)")
        self.value_entry.delete(0, tk.END)
        self._render_board()
        self._update_score_label()

        if self.game.is_game_over():
            self._end_game()
            return

        self.is_human_turn = False
        self._update_turn_indicator()
        self.info_label.config(text="Agent đang suy luận bằng Minimax, vui lòng chờ...")
        self.root.after(300, self._agent_turn)

    def on_auto_human_move(self):
        """Cho AI tự chọn ô tốt nhất thay người (dùng minimax)."""
        if self.game_over or not self.is_human_turn or self.is_agent_thinking:
            return
        self.is_human_turn = False
        self._update_turn_indicator()
        self.info_label.config(text="Đang tính nước đi tốt nhất cho bạn...")

        def run():
            row, col, value, _ = self.game.agent_choose_move()
            is_correct = self.game.human_move(row, col, value)
            self.cell_owner[(row, col)]   = "human"
            self.cell_correct[(row, col)] = is_correct
            self.root.after(0, lambda: self._after_auto_human(row, col, value, is_correct))

        threading.Thread(target=run, daemon=True).start()

    def _after_auto_human(self, row, col, value, is_correct):
        tag = "human" if is_correct else "result"
        self._log(
            f"🤖→👤 Tự chơi: điền {value} tại (hàng {row+1}, cột {col+1}) "
            f"→ {'ĐÚNG ✓' if is_correct else 'SAI ✗'}", tag)
        self._render_board()
        self._update_score_label()
        if self.game.is_game_over():
            self._end_game()
            return
        self.is_human_turn = False
        self._update_turn_indicator()
        self.info_label.config(text="Agent đang suy luận bằng Minimax...")
        self.root.after(300, self._agent_turn)

    # ------------------------------------------------------------------
    def _agent_turn(self):
        self.is_agent_thinking = True

        def run_agent():
            t0 = time.time()
            result = self.game.agent_choose_move()
            t1 = time.time()
            if result is None:
                self.root.after(0, self._end_game)
                return
            row, col, value, trace = result
            is_correct = self.game.agent_move(row, col, value)
            self.root.after(
                0, lambda: self._on_agent_move_done(row, col, value, is_correct, trace, t1 - t0))

        threading.Thread(target=run_agent, daemon=True).start()

    def _on_agent_move_done(self, row, col, value, is_correct, trace, elapsed):
        self.cell_owner[(row, col)]   = "agent"
        self.cell_correct[(row, col)] = is_correct
        self._render_board()
        self._update_score_label()

        self._log(
            f"🤖 Agent (Minimax, depth={self.game.search_depth}) | "
            f"{elapsed:.3f}s | {self.game.nodes_evaluated:,} nodes:", "agent")
        for t in trace[:5]:
            self._log(f"   • Ô({t['row']+1},{t['col']+1})={t['value']} "
                       f"→ score={t['score']}", "info")
        self._log(
            f"   ➜ CHỌN: {value} tại (hàng {row+1}, cột {col+1}) "
            f"→ {'ĐÚNG ✓' if is_correct else 'SAI ✗'}", "agent")
        self._log("", "info")

        self.is_agent_thinking = False

        if self.game.is_game_over():
            self._end_game()
            return

        self.is_human_turn = True
        self._update_turn_indicator()
        self.info_label.config(
            text="Lượt của Bạn! Click chọn ô, nhập số rồi xác nhận (hoặc Enter).")

    # ------------------------------------------------------------------
    def _end_game(self):
        self.game_over = True
        h, a = self.game.human_score, self.game.agent_score
        total = h + a
        if h > a:
            result_text = f"🎉 NGƯỜI THẮNG!  {h} - {a}"
            tag = "win"
        elif a > h:
            result_text = f"🤖 AGENT THẮNG!  {a} - {h}"
            tag = "lose"
        else:
            result_text = f"🤝 HÒA!  {h} - {a}"
            tag = "result"

        self.info_label.config(text=f"TRẬN ĐẤU KẾT THÚC — {result_text}")
        self._log(f"\n{'='*40}", "info")
        self._log(f"KẾT QUẢ: {result_text}", tag)
        self._log(f"Người điền đúng {h}/{total} ô | Agent điền đúng {a}/{total} ô", "info")
        self._log(f"Tổng nodes Minimax đã đánh giá: {self.game.nodes_evaluated:,}", "info")
        self._update_turn_indicator()
        messagebox.showinfo("Kết thúc trận đấu", result_text)

    # ------------------------------------------------------------------
    def on_new_game_click(self):
        if self.is_agent_thinking:
            return
        self._init_game_state()
        self._render_board()
        self._update_score_label()
        self._update_turn_indicator()
        self.selected_cell_label.config(text="(chưa chọn)")
        self.value_entry.delete(0, tk.END)
        self.info_label.config(
            text="Trận mới! Lượt của Người. Click chọn ô, nhập số rồi xác nhận.")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self._log("Trận mới bắt đầu. Chúc bạn may mắn!", "win")


def main():
    root = tk.Tk()
    app = MinimaxBattleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
