# -*- coding: utf-8 -*-
"""
minimax_solver.py
Cài đặt thuật toán Minimax áp dụng cho "SUDOKU BATTLE" — một biến thể 2
NGƯỜI CHƠI (Người vs Agent) của Sudoku, được thiết kế để có ý nghĩa với
Adversarial Search (vốn dành cho game 2 phía đối kháng, trong khi Sudoku
gốc chỉ có 1 người chơi).

----------------------------------------------------------------------------
LUẬT CHƠI "SUDOKU BATTLE":
    - Bàn cờ là 1 đề Sudoku 9x9 với một số ô đã cho sẵn (clue).
    - NGƯỜI và AGENT luân phiên đi: mỗi lượt, người chơi đến lượt chọn
      MỘT ô trống và điền MỘT số (1-9) vào đó.
    - Mỗi lượt chỉ được điền ĐÚNG 1 ô. Ô điền không nhất thiết phải đúng
      với lời giải thật (người chơi có thể điền sai).
    - Sau khi điền hết tất cả ô trống, bên nào ĐIỀN ĐÚNG (so với lời giải
      thật duy nhất của đề bài) NHIỀU Ô HƠN thì THẮNG (theo điểm số).
    - Đây là một trò chơi ZERO-SUM: điểm của Agent tăng = điểm của Người
      "thiệt hại" tương đối (vì tổng số ô trống cố định, ai điền đúng
      nhiều hơn người đó thắng).

MÔ HÌNH HÓA MINIMAX:
    - Agent đóng vai MAX: muốn tối đa hóa (số ô Agent điền đúng) - (số ô
      Người điền đúng).
    - Agent giả định Người chơi cũng chơi TỐI ƯU để chống lại Agent (giả
      định đối kháng worst-case theo đúng triết lý Minimax) -> Người
      đóng vai MIN: muốn tối thiểu hóa hiệu số đó (tức tối đa hóa điểm
      của chính Người, hoặc phá điểm của Agent).
    - Vì cây trò chơi Sudoku Battle có thể rất sâu (lên đến 50+ lượt) và
      rất rộng (mỗi lượt có thể có nhiều ô trống x nhiều giá trị khả dĩ),
      ta dùng MINIMAX CÓ GIỚI HẠN ĐỘ SÂU (depth-limited minimax) với HÀM
      ĐÁNH GIÁ (evaluation function) ở các node lá khi chưa kết thúc game:
          eval(state) = (điểm Agent hiện tại - điểm Người hiện tại)
                        + (hệ số) x (tiềm năng còn lại của Agent)
      Trong đó "tiềm năng còn lại" ước lượng đơn giản bằng số ô trống còn
      lại mà Agent CÓ THỂ điền đúng nếu được ưu tiên đi tiếp (heuristic).
    - Để giảm số nhánh cần xét (vì mỗi ô có thể thử 9 giá trị), ta giới
      hạn các giá trị được xét trong MINIMAX chỉ còn các giá trị HỢP LỆ
      theo luật Sudoku hiện tại tại ô đó (loại bỏ ngay các nhánh chắc
      chắn vi phạm luật, dù phần thưởng/điểm số không phụ thuộc luật mà
      phụ thuộc việc điền ĐÚNG lời giải).
    - Mỗi lượt, Agent xét MỘT SỐ Ô TRỐNG ngẫu nhiên (không xét hết 50+ ô
      để tránh nổ tổ hợp) làm ứng viên, sau đó dùng Minimax độ sâu D để
      chọn ra cặp (ô, giá trị) tốt nhất.
----------------------------------------------------------------------------
"""

import copy
import random
from sudoku_utils import SIZE, is_valid, find_empty_cells


