# -*- coding: utf-8 -*-
"""
main_menu.py
=============
MENU CHÍNH - 6 THUẬT TOÁN AI ĐƯỢC TRÍCH CHỌN
Trích từ Đồ Án Cuối Kỳ - Trí Tuệ Nhân Tạo (19 thuật toán / 6 nhóm)

6 thuật toán đại diện cho 6 nhóm tìm kiếm kinh điển (AIMA):
    1. Uninformed Search   -> BFS
    2. Informed Search     -> Greedy Best-First Search
    3. Local Search        -> Hill-Climbing
    4. Complex Environments-> AND-OR Search
    5. CSP                 -> Backtracking Search
    6. Adversarial Search  -> Minimax

CÁCH CHẠY:
    python main_menu.py
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os


# ===================== MÀU SẮC (Cyberpunk Theme) =====================
BG       = "#080816"
CARD     = "#141630"
CARD_H   = "#1E203E"
ACCENT   = "#00C6FF"
TXT      = "#D7DAE8"
TXT_D    = "#646987"
TXT_B    = "#FFFFFF"

FONT_TITLE    = ("Segoe UI", 22, "bold")
FONT_SUBTITLE = ("Segoe UI", 11)
FONT_GROUP    = ("Segoe UI", 12, "bold")
FONT_BTN      = ("Segoe UI", 11, "bold")
FONT_BTN_SUB  = ("Segoe UI", 9)

# ===================== 6 THUẬT TOÁN ĐƯỢC CHỌN =====================
ALGORITHMS = [
    {
        "name": "1. Uninformed Search",
        "color": "#00C6FF",
        "icon": "🔍",
        "short_name": "BFS",
        "file": "07_BFS_sudoku.py",
        "desc": "Breadth-First Search\nTìm kiếm theo chiều rộng — duyệt mức theo mức, "
                "đảm bảo tìm lời giải nông nhất nhưng tốn nhiều bộ nhớ."
    },
    {
        "name": "2. Informed Search",
        "color": "#00E473",
        "icon": "🎯",
        "short_name": "Greedy",
        "file": "09_Greedy_sudoku.py",
        "desc": "Greedy Best-First Search\nChỉ dùng hàm heuristic h(n) để chọn ô/giá trị "
                "hứa hẹn nhất, nhanh nhưng không đảm bảo tối ưu."
    },
    {
        "name": "3. Local Search",
        "color": "#FFBE00",
        "icon": "⛰️",
        "short_name": "Hill Climbing",
        "file": "11_HillClimbing_sudoku.py",
        "desc": "Hill-Climbing Search\nBắt đầu từ lời giải đầy đủ ngẫu nhiên, hoán đổi ô để "
                "giảm xung đột. Dễ kẹt cực tiểu địa phương."
    },
    {
        "name": "4. Complex Environments",
        "color": "#F97316",
        "icon": "🌫️",
        "short_name": "AND-OR Search",
        "file": "13_AndOr_sudoku.py",
        "desc": "AND-OR Search\nXây dựng cây AND-OR để xử lý môi trường có yếu tố "
                "nondeterministic / nhiều nhánh khả dĩ."
    },
    {
        "name": "5. CSP",
        "color": "#A855F7",
        "icon": "🔒",
        "short_name": "Backtracking",
        "file": "15_Backtracking_sudoku.py",
        "desc": "Backtracking Search (MRV)\nMô hình hóa Sudoku như CSP, duyệt giá trị theo "
                "chiều sâu, quay lui khi vi phạm ràng buộc."
    },
    {
        "name": "6. Adversarial Search",
        "color": "#FF325A",
        "icon": "⚔️",
        "short_name": "Minimax",
        "file": "06_Minimax_SudokuBattle.py",
        "desc": "Minimax (Sudoku Battle)\nNgười vs Agent điền số luân phiên. Agent (MAX) giả "
                "định Người chơi (MIN) tối ưu nhất."
    },
]


class MainMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Sudoku Solver — 6 Thuật Toán Tiêu Biểu")
        self.root.configure(bg=BG)
        self.root.geometry("980x640")
        self.root.resizable(False, False)

        self._build_ui()

    def _build_ui(self):
        # ----- Header -----
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill=tk.X, pady=(18, 10))

        tk.Label(
            header,
            text="🧩  AI Sudoku Solver",
            font=FONT_TITLE, bg=BG, fg=ACCENT
        ).pack()
        tk.Label(
            header,
            text="6 Thuật Toán Tiêu Biểu  ·  BFS · Greedy · Hill-Climbing · "
                 "AND-OR · Backtracking · Minimax",
            font=FONT_SUBTITLE, bg=BG, fg=TXT_D
        ).pack()

        divider = tk.Frame(self.root, bg=ACCENT, height=1)
        divider.pack(fill=tk.X, padx=20, pady=(6, 10))

        # ----- Grid 2 cột x 3 dòng -----
        grid_container = tk.Frame(self.root, bg=BG)
        grid_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        for col_idx in range(2):
            grid_container.columnconfigure(col_idx, weight=1)
        for row_idx in range(3):
            grid_container.rowconfigure(row_idx, weight=1)

        for idx, algo in enumerate(ALGORITHMS):
            row_idx = idx // 2
            col_idx = idx % 2

            card = tk.Frame(
                grid_container, bg=CARD,
                highlightbackground=algo["color"],
                highlightthickness=1
            )
            card.grid(row=row_idx, column=col_idx,
                      padx=8, pady=8, sticky="nsew")

            self._make_algo_card(card, algo)

        # ----- Footer -----
        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill=tk.X, pady=(4, 10))

        tk.Label(
            footer,
            text="Click vào thẻ thuật toán để mở giao diện · "
                 "Mỗi cửa sổ chạy độc lập · "
                 "Giữ file trong cùng thư mục khi chạy",
            font=("Segoe UI", 9), bg=BG, fg=TXT_D
        ).pack()

    def _make_algo_card(self, parent, algo):
        # Nhóm (label nhỏ phía trên)
        tk.Label(
            parent,
            text=f"{algo['icon']}  {algo['name']}",
            font=FONT_GROUP, bg=CARD, fg=algo["color"],
            anchor="w"
        ).pack(fill=tk.X, padx=12, pady=(10, 2))

        inner = tk.Frame(parent, bg=CARD_H, cursor="hand2")
        inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=(2, 12))

        name_lbl = tk.Label(
            inner, text=f"▶  {algo['short_name']}",
            font=FONT_BTN, bg=CARD_H, fg=TXT_B,
            anchor="w", padx=12, pady=8
        )
        name_lbl.pack(fill=tk.X)

        desc_lbl = tk.Label(
            inner, text=algo["desc"],
            font=FONT_BTN_SUB, bg=CARD_H, fg=TXT_D,
            anchor="w", justify="left", padx=12, wraplength=380
        )
        desc_lbl.pack(fill=tk.X, pady=(0, 8))

        widgets = [inner, name_lbl, desc_lbl]

        def on_enter(e):
            inner.config(bg=algo["color"])
            name_lbl.config(bg=algo["color"], fg=BG)
            desc_lbl.config(bg=algo["color"], fg=BG)

        def on_leave(e):
            inner.config(bg=CARD_H)
            name_lbl.config(bg=CARD_H, fg=TXT_B)
            desc_lbl.config(bg=CARD_H, fg=TXT_D)

        def on_click(e, fn=algo["file"]):
            self._launch(fn)

        for widget in widgets:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

    def _launch(self, filename):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, filename)

        if not os.path.exists(script_path):
            messagebox.showerror(
                "Không tìm thấy file",
                f"File '{filename}' không tồn tại trong thư mục:\n{script_dir}"
            )
            return

        try:
            subprocess.Popen(
                [sys.executable, script_path],
                cwd=script_dir
            )
        except Exception as ex:
            messagebox.showerror("Lỗi khởi chạy", str(ex))


def main():
    root = tk.Tk()
    app = MainMenuApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
