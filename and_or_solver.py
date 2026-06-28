# -*- coding: utf-8 -*-
"""
and_or_solver.py
Cài đặt thuật toán AND-OR Search để giải Sudoku.
Vì Sudoku là bài toán đơn định (deterministic), AND-OR Search suy biến thành Backtracking,
trong đó OR-node là việc chọn giá trị cho 1 ô, và AND-node là việc phải giải tất cả các ô còn lại.
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

class AndOrSolver:
    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
        self.nodes_expanded = 0

    def solve(self):
        result_board = self._or_search(self.puzzle)
        stats = {
            'nodes_expanded': self.nodes_expanded,
            'total_steps_recorded': len(self.steps),
        }
        return result_board, self.steps, stats

    def _or_search(self, board):
        empties = find_empty_cells(board)
        if not empties:
            return board
            
        row, col = empties[0]
        
        for num in range(1, 10):
            self.nodes_expanded += 1
            if is_valid(board, row, col, num):
                board[row][col] = num
                self.steps.append(SearchStep(board, row, col, num, 'try'))
                
                result = self._and_search(board)
                if result is not None:
                    return result
                    
                board[row][col] = 0
                self.steps.append(SearchStep(board, row, col, 0, 'backtrack'))
                
        return None

    def _and_search(self, board):
        # AND-node: Tất cả các phần còn lại của bài toán phải được giải quyết.
        # Ở Sudoku, ta chỉ có 1 nhánh duy nhất là trạng thái bảng hiện tại.
        return self._or_search(board)
