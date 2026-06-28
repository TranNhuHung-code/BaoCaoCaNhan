# -*- coding: utf-8 -*-
"""
base_gui.py
============
Lớp giao diện cơ sở cho tất cả các thuật toán giải Sudoku (nhóm 1-5).
Layout 2 cột: Bảng Sudoku bên trái, Log + Controls bên phải.
Log hiển thị rõ 3 loại sự kiện: TRY (thử), BACKTRACK (quay lui), DEAD-END.
"""

import tkinter as tk
from tkinter import messagebox
import time
import threading
import copy

from sudoku_utils import generate_puzzle, SIZE, BOX

# ========================= MÀU SẮC =========================
BG       = "#080816"
CARD     = "#141630"
ACCENT   = "#00C6FF"
TXT      = "#D7DAE8"
TXT_D    = "#646987"
TXT_B    = "#FFFFFF"

COLOR_EMPTY_BG        = "#1A1C38"
COLOR_CLUE_BG         = "#2A2D54"
COLOR_CLUE_TEXT       = "#A0A5D0"
COLOR_TRY_BG          = "#FFBE00"
COLOR_TRY_TEXT        = "#4A3800"
COLOR_BACKTRACK_BG    = "#FF325A"
COLOR_BACKTRACK_TEXT  = "#FFFFFF"
COLOR_DEAD_END_BG     = "#7F1D1D"
COLOR_DEAD_END_TEXT   = "#FCA5A5"
COLOR_SOLVED_BG       = "#00E473"
COLOR_SOLVED_TEXT     = "#000000"
COLOR_NEW_ITER_FLASH  = "#00B9FF"

FONT_CELL  = ("Segoe UI", 18, "bold")
FONT_LABEL = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI", 15, "bold")
FONT_SUB   = ("Segoe UI", 9)
FONT_LOG   = ("Consolas", 9)

# Giới hạn log hiển thị để tránh lag khi bước quá nhiều
MAX_LOG_LINES = 2000


