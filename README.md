# AI Sudoku Solver — 6 Thuật Toán Tiêu Biểu

Báo cáo cá nhân tìm hiểu và triển khai **6 thuật toán** đại diện cho 6 nhóm
tìm kiếm kinh điển (AIMA) trên bài toán Sudoku, cùng các file phụ trợ cần thiết.

## Chạy menu chính

```bash
python main_menu.py
```

## Danh sách 6 thuật toán

| Nhóm | Thuật toán | File chạy | File solver |
|---|---|---|---|
| 1. Uninformed Search | **BFS** | `07_BFS_sudoku.py` | `bfs_solver.py` |
| 2. Informed Search | **Greedy Best-First Search** | `09_Greedy_sudoku.py` | `greedy_solver.py` |
| 3. Local Search | **Hill-Climbing** | `11_HillClimbing_sudoku.py` | `hill_climbing_solver.py` |
| 4. Complex Environments | **AND-OR Search** | `13_AndOr_sudoku.py` | `and_or_solver.py` |
| 5. CSP | **Backtracking** | `15_Backtracking_sudoku.py` | `backtracking_solver.py` |
| 6. Adversarial Search | **Minimax** | `06_Minimax_SudokuBattle.py` | `minimax_solver.py` |

## File phụ trợ dùng chung

- `sudoku_utils.py` — sinh đề, kiểm tra hợp lệ, heuristic, đếm xung đột.
- `base_gui.py` — giao diện cơ sở (Cyberpunk theme) dùng cho BFS, Greedy,
  AND-OR, Backtracking (4 file này gọi `BaseSudokuApp`).
  Hill-Climbing và Minimax (Sudoku Battle) có giao diện riêng được viết
  trực tiếp trong file `_sudoku.py` / `_SudokuBattle.py` tương ứng, không
  dùng `base_gui.py`.

## Yêu cầu

Python 3.8+, thư viện `tkinter` có sẵn (Ubuntu: `sudo apt install python3-tk`).
Không cần cài thêm thư viện ngoài.

## Test logic không cần giao diện

```bash
python bfs_solver.py
python greedy_solver.py
python hill_climbing_solver.py
python and_or_solver.py
python backtracking_solver.py
python minimax_solver.py
```
