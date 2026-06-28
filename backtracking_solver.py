# -*- coding: utf-8 -*-
"""
backtracking_solver.py
Cài đặt thuật toán Backtracking Search để giải Sudoku.
Trong nhóm CSP, Backtracking thường đi kèm với các heuristic như
MRV (Minimum Remaining Values - Chọn biến có ít giá trị hợp lệ nhất).
"""
import copy
from sudoku_utils import is_valid, find_empty_cells, SIZE

class SearchStep:
    def __init__(self, board, row, col, value, action_type):
        self.board = copy.deepcopy(board)
        self.row = row
        self.col = col
        self.value = value
        self.action_type = action_type

class BacktrackingSolver:
    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
        self.nodes_expanded = 0

    def solve(self):
        result_board = self._search(self.puzzle)
        stats = {
            'nodes_expanded': self.nodes_expanded,
            'total_steps_recorded': len(self.steps),
        }
        return result_board, self.steps, stats

    def _select_unassigned_variable(self, board):
        empties = find_empty_cells(board)
        if not empties:
            return None
        
        # MRV Heuristic: Chọn ô trống có ít lựa chọn hợp lệ nhất
        best_cell = None
        min_options = float('inf')
        
        for r, c in empties:
            options = sum(1 for num in range(1, 10) if is_valid(board, r, c, num))
            if options < min_options:
                min_options = options
                best_cell = (r, c)
                
        return best_cell

    def _search(self, board):
        cell = self._select_unassigned_variable(board)
        if cell is None:
            return board
            
        row, col = cell
        
        for num in range(1, 10):
            self.nodes_expanded += 1
            if is_valid(board, row, col, num):
                board[row][col] = num
                self.steps.append(SearchStep(board, row, col, num, 'try'))
                
                result = self._search(board)
                if result is not None:
                    return result
                    
                board[row][col] = 0
                self.steps.append(SearchStep(board, row, col, 0, 'backtrack'))
                
        return None
