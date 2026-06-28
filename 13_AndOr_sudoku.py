# -*- coding: utf-8 -*-
"""
13_AndOr_sudoku.py
======================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: COMPLEX SEARCH
Thuật toán trình bày: AND-OR Search
"""

import tkinter as tk
from base_gui import BaseSudokuApp
from and_or_solver import AndOrSolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="13 - AND-OR Search",
        subtitle="Nhóm 4: Complex Search",
        algo_name="AND-OR Search",
        solver_class=AndOrSolver,
        num_clues=40
    )
    root.mainloop()

if __name__ == "__main__":
    main()
