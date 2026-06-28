# -*- coding: utf-8 -*-
"""
07_BFS_sudoku.py
================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: UNINFORMED SEARCH (Tìm kiếm mù / không thông tin)
Thuật toán trình bày: Breadth-First Search (BFS)
Bài toán áp dụng: Giải Sudoku 9x9
"""

import tkinter as tk
from base_gui import BaseSudokuApp
from bfs_solver import BFSSolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="07 - Breadth-First Search (BFS)",
        subtitle="Nhóm 1: Uninformed Search",
        algo_name="BFS",
        solver_class=BFSSolver,
        num_clues=74  # Cần cực ít ô trống vì BFS tốn bộ nhớ mũ
    )
    root.mainloop()

if __name__ == "__main__":
    main()
