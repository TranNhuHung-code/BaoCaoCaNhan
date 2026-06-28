# -*- coding: utf-8 -*-
"""
bfs_solver.py
Cài đặt thuật toán Breadth-First Search (BFS) để giải Sudoku.
"""
import copy
from collections import deque
from sudoku_utils import is_valid, find_empty_cells, SIZE

class SearchStep:
    def __init__(self, board, row, col, value, action_type):
        self.board = copy.deepcopy(board)
        self.row = row
        self.col = col
        self.value = value
        self.action_type = action_type

class BFSSolver:
    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
        self.nodes_expanded = 0

    def solve(self):
        queue = deque([self.puzzle])
        
        while queue:
            board = queue.popleft()
            self.nodes_expanded += 1
            
            empties = find_empty_cells(board)
            if not empties:
                stats = {
                    'nodes_expanded': self.nodes_expanded,
                    'total_steps_recorded': len(self.steps),
                }
                return board, self.steps, stats
                
            row, col = empties[0]
            
            for num in range(1, 10):
                if is_valid(board, row, col, num):
                    new_board = copy.deepcopy(board)
                    new_board[row][col] = num
                    # Ghi nhận bước nhảy của BFS
                    self.steps.append(SearchStep(new_board, row, col, num, 'try'))
                    queue.append(new_board)
                    
        stats = {
            'nodes_expanded': self.nodes_expanded,
            'total_steps_recorded': len(self.steps),
        }
        return None, self.steps, stats