class MinimaxSudokuBattle:
    """
    Quản lý 1 trận Sudoku Battle (Người vs Agent) và cung cấp hàm
    `agent_choose_move` sử dụng Minimax có giới hạn độ sâu để Agent chọn
    nước đi tốt nhất ở mỗi lượt.
    """

    def __init__(self, puzzle, real_solution, search_depth=2, candidate_cells_per_turn=6):
        self.puzzle = copy.deepcopy(puzzle)
        self.real_solution = real_solution
        self.board = copy.deepcopy(puzzle)
        self.search_depth = search_depth  # độ sâu nhìn trước của Minimax (tính theo "nửa lượt")
        self.candidate_cells_per_turn = candidate_cells_per_turn

        self.agent_score = 0
        self.human_score = 0
        self.nodes_evaluated = 0  # phục vụ thống kê cho báo cáo

    # ------------------------------------------------------------------
    def get_empty_cells(self):
        return find_empty_cells(self.board)

    def is_game_over(self):
        return len(self.get_empty_cells()) == 0

    def human_move(self, row, col, value):
        """Người chơi điền giá trị `value` vào (row, col). Trả về True nếu
        điền đúng so với lời giải thật."""
        self.board[row][col] = value
        is_correct = (value == self.real_solution[row][col])
        if is_correct:
            self.human_score += 1
        return is_correct

    def agent_move(self, row, col, value):
        """Agent tự điền vào (row, col) (đã được Minimax chọn từ trước)."""
        self.board[row][col] = value
        is_correct = (value == self.real_solution[row][col])
        if is_correct:
            self.agent_score += 1
        return is_correct

    # ------------------------------------------------------------------
    # HÀM ĐÁNH GIÁ (EVALUATION FUNCTION) CHO NODE LÁ (khi hết độ sâu nhìn trước)
    # ------------------------------------------------------------------
    def _evaluate(self, board, agent_score, human_score, remaining_empty):
        """
        eval(state) = (điểm Agent - điểm Người) hiện tại
                      + 0.5 x (số ô trống còn lại) -- ước lượng đơn giản
                        rằng Agent còn nhiều cơ hội gỡ điểm/lấy điểm hơn
                        nếu trò chơi còn dài (khuyến khích Minimax không
                        vội đánh giá thấp các trạng thái còn nhiều ô trống).
        Đây là một heuristic ĐƠN GIẢN HÓA cho mục đích minh họa giáo trình,
        không phải là heuristic admissible chặt như trong A*.
        """
        return (agent_score - human_score) + 0.5 * len(remaining_empty)

    def _candidate_moves(self, board, empty_cells, limit):
        """
        Chọn ra tối đa `limit` ô trống (ưu tiên ô có ÍT giá trị hợp lệ nhất
        - tương tự MRV - để cây Minimax tập trung vào các nhánh "quan
        trọng" hơn, giảm nhánh cần xét), và với mỗi ô, chỉ xét các giá
        trị HỢP LỆ theo luật Sudoku hiện tại.

        LƯU Ý: vì người chơi/agent có thể điền SAI (ô không bị xóa, "khóa"
        vĩnh viễn giá trị sai đó), nên có thể xảy ra trường hợp một ô
        trống không còn giá trị nào "hợp lệ theo luật" (do bị ô sai xung
        quanh làm rối ràng buộc). Trong trường hợp đó, ta cho phép xét cả
        9 giá trị (1-9) để đảm bảo trò chơi luôn có nước đi tiếp, đúng với
        luật Sudoku Battle (mỗi lượt phải điền đúng 1 ô bất kể đúng/sai).
        """
        scored_cells = []
        for (r, c) in empty_cells:
            valid_values = [v for v in range(1, 10) if is_valid(board, r, c, v)]
            if not valid_values:
                # Không còn giá trị nào tuân theo luật Sudoku (do ô sai lân
                # cận) -> vẫn phải có nước đi để chơi tiếp, cho phép thử cả
                # 1-9 (ưu tiên giá trị đúng với lời giải thật nếu biết, để
                # Minimax vẫn đánh giá được phương án "điền đúng" dù phạm luật).
                valid_values = list(range(1, 10))
            scored_cells.append((r, c, valid_values))

        scored_cells.sort(key=lambda item: len(item[2]))
        return scored_cells[:limit]

    # ------------------------------------------------------------------
    # THUẬT TOÁN MINIMAX (có giới hạn độ sâu)
    # ------------------------------------------------------------------
    def _minimax(self, board, agent_score, human_score, depth, is_agent_turn, trace=None):
        """
        Trả về giá trị Minimax (float) của trạng thái hiện tại.
        is_agent_turn=True  -> lượt hiện tại là MAX (Agent)
        is_agent_turn=False -> lượt hiện tại là MIN (Người, giả định chơi tối ưu)

        Nếu `trace` (list) được truyền vào, ghi lại các bước xét để phục vụ
        trực quan hóa (chỉ dùng ở lượt gọi NGOÀI CÙNG, tức lượt thật của Agent).
        """
        self.nodes_evaluated += 1
        empty_cells = find_empty_cells(board)

        if depth == 0 or not empty_cells:
            return self._evaluate(board, agent_score, human_score, empty_cells)

        candidates = self._candidate_moves(board, empty_cells, self.candidate_cells_per_turn)
        if not candidates:
            return self._evaluate(board, agent_score, human_score, empty_cells)

        if is_agent_turn:
            best_value = float('-inf')
            for (r, c, valid_values) in candidates:
                for v in valid_values:
                    board[r][c] = v
                    correct = (v == self.real_solution[r][c])
                    new_agent_score = agent_score + (1 if correct else 0)

                    value = self._minimax(board, new_agent_score, human_score,
                                           depth - 1, False)

                    if trace is not None:
                        trace.append({'row': r, 'col': c, 'value': v, 'score': value,
                                      'player': 'agent'})

                    board[r][c] = 0
                    best_value = max(best_value, value)
            return best_value
        else:
            best_value = float('inf')
            for (r, c, valid_values) in candidates:
                for v in valid_values:
                    board[r][c] = v
                    correct = (v == self.real_solution[r][c])
                    new_human_score = human_score + (1 if correct else 0)

                    value = self._minimax(board, agent_score, new_human_score,
                                           depth - 1, True)

                    board[r][c] = 0
                    best_value = min(best_value, value)
            return best_value

    def agent_choose_move(self):
        """
        Agent (MAX) chọn nước đi tốt nhất bằng Minimax có giới hạn độ sâu.
        Trả về (row, col, value, trace) với trace là danh sách các ứng
        viên đã được Agent xét qua (dùng để trực quan hóa quá trình suy
        luận của Agent trên giao diện).
        """
        empty_cells = find_empty_cells(self.board)
        if not empty_cells:
            return None

        candidates = self._candidate_moves(self.board, empty_cells, self.candidate_cells_per_turn)

        best_value = float('-inf')
        best_move = None
        trace = []

        for (r, c, valid_values) in candidates:
            for v in valid_values:
                self.board[r][c] = v
                correct = (v == self.real_solution[r][c])
                new_agent_score = self.agent_score + (1 if correct else 0)

                value = self._minimax(self.board, new_agent_score, self.human_score,
                                       self.search_depth - 1, False)

                trace.append({'row': r, 'col': c, 'value': v, 'score': round(value, 2)})

                self.board[r][c] = 0

                if value > best_value:
                    best_value = value
                    best_move = (r, c, v)

        trace.sort(key=lambda t: -t['score'])
        return best_move[0], best_move[1], best_move[2], trace