class BaseSudokuApp:
    def __init__(self, root, title, subtitle, algo_name,
                 solver_class, num_clues=35):
        self.root = root
        self.root.title(title)
        self.root.configure(bg=BG)
        self.root.geometry("1100x680")
        self.root.resizable(True, True)

        self.title_text    = title
        self.subtitle_text = subtitle
        self.algo_name     = algo_name
        self.solver_class  = solver_class
        self.num_clues     = num_clues

        self.puzzle, self.real_solution = generate_puzzle(
            num_clues=num_clues, seed=None)
        self.solver = self.solver_class(self.puzzle)

        self.steps               = []
        self.stats               = {}
        self.solution_board      = None
        self.is_solving          = False
        self.is_playing          = False
        self.is_paused           = False
        self.current_step_index  = -1
        self.play_speed_ms       = 40

        # Bộ đếm log
        self._log_try_count      = 0
        self._log_bt_count       = 0
        self._log_dead_count     = 0
        self._log_lines          = 0

        self._build_ui()
        self._render_board(self.puzzle)

    # ================================================================
    def _build_ui(self):
        # ---- Header ----
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill=tk.X, pady=(10, 4))
        tk.Label(hdr, text=self.title_text,
                 font=FONT_TITLE, bg=BG, fg=ACCENT).pack()
        tk.Label(hdr, text=self.subtitle_text,
                 font=FONT_SUB, bg=BG, fg=TXT_D).pack()

        # ---- Body: 2 cột ----
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        # ===== CỘT TRÁI: bảng Sudoku =====
        left = tk.Frame(body, bg=CARD,
                        highlightbackground=ACCENT, highlightthickness=1)
        left.pack(side=tk.LEFT, padx=(0, 10), pady=0, fill=tk.Y)

        grid_wrap = tk.Frame(left, bg=CARD)
        grid_wrap.pack(padx=14, pady=14)

        grid_frame = tk.Frame(grid_wrap, bg="#2A2D54")
        grid_frame.pack()

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
                    relief="flat", borderwidth=0)
                cell.grid(row=r, column=c,
                          padx=(pl, pr), pady=(pt, pb), sticky="nsew")
                self.cell_labels[r][c] = cell

        # Chú thích màu dưới bảng
        legend = tk.Frame(left, bg=CARD)
        legend.pack(padx=10, pady=(0, 10))
        for color, label in [
            (COLOR_TRY_BG,       "Đang thử"),
            (COLOR_BACKTRACK_BG, "Quay lui"),
            (COLOR_DEAD_END_BG,  "Dead-end"),
            (COLOR_SOLVED_BG,    "Xác định"),
            (COLOR_CLUE_BG,      "Đề bài"),
        ]:
            tk.Label(legend, text="■", font=("Segoe UI", 11),
                     bg=CARD, fg=color).pack(side=tk.LEFT, padx=(4, 1))
            tk.Label(legend, text=label, font=("Segoe UI", 8),
                     bg=CARD, fg=TXT_D).pack(side=tk.LEFT, padx=(0, 8))

        # ===== CỘT PHẢI: controls + stats + log =====
        right = tk.Frame(body, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Panel điều khiển ---
        ctrl = tk.Frame(right, bg=CARD,
                        highlightbackground=ACCENT, highlightthickness=1)
        ctrl.pack(fill=tk.X, pady=(0, 8))

        btn_cfg = dict(font=FONT_LABEL, relief="flat",
                       padx=8, pady=5, cursor="hand2")

        # Hàng 1: các nút chính
        row1 = tk.Frame(ctrl, bg=CARD)
        row1.pack(fill=tk.X, padx=8, pady=(8, 4))

        self.btn_solve = tk.Button(
            row1, text=f"▶ Giải ({self.algo_name})",
            command=self.on_solve_click,
            bg="#0066FF", fg=TXT_B, activebackground="#0052CC", **btn_cfg)
        self.btn_solve.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_play = tk.Button(
            row1, text="⏵ Phát lại", state="disabled",
            command=self.on_play_click,
            bg="#00E473", fg="black", activebackground="#00C463", **btn_cfg)
        self.btn_play.pack(side=tk.LEFT, padx=5)

        self.btn_pause = tk.Button(
            row1, text="⏸ Tạm dừng", state="disabled",
            command=self.on_pause_click,
            bg="#FFBE00", fg="black", activebackground="#D9A200", **btn_cfg)
        self.btn_pause.pack(side=tk.LEFT, padx=5)

        self.btn_skip = tk.Button(
            row1, text="⏭ Bỏ qua", state="disabled",
            command=self.on_skip_click,
            bg=TXT_D, fg=TXT_B, activebackground="#4B5563", **btn_cfg)
        self.btn_skip.pack(side=tk.LEFT, padx=5)

        self.btn_new = tk.Button(
            row1, text="↻ Đề mới",
            command=self.on_new_puzzle_click,
            bg="#FF325A", fg=TXT_B, activebackground="#CC2848", **btn_cfg)
        self.btn_new.pack(side=tk.LEFT, padx=(5, 0))

        # Hàng 2: tốc độ + bộ lọc log
        row2 = tk.Frame(ctrl, bg=CARD)
        row2.pack(fill=tk.X, padx=8, pady=(0, 8))

        tk.Label(row2, text="Tốc độ:", font=FONT_LABEL,
                 bg=CARD, fg=TXT_D).pack(side=tk.LEFT)
        self.speed_scale = tk.Scale(
            row2, from_=1, to=300, orient="horizontal",
            length=200, bg=CARD, fg=TXT_B, troughcolor=BG,
            highlightthickness=0, command=self._on_speed_change)
        self.speed_scale.set(self.play_speed_ms)
        self.speed_scale.pack(side=tk.LEFT, padx=(4, 16))

        tk.Label(row2, text="Lọc log:", font=FONT_LABEL,
                 bg=CARD, fg=TXT_D).pack(side=tk.LEFT)

        self._filter_try      = tk.BooleanVar(value=True)
        self._filter_bt       = tk.BooleanVar(value=True)
        self._filter_dead     = tk.BooleanVar(value=True)

        for var, label, color in [
            (self._filter_try,  "Thử",      COLOR_TRY_BG),
            (self._filter_bt,   "Quay lui",  COLOR_BACKTRACK_BG),
            (self._filter_dead, "Dead-end",  COLOR_DEAD_END_BG),
        ]:
            cb = tk.Checkbutton(row2, text=label, variable=var,
                                font=FONT_LABEL, bg=CARD, fg=color,
                                selectcolor=CARD, activebackground=CARD,
                                command=self._on_filter_change)
            cb.pack(side=tk.LEFT, padx=4)

        # --- Info bar ---
        self.info_label = tk.Label(
            right, text="Sẵn sàng. Nhấn ▶ Giải để bắt đầu.",
            font=FONT_LABEL, bg=BG, fg=ACCENT,
            anchor="w", justify="left", wraplength=560)
        self.info_label.pack(fill=tk.X, pady=(0, 6))

        # --- Thanh thống kê nhanh ---
        stats_bar = tk.Frame(right, bg=CARD,
                             highlightbackground=ACCENT, highlightthickness=1)
        stats_bar.pack(fill=tk.X, pady=(0, 6))

        self._stat_try_lbl  = self._make_stat(stats_bar, "Thử",      "0", COLOR_TRY_BG)
        self._stat_bt_lbl   = self._make_stat(stats_bar, "Quay lui",  "0", COLOR_BACKTRACK_BG)
        self._stat_dead_lbl = self._make_stat(stats_bar, "Dead-end",  "0", COLOR_DEAD_END_BG)
        self._stat_time_lbl = self._make_stat(stats_bar, "Thời gian", "—", ACCENT)
        self._stat_step_lbl = self._make_stat(stats_bar, "Bước",      "—", TXT_D)

        # --- Log ---
        log_frame = tk.Frame(right, bg=CARD,
                             highlightbackground=ACCENT, highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True)

        log_hdr = tk.Frame(log_frame, bg=CARD)
        log_hdr.pack(fill=tk.X, padx=8, pady=(6, 2))
        tk.Label(log_hdr, text="📋 Log tìm kiếm",
                 font=(FONT_LABEL[0], 10, "bold"),
                 bg=CARD, fg=TXT_B).pack(side=tk.LEFT)
        tk.Button(log_hdr, text="Xóa log",
                  command=self._clear_log,
                  font=("Segoe UI", 8), relief="flat",
                  bg=TXT_D, fg=TXT_B, cursor="hand2",
                  padx=6, pady=2).pack(side=tk.RIGHT)

        self.log_text = tk.Text(
            log_frame, font=FONT_LOG, bg=BG, fg=TXT,
            state=tk.DISABLED, wrap=tk.WORD, bd=0)
        sb = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                           padx=(8, 0), pady=(0, 8))
        sb.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=(0, 8))

        # Tags màu log
        self.log_text.tag_configure("info",     foreground=TXT_D)
        self.log_text.tag_configure("try",      foreground=COLOR_TRY_BG)
        self.log_text.tag_configure("backtrack",foreground=COLOR_BACKTRACK_BG)
        self.log_text.tag_configure("dead",     foreground=COLOR_DEAD_END_TEXT,
                                    background=COLOR_DEAD_END_BG)
        self.log_text.tag_configure("success",  foreground=COLOR_SOLVED_BG)
        self.log_text.tag_configure("iter",     foreground=COLOR_NEW_ITER_FLASH)

    # ================================================================
    def _make_stat(self, parent, label, value, color):
        f = tk.Frame(parent, bg=CARD)
        f.pack(side=tk.LEFT, padx=12, pady=5)
        tk.Label(f, text=label, font=("Segoe UI", 8),
                 bg=CARD, fg=TXT_D).pack()
        lbl = tk.Label(f, text=value, font=("Segoe UI", 11, "bold"),
                       bg=CARD, fg=color)
        lbl.pack()
        return lbl

    def _update_stats_bar(self):
        self._stat_try_lbl.config( text=f"{self._log_try_count:,}")
        self._stat_bt_lbl.config(  text=f"{self._log_bt_count:,}")
        self._stat_dead_lbl.config(text=f"{self._log_dead_count:,}")
        t = self.stats.get("elapsed_seconds", None)
        if t is not None:
            self._stat_time_lbl.config(text=f"{t}s")
        n = len(self.steps)
        if n:
            self._stat_step_lbl.config(text=f"{n:,}")

    # ================================================================
    def _on_speed_change(self, value):
        self.play_speed_ms = int(value)

    def _on_filter_change(self):
        pass  # Lọc hoạt động trực tiếp trong _log()

    def _log(self, message, tag="info"):
        # Kiểm tra bộ lọc
        if tag == "try"       and not self._filter_try.get():  return
        if tag == "backtrack" and not self._filter_bt.get():   return
        if tag == "dead"      and not self._filter_dead.get(): return

        # Giới hạn số dòng log để tránh lag
        if self._log_lines >= MAX_LOG_LINES:
            return

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self._log_lines += 1

        if self._log_lines == MAX_LOG_LINES:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(
                tk.END,
                f"⚠ Log đã đạt {MAX_LOG_LINES:,} dòng — tắt hiển thị để tránh lag. "
                "Bỏ chọn filter 'Thử' để ẩn bớt.\n", "info")
            self.log_text.config(state=tk.DISABLED)

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self._log_lines = 0

    # ================================================================
    def _render_board(self, board, highlight=None):
        for r in range(SIZE):
            for c in range(SIZE):
                val   = board[r][c]
                label = self.cell_labels[r][c]
                is_clue = self.puzzle[r][c] != 0

                label.config(text=str(val) if val != 0 else "")

                if highlight and highlight[0] == r and highlight[1] == c:
                    atype = highlight[2]
                    if atype in ("try", "assign"):
                        label.config(bg=COLOR_TRY_BG,      fg=COLOR_TRY_TEXT)
                    elif atype == "backtrack":
                        label.config(bg=COLOR_BACKTRACK_BG, fg=COLOR_BACKTRACK_TEXT)
                    elif atype in ("dead_end", "forward_check_fail"):
                        label.config(bg=COLOR_DEAD_END_BG,  fg=COLOR_DEAD_END_TEXT,
                                     text="✕")
                    elif atype == "new_iteration":
                        label.config(bg=COLOR_NEW_ITER_FLASH, fg=COLOR_SOLVED_TEXT)
                    elif atype == "swap":
                        label.config(bg=ACCENT, fg="black")
                    continue

                if is_clue:
                    label.config(bg=COLOR_CLUE_BG,   fg=COLOR_CLUE_TEXT)
                elif val != 0:
                    label.config(bg=COLOR_SOLVED_BG,  fg=COLOR_SOLVED_TEXT)
                else:
                    label.config(bg=COLOR_EMPTY_BG,   fg=TXT_B)

    # ================================================================
    def on_solve_click(self):
        if self.is_solving:
            return
        self.is_solving = True
        self._log_try_count = self._log_bt_count = self._log_dead_count = 0
        self._clear_log()
        self._log(f"Bắt đầu giải bằng {self.algo_name}...", "info")
        self.btn_solve.config(state="disabled", text="⏳ Đang giải...")
        self.info_label.config(text=f"Đang chạy {self.algo_name}...")

        def _run():
            t0 = time.time()
            result = self.solver.solve()
            t1 = time.time()
            solution, steps, stats = result
            stats["elapsed_seconds"] = round(t1 - t0, 4)
            self.steps          = steps
            self.stats          = stats
            self.solution_board = solution
            self.root.after(0, self._on_solve_finished)

        threading.Thread(target=_run, daemon=True).start()

    def _on_solve_finished(self):
        self.is_solving = False
        self.btn_solve.config(state="normal",
                              text=f"▶ Giải ({self.algo_name})")

        if self.solution_board is None:
            self._log("✗ Không tìm thấy lời giải.", "backtrack")
            messagebox.showwarning("Không có lời giải",
                                   f"{self.algo_name} không tìm được lời giải.")
            self.info_label.config(text="Không tìm được lời giải.")
            return

        self.btn_play.config(state="normal")
        self.btn_skip.config(state="normal")
        self.current_step_index = -1

        nodes = self.stats.get("nodes_expanded",
                self.stats.get("nodes", len(self.steps)))
        t     = self.stats.get("elapsed_seconds", 0)
        self.info_label.config(
            text=f"✓ Giải xong! | Nodes: {nodes:,} | "
                 f"Bước: {len(self.steps):,} | Thời gian: {t}s")
        self._log(f"✓ Hoàn thành trong {t}s | {nodes:,} nodes.", "success")
        self._update_stats_bar()

    # ================================================================
    def on_play_click(self):
        if self.is_playing:
            return
        # Reset counters khi phát lại
        self._log_try_count = self._log_bt_count = self._log_dead_count = 0
        self._clear_log()
        self.current_step_index = -1
        self.is_playing = True
        self.is_paused  = False
        self.btn_play.config(state="disabled")
        self.btn_pause.config(state="normal", text="⏸ Tạm dừng")
        self.btn_solve.config(state="disabled")
        self.btn_skip.config(state="normal")
        self._render_board(self.puzzle)
        self._play_next_step()

    def on_pause_click(self):
        if not self.is_playing:
            return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.config(text="▶ Tiếp tục")
        else:
            self.btn_pause.config(text="⏸ Tạm dừng")
            self._play_next_step()

    def _play_next_step(self):
        if self.is_paused:
            return
        self.current_step_index += 1

        if self.current_step_index >= len(self.steps):
            self._finish_playing()
            return

        step   = self.steps[self.current_step_index]
        atype  = getattr(step, "action_type", "try")
        row    = getattr(step, "row", 0)
        col    = getattr(step, "col", 0)
        val    = getattr(step, "value", 0)
        board  = step.board

        si = self.current_step_index + 1
        total = len(self.steps)
        self.info_label.config(text=f"Bước {si:,}/{total:,}")

        if atype == "new_iteration":
            self._render_board(board)
            depth = getattr(step, "depth_limit", "")
            self._log(f"━━ Lặp mới (depth_limit={depth}) ━━", "iter")

        elif atype == "swap":
            self._render_board(board, highlight=(row, col, "swap"))
            self._log_try_count += 1
            self._log(f"↕ Swap ô ({row+1},{col+1})", "try")

        elif atype == "info":
            self._render_board(board)
            self._log(str(getattr(step, "value", "")), "info")

        elif atype in ("try", "assign"):
            self._render_board(board, highlight=(row, col, "try"))
            self._log_try_count += 1
            self._log(f"  → Thử  {val}  tại ({row+1},{col+1})", "try")

        elif atype == "backtrack":
            self._render_board(board, highlight=(row, col, "backtrack"))
            self._log_bt_count += 1
            self._log(f"  ← Quay lui tại ({row+1},{col+1})  [xoá {val}]",
                      "backtrack")

        elif atype in ("dead_end", "forward_check_fail"):
            self._render_board(board, highlight=(row, col, "dead_end"))
            self._log_dead_count += 1
            self._log(f"  ✕ Dead-end tại ({row+1},{col+1})  —  domain rỗng",
                      "dead")

        # Cập nhật thanh thống kê mỗi 50 bước để không lag
        if si % 50 == 0:
            self._update_stats_bar()

        self.root.after(self.play_speed_ms, self._play_next_step)

    def _finish_playing(self):
        self.is_playing = False
        self.btn_play.config(state="normal",  text="⏵ Phát lại")
        self.btn_pause.config(state="disabled")
        self.btn_solve.config(state="normal")
        if self.solution_board:
            self._render_board(self.solution_board)
        self.info_label.config(text="✓ Đã phát xong toàn bộ quá trình tìm kiếm.")
        self._log("✓ Kết thúc phát lại.", "success")
        self._update_stats_bar()

    def on_skip_click(self):
        self.is_playing = False
        self.is_paused  = False
        self.current_step_index = len(self.steps)
        if self.solution_board:
            self._render_board(self.solution_board)
        self.info_label.config(
            text="⏭ Đã bỏ qua — hiển thị kết quả cuối.")
        self._log("⏭ Bỏ qua đến kết quả cuối.", "success")
        self.btn_play.config(state="normal", text="⏵ Phát lại")
        self.btn_pause.config(state="disabled")
        self.btn_solve.config(state="normal")
        self._update_stats_bar()

    def on_new_puzzle_click(self):
        if self.is_solving or self.is_playing:
            return
        self.puzzle, self.real_solution = generate_puzzle(
            num_clues=self.num_clues, seed=None)
        self.solver = self.solver_class(self.puzzle)
        self.steps               = []
        self.stats               = {}
        self.solution_board      = None
        self.current_step_index  = -1
        self._log_try_count      = 0
        self._log_bt_count       = 0
        self._log_dead_count     = 0
        self.btn_play.config(state="disabled")
        self.btn_pause.config(state="disabled")
        self.btn_skip.config(state="disabled")
        self._render_board(self.puzzle)
        self._clear_log()
        self._update_stats_bar()
        self.info_label.config(
            text="Đã sinh đề mới. Nhấn ▶ Giải để bắt đầu.")
        self._log("Đề mới đã được tạo.", "info")


# ================================================================
class SearchStep:
    """Dùng để solver truyền thông tin từng bước lại cho GUI."""
    def __init__(self, board, row, col, value, action_type, **kwargs):
        self.board       = copy.deepcopy(board)
        self.row         = row
        self.col         = col
        self.value       = value
        self.action_type = action_type
        # 'try' | 'assign' | 'backtrack' | 'dead_end' |
        # 'forward_check_fail' | 'swap' | 'new_iteration' | 'info'
        for k, v in kwargs.items():
            setattr(self, k, v)
