# -*- coding: utf-8 -*-
"""
hill_climbing_solver.py
Cài đặt thuật toán Hill Climbing (Steepest-Ascent) giải Sudoku.
"""
import copy
import random
from sudoku_utils import SIZE, count_conflicts

class SearchStep:
    def __init__(self, board, row, col1, col2, action_type, h_value):
        self.board = copy.deepcopy(board)
        self.row = row
        self.col1 = col1
        self.col2 = col2
        self.action_type = action_type  # 'accept_better' | 'restart' | 'stuck'
        self.h_value = h_value

class HillClimbingSolver:
    def __init__(self, puzzle, max_steps=2000, max_restarts=20):
        self.puzzle = copy.deepcopy(puzzle)
        self.max_steps = max_steps
        self.max_restarts = max_restarts
        self.steps = []
        self.is_clue = [[puzzle[r][c] != 0 for c in range(SIZE)] for r in range(SIZE)]

    def _init_random_board(self):
        board = copy.deepcopy(self.puzzle)
        for r in range(SIZE):
            existing = set(board[r])
            missing = [n for n in range(1, 10) if n not in existing]
            random.shuffle(missing)
            idx = 0
            for c in range(SIZE):
                if board[r][c] == 0:
                    board[r][c] = missing[idx]
                    idx += 1
        return board

    def _empty_cols_in_row(self, row):
        return [c for c in range(SIZE) if not self.is_clue[row][c]]

    def solve(self):
        rows_with_freedom = [r for r in range(SIZE) if len(self._empty_cols_in_row(r)) >= 2]
        
        if not rows_with_freedom:
            current = self._init_random_board()
            current_h = count_conflicts(current)
            stats = {'steps': 0, 'restarts': 0}
            return (current if current_h == 0 else None), self.steps, stats

        total_step_count = 0
        restart_count = 0

        while restart_count < self.max_restarts:
            result_board, current_h, step_count = self._run_one_attempt(rows_with_freedom)
            total_step_count += step_count

            if current_h == 0:
                stats = {'steps': total_step_count, 'restarts': restart_count}
                return result_board, self.steps, stats

            restart_count += 1
            if restart_count < self.max_restarts:
                self.steps.append(SearchStep(result_board, -1, -1, -1, 'restart', current_h))

        stats = {'steps': total_step_count, 'restarts': restart_count}
        return None, self.steps, stats

    def _run_one_attempt(self, rows_with_freedom):
        current = self._init_random_board()
        current_h = count_conflicts(current)
        step_count = 0

        while step_count < self.max_steps and current_h > 0:
            step_count += 1
            
            best_neighbor = None
            best_h = float('inf')
            best_move = None
            
            # Khám phá toàn bộ lân cận (Steepest-Ascent)
            for row in rows_with_freedom:
                cols = self._empty_cols_in_row(row)
                for i in range(len(cols)):
                    for j in range(i + 1, len(cols)):
                        c1, c2 = cols[i], cols[j]
                        neighbor = copy.deepcopy(current)
                        neighbor[row][c1], neighbor[row][c2] = neighbor[row][c2], neighbor[row][c1]
                        neighbor_h = count_conflicts(neighbor)
                        
                        if neighbor_h < best_h:
                            best_h = neighbor_h
                            best_neighbor = neighbor
                            best_move = (row, c1, c2)
            
            if best_h < current_h:
                current = best_neighbor
                current_h = best_h
                self.steps.append(SearchStep(current, best_move[0], best_move[1], best_move[2], 'accept_better', current_h))
            else:
                self.steps.append(SearchStep(current, -1, -1, -1, 'stuck', current_h))
                break # Kẹt ở local optimum, cần restart
                
        return current, current_h, step_count
