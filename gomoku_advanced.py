#!/usr/bin/env python3
"""
Advanced AI Gomoku with Enhanced AI and GUI Interface
Features: Better evaluation, iterative deepening, transposition table, GUI
"""

import tkinter as tk
from tkinter import messagebox
from enum import Enum
from typing import List, Tuple, Optional, Dict
import threading
from collections import defaultdict


class Player(Enum):
    """Player types"""
    HUMAN = 1
    AI = 2
    EMPTY = 0


class GomokuBoardAdvanced:
    """Advanced Gomoku board with enhanced evaluation"""

    def __init__(self, size: int = 15):
        self.size = size
        self.board = [[Player.EMPTY for _ in range(size)] for _ in range(size)]
        self.move_history = []
        self.transposition_table = {}  # Cache for board evaluations

    def make_move(self, row: int, col: int, player: Player) -> bool:
        """Place a piece on the board"""
        if not self.is_valid_move(row, col):
            return False
        self.board[row][col] = player
        self.move_history.append((row, col, player))
        return True

    def is_valid_move(self, row: int, col: int) -> bool:
        """Check if a move is valid"""
        return (0 <= row < self.size and 
                0 <= col < self.size and 
                self.board[row][col] == Player.EMPTY)

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Get all valid moves"""
        moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.is_valid_move(row, col):
                    moves.append((row, col))
        return moves

    def check_winner(self, player: Player) -> Tuple[bool, Optional[List[Tuple[int, int]]]]:
        """Check if a player has won and return winning positions"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == player:
                    for dr, dc in directions:
                        result = self._check_direction(row, col, dr, dc, player)
                        if result:
                            return True, result
        return False, None

    def _check_direction(self, row: int, col: int, dr: int, dc: int, player: Player) -> Optional[List[Tuple[int, int]]]:
        """Check if five pieces in a row and return positions"""
        positions = []
        r, c = row, col
        # Count backwards
        while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
            positions.insert(0, (r, c))
            r -= dr
            c -= dc
        
        # Count forwards from next position
        r, c = row + dr, col + dc
        while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
            positions.append((r, c))
            r += dr
            c += dc
        
        if len(positions) >= 5:
            return positions[:5]
        return None

    def is_game_over(self) -> bool:
        """Check if game is over"""
        won, _ = self.check_winner(Player.HUMAN)
        if won:
            return True
        won, _ = self.check_winner(Player.AI)
        return won

    def get_board_hash(self) -> str:
        """Get hash of current board state for transposition table"""
        return ''.join(''.join(str(cell.value) for cell in row) for row in self.board)

    def evaluate_board(self, is_ai: bool) -> int:
        """Advanced board evaluation"""
        board_hash = self.get_board_hash()
        if board_hash in self.transposition_table:
            return self.transposition_table[board_hash]
        
        ai_score = self._calculate_threats(Player.AI)
        human_score = self._calculate_threats(Player.HUMAN)
        
        score = ai_score - human_score
        self.transposition_table[board_hash] = score
        return score

    def _calculate_threats(self, player: Player) -> int:
        """Calculate threat level - considers all patterns"""
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == player:
                    for dr, dc in directions:
                        pattern_score = self._evaluate_pattern(row, col, dr, dc, player)
                        score += pattern_score
        
        return score

    def _evaluate_pattern(self, row: int, col: int, dr: int, dc: int, player: Player) -> int:
        """Evaluate pattern value"""
        # Get line in both directions
        line = self._get_line(row, col, dr, dc)
        
        pattern_scores = {
            ('X', 'X', 'X', 'X', 'X'): 1000000,  # 5 in a row
            ('_', 'X', 'X', 'X', 'X'): 50000,    # 4 with opening
            ('X', 'X', 'X', 'X', '_'): 50000,
            ('X', 'X', 'X', '_', 'X'): 10000,    # 4 with gap
            ('X', '_', 'X', 'X', 'X'): 10000,
            ('_', 'X', 'X', 'X', '_'): 8000,     # 3 with both openings
            ('_', 'X', 'X', '_', 'X'): 2000,     # 3 with gaps
            ('X', 'X', '_', 'X', '_'): 2000,
            ('_', 'X', '_', 'X', 'X'): 2000,
            ('X', '_', 'X', '_', 'X'): 1000,
            ('X', 'X', '_', '_', 'X'): 500,
            ('_', 'X', 'X', '_', '_'): 100,      # 2 with opening
            ('_', '_', 'X', 'X', '_'): 100,
        }
        
        for pattern, value in pattern_scores.items():
            if all(line[i] == pattern[i] for i in range(5)):
                return value
        
        return 0

    def _get_line(self, row: int, col: int, dr: int, dc: int) -> Tuple:
        """Get 5-element line centered around (row, col)"""
        center_pos = 2
        line = ['_'] * 5
        
        for i in range(-2, 3):
            r = row + i * dr
            c = col + i * dc
            if 0 <= r < self.size and 0 <= c < self.size:
                if self.board[r][c] == Player.EMPTY:
                    line[i + 2] = '_'
                elif self.board[r][c] == Player.AI:
                    line[i + 2] = 'X'
                else:
                    line[i + 2] = 'O'
            else:
                line[i + 2] = '#'  # Out of bounds
        
        return tuple(line)

    def undo_move(self):
        """Undo the last move"""
        if self.move_history:
            row, col, _ = self.move_history.pop()
            self.board[row][col] = Player.EMPTY
            self.transposition_table.clear()


