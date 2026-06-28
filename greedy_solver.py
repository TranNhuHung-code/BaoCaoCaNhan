# -*- coding: utf-8 -*-
"""
greedy_solver.py
Cài đặt thuật toán Greedy Best-First Search để giải Sudoku.
"""
import copy
import heapq
from sudoku_utils import is_valid, find_empty_cells, heuristic_min_conflicts_domain, SIZE

class SearchStep:
    def __init__(self, board, row, col, value, action_type):
        self.board = copy.deepcopy(board)
        self.row = row
        self.col = col
        self.value = value
        self.action_type = action_type

class GreedySolver:
    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
        self.nodes_expanded = 0

    def solve(self):
        pq = []
        h_initial = heuristic_min_conflicts_domain(self.puzzle)
        heapq.heappush(pq, (h_initial, 0, self.puzzle))
        counter = 1
        
        while pq:
            h, _, board = heapq.heappop(pq)
            self.nodes_expanded += 1
            
            empties = find_empty_cells(board)
            if not empties:
                stats = {'nodes_expanded': self.nodes_expanded, 'total_steps': len(self.steps)}
                return board, self.steps, stats
                
            row, col = empties[0]
            
            for num in range(1, 10):
                if is_valid(board, row, col, num):
                    new_board = copy.deepcopy(board)
                    new_board[row][col] = num
                    self.steps.append(SearchStep(new_board, row, col, num, 'try'))
                    new_h = heuristic_min_conflicts_domain(new_board)
                    heapq.heappush(pq, (new_h, counter, new_board))
                    counter += 1
                    
        return None, self.steps, {'nodes_expanded': self.nodes_expanded}
