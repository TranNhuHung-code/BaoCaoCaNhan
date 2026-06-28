# -*- coding: utf-8 -*-
"""
sudoku_utils.py
Các hàm và lớp dùng chung cho toàn bộ đồ án 6 thuật toán giải Sudoku 9x9:
    - Sinh đề Sudoku (puzzle) có độ khó tùy chọn
    - Kiểm tra tính hợp lệ của việc điền số
    - Một số hàm heuristic dùng cho Informed Search / Local Search

Quy ước biểu diễn:
    - Bảng Sudoku là một list 2 chiều 9x9, giá trị 0 = ô trống, 1..9 = đã điền.
    - board[row][col], row và col đều đánh số từ 0 đến 8.
"""

import random
import copy

SIZE = 9
BOX = 3


def is_valid(board, row, col, num):
    """Kiểm tra nếu đặt `num` vào board[row][col] có vi phạm luật Sudoku không."""
    # Kiểm tra hàng
    for c in range(SIZE):
        if board[row][c] == num:
            return False
    # Kiểm tra cột
    for r in range(SIZE):
        if board[r][col] == num:
            return False
    # Kiểm tra khung 3x3
    box_row, box_col = (row // BOX) * BOX, (col // BOX) * BOX
    for r in range(box_row, box_row + BOX):
        for c in range(box_col, box_col + BOX):
            if board[r][c] == num:
                return False
    return True


def find_empty_cells(board):
    """Trả về danh sách toạ độ (row, col) các ô còn trống (giá trị 0)."""
    cells = []
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                cells.append((r, c))
    return cells


def count_conflicts(board):
    """
    Đếm tổng số cặp xung đột (số trùng nhau) trên toàn bảng.
    Dùng làm hàm đánh giá h(n) cho Simulated Annealing / Local Search
    khi bảng đã được điền đầy nhưng có thể còn sai luật.
    """
    conflicts = 0
    # Hàng
    for r in range(SIZE):
        seen = {}
        for c in range(SIZE):
            v = board[r][c]
            if v != 0:
                seen[v] = seen.get(v, 0) + 1
        conflicts += sum(cnt - 1 for cnt in seen.values() if cnt > 1)
    # Cột
    for c in range(SIZE):
        seen = {}
        for r in range(SIZE):
            v = board[r][c]
            if v != 0:
                seen[v] = seen.get(v, 0) + 1
        conflicts += sum(cnt - 1 for cnt in seen.values() if cnt > 1)
    # Khung 3x3
    for br in range(0, SIZE, BOX):
        for bc in range(0, SIZE, BOX):
            seen = {}
            for r in range(br, br + BOX):
                for c in range(bc, bc + BOX):
                    v = board[r][c]
                    if v != 0:
                        seen[v] = seen.get(v, 0) + 1
            conflicts += sum(cnt - 1 for cnt in seen.values() if cnt > 1)
    return conflicts


def heuristic_empty_cells(board):
    """h(n) đơn giản = số ô trống còn lại. Dùng cho A*/IDA*."""
    return len(find_empty_cells(board))


def candidates_for_cell(board, row, col):
    """Trả về tập các số hợp lệ có thể điền vào ô (row, col)."""
    if board[row][col] != 0:
        return set()
    return {n for n in range(1, 10) if is_valid(board, row, col, n)}


def heuristic_min_conflicts_domain(board):
    """
    h(n) "thông minh" hơn cho A*/IDA*: tổng số lựa chọn khả dĩ bị mất đi.
    Càng nhiều ô có ít lựa chọn (domain nhỏ) thì heuristic càng lớn
    -> ưu tiên các trạng thái có ràng buộc chặt hơn (gần giống MRV trong CSP).
    Giá trị trả về luôn xấp xỉ chứ không đảm bảo admissible 100%, dùng cho mục
    đích minh họa giáo trình.
    """
    empties = find_empty_cells(board)
    if not empties:
        return 0
    total = 0
    for (r, c) in empties:
        n_candidates = len(candidates_for_cell(board, r, c))
        if n_candidates == 0:
            return float('inf')  # Dead-end, không thể giải tiếp
        total += (9 - n_candidates)
    return total + len(empties)  # cộng thêm số ô trống để đảm bảo > 0 trừ khi xong


def _fill_full_board(board):
    """Sinh ngẫu nhiên một bảng Sudoku 9x9 ĐẦY và hợp lệ 100% bằng backtracking
    có xáo trộn thứ tự số, dùng làm 'lời giải gốc' trước khi đục lỗ tạo đề."""
    empties = find_empty_cells(board)
    if not empties:
        return True
    row, col = empties[0]
    nums = list(range(1, 10))
    random.shuffle(nums)
    for num in nums:
        if is_valid(board, row, col, num):
            board[row][col] = num
            if _fill_full_board(board):
                return True
            board[row][col] = 0
    return False


def generate_full_solution():
    """Trả về một bảng Sudoku 9x9 đã điền đầy, hợp lệ 100%."""
    board = [[0] * SIZE for _ in range(SIZE)]
    _fill_full_board(board)
    return board


def generate_puzzle(num_clues=35, seed=None):
    """
    Sinh một đề Sudoku 9x9 (puzzle) bằng cách:
        1. Sinh lời giải đầy đủ ngẫu nhiên.
        2. Đục lỗ (xóa số) ngẫu nhiên cho đến khi còn lại đúng `num_clues` ô gợi ý.

    Tham số:
        num_clues: số ô gợi ý (clue) còn lại trên đề. Giá trị khuyến nghị 28-45.
                   Số clue càng ít, đề càng khó (và có thể tốn nhiều thời gian
                   với các thuật toán uninformed/local search).
        seed: hạt giống ngẫu nhiên để có thể tái lập (reproducible) đề bài.

    Trả về: (puzzle, solution)
        puzzle:   bảng 9x9 với ô trống = 0, dùng làm đầu vào cho thuật toán.
        solution: bảng 9x9 lời giải đầy đủ tương ứng (dùng để so sánh / chấm điểm).
    """
    if seed is not None:
        random.seed(seed)

    solution = generate_full_solution()
    puzzle = copy.deepcopy(solution)

    cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(cells)

    num_to_remove = SIZE * SIZE - num_clues
    removed = 0
    for (r, c) in cells:
        if removed >= num_to_remove:
            break
        puzzle[r][c] = 0
        removed += 1

    return puzzle, solution


def board_to_string(board):
    """In bảng Sudoku ra dạng text dễ đọc (dùng khi debug ngoài giao diện)."""
    lines = []
    for r in range(SIZE):
        if r % BOX == 0 and r != 0:
            lines.append("-" * 21)
        row_str = ""
        for c in range(SIZE):
            if c % BOX == 0 and c != 0:
                row_str += "| "
            row_str += (str(board[r][c]) if board[r][c] != 0 else ".") + " "
        lines.append(row_str)
    return "\n".join(lines)


def copy_board(board):
    return [row[:] for row in board]


def is_solved(board):
    """Kiểm tra bảng đã điền đầy và không vi phạm luật nào."""
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                return False
    return count_conflicts(board) == 0