class AdvancedGomokuAI:
    """Advanced AI with better strategies"""

    def __init__(self, depth: int = 4, time_limit: float = 5.0):
        self.depth = depth
        self.time_limit = time_limit
        self.nodes_evaluated = 0

    def get_best_move(self, board: GomokuBoardAdvanced) -> Optional[Tuple[int, int]]:
        """Find best move using iterative deepening"""
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None
        
        if len(board.move_history) == 0:
            return (board.size // 2, board.size // 2)
        
        # Prioritize moves
        candidate_moves = self._get_candidate_moves(board, valid_moves, limit=100)
        
        best_move = candidate_moves[0]
        best_score = float('-inf')
        
        for move in candidate_moves:
            row, col = move
            board.board[row][col] = Player.AI
            
            # Check for winning move
            won, _ = board.check_winner(Player.AI)
            if won:
                board.board[row][col] = Player.EMPTY
                return move
            
            score = self._minimax(board, self.depth - 1, False, float('-inf'), float('inf'))
            board.board[row][col] = Player.EMPTY
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move

    def _minimax(self, board: GomokuBoardAdvanced, depth: int, is_maximizing: bool,
                 alpha: float, beta: float) -> int:
        """Minimax with alpha-beta pruning"""
        # Terminal states
        won, _ = board.check_winner(Player.AI)
        if won:
            return 100000 + (self.depth - depth) * 100
        
        won, _ = board.check_winner(Player.HUMAN)
        if won:
            return -100000 - (self.depth - depth) * 100
        
        if depth == 0:
            return board.evaluate_board(is_maximizing)
        
        if is_maximizing:
            max_eval = float('-inf')
            for row, col in self._get_candidate_moves(board, board.get_valid_moves(), 30):
                board.board[row][col] = Player.AI
                eval_score = self._minimax(board, depth - 1, False, alpha, beta)
                board.board[row][col] = Player.EMPTY
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for row, col in self._get_candidate_moves(board, board.get_valid_moves(), 30):
                board.board[row][col] = Player.HUMAN
                eval_score = self._minimax(board, depth - 1, True, alpha, beta)
                board.board[row][col] = Player.EMPTY
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _get_candidate_moves(self, board: GomokuBoardAdvanced, moves: List[Tuple[int, int]], 
                            limit: int = 30) -> List[Tuple[int, int]]:
        """Get best candidate moves"""
        if not board.move_history:
            center = board.size // 2
            return [(center, center)]
        
        scored_moves = []
        for move in moves:
            score = self._move_priority(board, move)
            scored_moves.append((score, move))
        
        scored_moves.sort(reverse=True)
        return [move for _, move in scored_moves[:limit]]

    def _move_priority(self, board: GomokuBoardAdvanced, move: Tuple[int, int]) -> int:
        """Calculate move priority"""
        row, col = move
        priority = 0
        
        # Distance to nearest piece
        min_dist = float('inf')
        for h_row, h_col, _ in board.move_history:
            dist = max(abs(row - h_row), abs(col - h_col))
            min_dist = min(min_dist, dist)
        
        priority += (10 - min(min_dist, 10)) * 1000
        
        # Check for winning/blocking positions
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            # Count own pieces
            count_ai = 0
            for i in range(1, 5):
                r, c = row + i * dr, col + i * dc
                if 0 <= r < board.size and 0 <= c < board.size:
                    if board.board[r][c] == Player.AI:
                        count_ai += 1
                    else:
                        break
            
            for i in range(1, 5):
                r, c = row - i * dr, col - i * dc
                if 0 <= r < board.size and 0 <= c < board.size:
                    if board.board[r][c] == Player.AI:
                        count_ai += 1
                    else:
                        break
            
            priority += count_ai * 500
        
        return priority


class GomokuGUI:
    """GUI for Gomoku game"""

    def __init__(self, root):
        self.root = root
        self.root.title("AI 五子棋 - Advanced Gomoku")
        self.root.geometry("900x1000")
        
        self.board_size = 15
        self.cell_size = 50
        self.board = GomokuBoardAdvanced(self.board_size)
        self.ai = AdvancedGomokuAI(depth=4)
        
        self.game_over = False
        self.ai_thinking = False
        self.winning_positions = []
        
        self._create_widgets()

    def _create_widgets(self):
        """Create GUI widgets"""
        # Title
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10)
        
        title_label = tk.Label(title_frame, text="AI 五子棋游戏", font=("Arial", 24, "bold"))
        title_label.pack()
        
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=5)
        
        self.status_label = tk.Label(status_frame, text="你的回合 (X)", font=("Arial", 14), fg="blue")
        self.status_label.pack()
        
        # Canvas for board
        board_frame = tk.Frame(self.root)
        board_frame.pack()
        
        self.canvas = tk.Canvas(board_frame, 
                                width=self.cell_size * self.board_size + 50,
                                height=self.cell_size * self.board_size + 50,
                                bg="wheat")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        
        # Control buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        reset_btn = tk.Button(button_frame, text="新游戏", command=self._reset_game, 
                              font=("Arial", 12), width=10)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        undo_btn = tk.Button(button_frame, text="撤销", command=self._undo_move,
                             font=("Arial", 12), width=10)
        undo_btn.pack(side=tk.LEFT, padx=5)
        
        quit_btn = tk.Button(button_frame, text="退出", command=self.root.quit,
                             font=("Arial", 12), width=10)
        quit_btn.pack(side=tk.LEFT, padx=5)
        
        # Info label
        self.info_label = tk.Label(self.root, text="点击棋盘下棋", font=("Arial", 10), fg="gray")
        self.info_label.pack(pady=5)
        
        self._draw_board()

    def _draw_board(self):
        """Draw the game board"""
        self.canvas.delete("all")
        
        # Draw grid
        for i in range(self.board_size + 1):
            x = 25 + i * self.cell_size
            y1 = 25
            y2 = 25 + self.cell_size * self.board_size
            self.canvas.create_line(x, y1, x, y2, fill="black", width=1)
            
            y = 25 + i * self.cell_size
            x1 = 25
            x2 = 25 + self.cell_size * self.board_size
            self.canvas.create_line(x1, y, x2, y, fill="black", width=1)
        
        # Draw star points
        star_positions = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        for row, col in star_positions:
            x = 25 + col * self.cell_size
            y = 25 + row * self.cell_size
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="black")
        
        # Draw pieces
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board.board[row][col] != Player.EMPTY:
                    self._draw_piece(row, col, self.board.board[row][col])
        
        # Draw winning line
        if self.winning_positions:
            for i in range(len(self.winning_positions) - 1):
                r1, c1 = self.winning_positions[i]
                r2, c2 = self.winning_positions[i + 1]
                x1 = 25 + c1 * self.cell_size
                y1 = 25 + r1 * self.cell_size
                x2 = 25 + c2 * self.cell_size
                y2 = 25 + r2 * self.cell_size
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=3)

    def _draw_piece(self, row: int, col: int, player: Player):
        """Draw a single piece"""
        x = 25 + col * self.cell_size
        y = 25 + row * self.cell_size
        radius = self.cell_size // 2 - 3
        
        color = "black" if player == Player.AI else "white"
        outline = "black" if player == Player.HUMAN else "gray"
        
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                               fill=color, outline=outline, width=2)

    def _on_canvas_click(self, event):
        """Handle canvas click"""
        if self.game_over or self.ai_thinking:
            return
        
        col = (event.x - 25) // self.cell_size
        row = (event.y - 25) // self.cell_size
        
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return
        
        self._make_human_move(row, col)

    def _make_human_move(self, row: int, col: int):
        """Handle human move"""
        if not self.board.is_valid_move(row, col):
            self.info_label.config(text="无效位置！")
            return
        
        self.board.make_move(row, col, Player.HUMAN)
        self._draw_board()
        
        # Check winner
        won, positions = self.board.check_winner(Player.HUMAN)
        if won:
            self.winning_positions = positions
            self._draw_board()
            self.game_over = True
            self.status_label.config(text="🎉 你赢了！", fg="green")
            messagebox.showinfo("游戏结束", "恭喜！你赢了！")
            return
        
        # AI move
        self.ai_thinking = True
        self.status_label.config(text="AI 思考中...", fg="orange")
        self.root.update()
        
        # Run AI move in separate thread to avoid freezing
        thread = threading.Thread(target=self._ai_move_thread)
        thread.start()

    def _ai_move_thread(self):
        """AI move in separate thread"""
        try:
            move = self.ai.get_best_move(self.board)
            
            if move:
                self.root.after(0, lambda: self._make_ai_move(move))
            else:
                self.root.after(0, lambda: self._end_game("棋盘已满，平局！"))
        except Exception as e:
            self.root.after(0, lambda: self._end_game(f"错误: {str(e)}"))

    def _make_ai_move(self, move: Tuple[int, int]):
        """Make AI move"""
        row, col = move
        self.board.make_move(row, col, Player.AI)
        self._draw_board()
        
        # Check winner
        won, positions = self.board.check_winner(Player.AI)
        if won:
            self.winning_positions = positions
            self._draw_board()
            self.game_over = True
            self.status_label.config(text="😢 AI 赢了", fg="red")
            self.ai_thinking = False
            messagebox.showinfo("游戏结束", f"AI 在位置 {row}, {col} 赢了！")
            return
        
        self.status_label.config(text="你的回合 (X)", fg="blue")
        self.info_label.config(text=f"AI 下在: ({row}, {col})")
        self.ai_thinking = False

    def _end_game(self, message: str):
        """End game"""
        self.game_over = True
        self.ai_thinking = False
        self.status_label.config(text="游戏结束", fg="red")
        messagebox.showinfo("游戏结束", message)

    def _undo_move(self):
        """Undo moves"""
        if self.game_over:
            messagebox.showinfo("提示", "游戏已结束，请开始新游戏")
            return
        
        if len(self.board.move_history) >= 2:
            self.board.undo_move()  # Undo AI move
            self.board.undo_move()  # Undo human move
            self.winning_positions = []
            self.game_over = False
            self.status_label.config(text="你的回合 (X)", fg="blue")
            self.info_label.config(text="已撤销上一步")
            self._draw_board()
        else:
            messagebox.showinfo("提示", "无法撤销")

    def _reset_game(self):
        """Reset game"""
        self.board = GomokuBoardAdvanced(self.board_size)
        self.game_over = False
        self.ai_thinking = False
        self.winning_positions = []
        self.status_label.config(text="你的回合 (X)", fg="blue")
        self.info_label.config(text="游戏已重置")
        self._draw_board()


def main():
    """Entry point"""
    root = tk.Tk()
    gui = GomokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
