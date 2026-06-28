# -*- coding: utf-8 -*-
"""
09_Greedy_sudoku.py
================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: INFORMED SEARCH
Thuật toán trình bày: Greedy Best-First Search
"""
import tkinter as tk
from base_gui import BaseSudokuApp
from greedy_solver import GreedySolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="09 - Greedy Best-First Search",
        subtitle="Nhóm 2: Informed Search",
        algo_name="Greedy Best-First",
        solver_class=GreedySolver,
        num_clues=45
    )
    root.mainloop()

if __name__ == "__main__":
    main()
