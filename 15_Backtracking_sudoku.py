# -*- coding: utf-8 -*-
"""
15_Backtracking_sudoku.py
======================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: CONSTRAINT SATISFACTION PROBLEM (CSP)
Thuật toán trình bày: Backtracking Search (với MRV Heuristic)
"""

import tkinter as tk
from base_gui import BaseSudokuApp
from backtracking_solver import BacktrackingSolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="15 - Backtracking Search (CSP)",
        subtitle="Nhóm 5: Constraint Satisfaction Problem",
        algo_name="Backtracking (MRV)",
        solver_class=BacktrackingSolver,
        num_clues=40
    )
    root.mainloop()

if __name__ == "__main__":
    main()