if __name__ == "__main__":
    from sudoku_utils import generate_puzzle, board_to_string

    puzzle, real_solution = generate_puzzle(num_clues=70, seed=9)  # ít ô trống để demo nhanh
    print("Đề bài (Sudoku Battle - ít ô trống để demo dòng lệnh):")
    print(board_to_string(puzzle))
    print()

    game = MinimaxSudokuBattle(puzzle, real_solution, search_depth=2, candidate_cells_per_turn=5)

    turn = 0  # 0 = Agent đi trước, 1 = Người đi trước (ví dụ minh họa: Agent luôn đi)
    while not game.is_game_over():
        row, col, value, trace = game.agent_choose_move()
        correct = game.agent_move(row, col, value)
        print(f"Agent điền {value} tại (hàng {row+1}, cột {col+1}) "
              f"-> {'ĐÚNG' if correct else 'SAI'}. Điểm Agent: {game.agent_score}")

        empties = game.get_empty_cells()
        if empties:
            # Mô phỏng "người chơi" bằng cách điền ngẫu nhiên (chỉ để test luồng)
            r, c = random.choice(empties)
            v = random.randint(1, 9)
            correct = game.human_move(r, c, v)
            print(f"(Giả lập) Người điền {v} tại (hàng {r+1}, cột {c+1}) "
                  f"-> {'ĐÚNG' if correct else 'SAI'}. Điểm Người: {game.human_score}")

    print()
    print(f"KẾT QUẢ CUỐI: Agent = {game.agent_score} | Người = {game.human_score}")
    print(f"Tổng số node Minimax đã đánh giá: {game.nodes_evaluated}")
    print(board_to_string(game.board))
