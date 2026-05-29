#!/usr/bin/env python3
"""
Intelligent AI Gomoku - Human Level
Features: Deep thinking (8 plies), advanced threat detection, winning strategy recognition
"""

import tkinter as tk
from tkinter import messagebox
from enum import Enum
from typing import List, Tuple, Optional, Dict
import threading
import time


class Player(Enum):
    """Player types"""
    HUMAN = 1
    AI = 2
    EMPTY = 0


class GomokuBoardAdvanced:
    """Advanced Gomoku board with deep pattern analysis"""

    def __init__(self, size: int = 15):
        self.size = size
        self.board = [[Player.EMPTY for _ in range(size)] for _ in range(size)]
        self.move_history = []
        self.last_move = None
        self.zobrist_hash = 0
        self.zobrist_table = self._init_zobrist()
        self.transposition_table = {}

    def _init_zobrist(self) -> Dict:
        """Initialize Zobrist hash"""
        import random
        random.seed(42)
        zobrist = {}
        for row in range(self.size):
            for col in range(self.size):
                zobrist[(row, col, Player.AI)] = random.getrandbits(64)
                zobrist[(row, col, Player.HUMAN)] = random.getrandbits(64)
        return zobrist

    def make_move(self, row: int, col: int, player: Player) -> bool:
        """Place a piece"""
        if not self.is_valid_move(row, col):
            return False
        self.board[row][col] = player
        self.move_history.append((row, col, player))
        self.last_move = (row, col)
        self.zobrist_hash ^= self.zobrist_table[(row, col, player)]
        return True

    def undo_move(self):
        """Undo last move"""
        if self.move_history:
            row, col, player = self.move_history.pop()
            self.board[row][col] = Player.EMPTY
            self.zobrist_hash ^= self.zobrist_table[(row, col, player)]
            if self.move_history:
                self.last_move = self.move_history[-1][:2]
            else:
                self.last_move = None

    def is_valid_move(self, row: int, col: int) -> bool:
        """Check if move is valid"""
        return (0 <= row < self.size and 
                0 <= col < self.size and 
                self.board[row][col] == Player.EMPTY)

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Get candidate moves near existing pieces"""
        if not self.move_history:
            return [(self.size // 2, self.size // 2)]
        
        moves = set()
        search_range = 2
        
        for row, col, _ in self.move_history[-2:]:
            for dr in range(-search_range, search_range + 1):
                for dc in range(-search_range, search_range + 1):
                    r, c = row + dr, col + dc
                    if self.is_valid_move(r, c):
                        moves.add((r, c))
        
        return list(moves)

    def check_winner(self, player: Player) -> Tuple[bool, Optional[List[Tuple[int, int]]]]:
        """Check if player won"""
        if not self.last_move:
            return False, None
        
        row, col = self.last_move
        
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            positions = self._count_line(row, col, dr, dc, player)
            if len(positions) >= 5:
                return True, positions[:5]
        
        return False, None

    def _count_line(self, row: int, col: int, dr: int, dc: int, 
                   player: Player) -> List[Tuple[int, int]]:
        """Count consecutive pieces"""
        positions = []
        
        # Backward
        r, c = row - dr, col - dc
        while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
            positions.insert(0, (r, c))
            r -= dr
            c -= dc
        
        positions.append((row, col))
        
        # Forward
        r, c = row + dr, col + dc
        while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
            positions.append((r, c))
            r += dr
            c += dc
        
        return positions

    def evaluate_board(self) -> int:
        """Comprehensive board evaluation"""
        if self.zobrist_hash in self.transposition_table:
            return self.transposition_table[self.zobrist_hash]
        
        ai_score = self._score_player(Player.AI)
        human_score = self._score_player(Player.HUMAN)
        
        score = ai_score - human_score
        self.transposition_table[self.zobrist_hash] = score
        return score

    def _score_player(self, player: Player) -> int:
        """Score all patterns for a player"""
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == player:
                    for dr, dc in directions:
                        line = self._get_line(row, col, dr, dc)
                        score += self._score_line(line, player)
        
        return score

    def _get_line(self, row: int, col: int, dr: int, dc: int) -> str:
        """Get 9-char line centered at (row, col)"""
        line = []
        for i in range(-4, 5):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < self.size and 0 <= c < self.size:
                if self.board[r][c] == Player.EMPTY:
                    line.append('_')
                elif self.board[r][c] == Player.AI:
                    line.append('X')
                else:
                    line.append('O')
            else:
                line.append('#')
        return ''.join(line)

    def _score_line(self, line: str, player: Player) -> int:
        """Score a line for a player"""
        is_ai = (player == Player.AI)
        my_char = 'X' if is_ai else 'O'
        opp_char = 'O' if is_ai else 'X'
        
        score = 0
        
        # ===== 我方得分 =====
        
        # 5 in a row
        if my_char * 5 in line:
            score += 1000000
        
        # 活四 (两边空)
        if f'_{my_char*4}_' in line:
            score += 100000
        
        # 冲四 (一边堵，一边空)
        if f'_{my_char*4}{opp_char}' in line or f'{opp_char}{my_char*4}_' in line:
            score += 10000
        if f'_{my_char}_{my_char*3}' in line or f'{my_char*3}_{my_char}_' in line:
            score += 5000
        
        # 活三 (两边空)
        if f'_{my_char*3}_' in line:
            score += 5000
        
        # 冲三 (一边空一边堵)
        if f'_{my_char*3}{opp_char}' in line or f'{opp_char}{my_char*3}_' in line:
            score += 500
        if f'_{my_char}_{my_char}_{my_char}_' in line:
            score += 500
        if f'_{my_char}{my_char}_{my_char*2}' in line or f'{my_char*2}_{my_char}{my_char}_' in line:
            score += 500
        
        # 活二 (两边空，能形成三)
        if f'_{my_char*2}_' in line:
            score += 200
        if f'_{my_char}__{my_char}_' in line:
            score += 100
        
        # 单子和孤立子
        for i in range(len(line) - 4):
            segment = line[i:i+5]
            if my_char in segment:
                count = segment.count(my_char)
                if count == 1 and segment.count('_') >= 3:
                    score += 5
        
        # ===== 对方威胁惩罚 =====
        
        # 对方5连 (紧急！)
        if opp_char * 5 in line:
            score -= 1000000
        
        # 对方活四 (必须堵)
        if f'_{opp_char*4}_' in line:
            score -= 100000
        
        # 对方冲四
        if f'_{opp_char*4}{my_char}' in line or f'{my_char}{opp_char*4}_' in line:
            score -= 10000
        
        # 对方活三 (必须立即堵！优先级最高)
        if f'_{opp_char*3}_' in line:
            score -= 50000
        
        # 对方带间隔活三的检测
        if f'_{opp_char}__{opp_char*2}_' in line or f'_{opp_char*2}__{opp_char}_' in line:
            score -= 20000
        if f'_{opp_char}_{opp_char}_{opp_char}_' in line:
            score -= 15000
        
        return score


class AdvancedGomokuAI:
    """Human-level AI with 8-ply deep search"""

    def __init__(self, depth: int = 8):
        self.depth = depth
        self.nodes_evaluated = 0
        self.start_time = 0
        self.time_limit = 10.0

    def get_best_move(self, board: GomokuBoardAdvanced) -> Optional[Tuple[int, int]]:
        """Get best move with deep analysis"""
        self.start_time = time.time()
        self.nodes_evaluated = 0
        
        if len(board.move_history) == 0:
            return (board.size // 2, board.size // 2)
        
        if len(board.move_history) == 1:
            return self._opening_move(board)
        
        # Phase 1: Quick win check
        move = self._find_instant_win(board, Player.AI)
        if move:
            return move
        
        # Phase 2: Urgent defense - block opponent's instant win
        move = self._find_instant_win(board, Player.HUMAN)
        if move:
            return move
        
        # Phase 2.5: CRITICAL - Block opponent's active three
        move = self._block_active_three(board)
        if move:
            return move
        
        # Phase 3: Look for double threats
        move = self._find_double_threat(board)
        if move:
            return move
        
        # Phase 4: Deep minimax
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None
        
        moves = self._rank_moves(board, valid_moves)
        
        best_move = moves[0]
        best_score = float('-inf')
        
        for move in moves[:10]:  # Only evaluate top 10
            row, col = move
            board.board[row][col] = Player.AI
            board.last_move = (row, col)
            
            score = self._minimax(board, self.depth - 1, False, float('-inf'), float('inf'))
            board.board[row][col] = Player.EMPTY
            
            if score > best_score:
                best_score = score
                best_move = move
            
            if time.time() - self.start_time > self.time_limit * 0.8:
                break
        
        return best_move

    def _opening_move(self, board: GomokuBoardAdvanced) -> Tuple[int, int]:
        """Smart opening"""
        row, col = board.move_history[0][:2]
        center = board.size // 2
        
        if abs(row - center) <= 1 and abs(col - center) <= 1:
            return (center, col + 2)
        else:
            return (center, center)

    def _find_instant_win(self, board: GomokuBoardAdvanced, 
                         player: Player) -> Optional[Tuple[int, int]]:
        """Check for 1-move win"""
        for row, col in board.get_valid_moves():
            board.board[row][col] = player
            board.last_move = (row, col)
            
            won, _ = board.check_winner(player)
            board.board[row][col] = Player.EMPTY
            
            if won:
                return (row, col)
        
        return None

    def _block_active_three(self, board: GomokuBoardAdvanced) -> Optional[Tuple[int, int]]:
        """Block opponent's active three pattern - CRITICAL DEFENSE"""
        threat_positions = set()
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        # 收集所有对手活三的开口位置
        for row in range(board.size):
            for col in range(board.size):
                if board.board[row][col] == Player.HUMAN:
                    for dr, dc in directions:
                        line = board._get_line(row, col, dr, dc)
                        
                        # 标准活三：_OOO_
                        if '_OOO_' in line:
                            idx = line.index('_OOO_')
                            center_pos = 4
                            
                            # 左边的开口
                            left_pos = idx - 1 - center_pos
                            r1, c1 = row + left_pos * dr, col + left_pos * dc
                            if 0 <= r1 < board.size and 0 <= c1 < board.size:
                                threat_positions.add((r1, c1))
                            
                            # 右边的开口
                            right_pos = idx + 4 - center_pos
                            r2, c2 = row + right_pos * dr, col + right_pos * dc
                            if 0 <= r2 < board.size and 0 <= c2 < board.size:
                                threat_positions.add((r2, c2))
                        
                        # 其他活三变体
                        patterns = ['_O_OO_', '_OO_O_']
                        for pattern in patterns:
                            if pattern in line:
                                idx = line.index(pattern)
                                for i, char in enumerate(pattern):
                                    if char == '_':
                                        pos = idx + i - center_pos
                                        r, c = row + pos * dr, col + pos * dc
                                        if 0 <= r < board.size and 0 <= c < board.size and board.board[r][c] == Player.EMPTY:
                                            threat_positions.add((r, c))
        
        # 选择最佳阻挡位置
        if threat_positions:
            best_block = None
            max_blocked = 0
            
            for block_row, block_col in threat_positions:
                board.board[block_row][block_col] = Player.AI
                
                # 计算有多少个威胁被阻挡
                blocked_count = 0
                for row in range(board.size):
                    for col in range(board.size):
                        if board.board[row][col] == Player.HUMAN:
                            for dr, dc in directions:
                                line = board._get_line(row, col, dr, dc)
                                if '_OOO_' in line or '_O_OO_' in line or '_OO_O_' in line:
                                    blocked_count += 1
                
                board.board[block_row][block_col] = Player.EMPTY
                
                if blocked_count > max_blocked:
                    max_blocked = blocked_count
                    best_block = (block_row, block_col)
            
            return best_block
        
        return None

    def _find_double_threat(self, board: GomokuBoardAdvanced) -> Optional[Tuple[int, int]]:
        """Find 2-threat position"""
        for row, col in board.get_valid_moves():
            board.board[row][col] = Player.AI
            board.last_move = (row, col)
            
            threats = 0
            for next_row, next_col in board.get_valid_moves():
                board.board[next_row][next_col] = Player.AI
                board.last_move = (next_row, next_col)
                
                won, _ = board.check_winner(Player.AI)
                board.board[next_row][next_col] = Player.EMPTY
                
                if won:
                    threats += 1
                    if threats >= 2:
                        break
            
            board.board[row][col] = Player.EMPTY
            
            if threats >= 2:
                return (row, col)
        
        return None

    def _rank_moves(self, board: GomokuBoardAdvanced, 
                   moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Rank moves by strategic value"""
        scored = []
        
        for row, col in moves:
            score = 0
            
            # Proximity to last move
            if board.last_move:
                last_row, last_col = board.last_move
                dist = abs(row - last_row) + abs(col - last_col)
                score -= dist * 1000
            
            # Adjacency
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    r, c = row + dr, col + dc
                    if 0 <= r < board.size and 0 <= c < board.size:
                        if board.board[r][c] != Player.EMPTY:
                            score += 10000
            
            # Pattern potential
            board.board[row][col] = Player.AI
            for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                line = board._get_line(row, col, dr, dc)
                ai_count = line.count('X')
                
                if ai_count == 4:
                    score += 50000
                elif ai_count == 3:
                    score += 10000
                elif ai_count == 2:
                    score += 1000
            
            board.board[row][col] = Player.EMPTY
            
            scored.append((score, (row, col)))
        
        scored.sort(reverse=True)
        return [move for _, move in scored]

    def _minimax(self, board: GomokuBoardAdvanced, depth: int, is_max: bool,
                 alpha: float, beta: float) -> int:
        """Minimax with alpha-beta pruning"""
        # Terminal states
        won, _ = board.check_winner(Player.AI)
        if won:
            return 100000 + depth * 1000
        
        won, _ = board.check_winner(Player.HUMAN)
        if won:
            return -100000 - depth * 1000
        
        if depth == 0:
            return board.evaluate_board()
        
        if is_max:
            max_eval = float('-inf')
            for row, col in self._rank_moves(board, board.get_valid_moves())[:8]:
                board.board[row][col] = Player.AI
                board.last_move = (row, col)
                
                eval_score = self._minimax(board, depth - 1, False, alpha, beta)
                board.board[row][col] = Player.EMPTY
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            return max_eval
        else:
            min_eval = float('inf')
            for row, col in self._rank_moves(board, board.get_valid_moves())[:8]:
                board.board[row][col] = Player.HUMAN
                board.last_move = (row, col)
                
                eval_score = self._minimax(board, depth - 1, True, alpha, beta)
                board.board[row][col] = Player.EMPTY
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            
            return min_eval


class GomokuGUI:
    """GUI Interface"""

    def __init__(self, root):
        self.root = root
        self.root.title("AI 五子棋 - 人类级别智能")
        self.root.geometry("900x1000")
        
        self.board_size = 15
        self.cell_size = 50
        self.board_offset = 25
        
        self.board = GomokuBoardAdvanced(self.board_size)
        self.ai = AdvancedGomokuAI(depth=8)
        
        self.game_over = False
        self.ai_thinking = False
        self.winning_positions = []
        
        self._create_widgets()

    def _create_widgets(self):
        """Create UI"""
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10)
        
        title_label = tk.Label(title_frame, text="AI 五子棋 - 人类级别", font=("Arial", 24, "bold"))
        title_label.pack()
        
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=5)
        
        self.status_label = tk.Label(status_frame, text="你的回合 (白子)", font=("Arial", 14), fg="blue")
        self.status_label.pack()
        
        board_frame = tk.Frame(self.root)
        board_frame.pack()
        
        self.canvas = tk.Canvas(board_frame, 
                                width=self.cell_size * self.board_size + 2 * self.board_offset,
                                height=self.cell_size * self.board_size + 2 * self.board_offset,
                                bg="wheat")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)
        
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="新游戏", command=self._reset, 
                  font=("Arial", 12), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="撤销", command=self._undo,
                  font=("Arial", 12), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="退出", command=self.root.quit,
                  font=("Arial", 12), width=10).pack(side=tk.LEFT, padx=5)
        
        self.info_label = tk.Label(self.root, text="点击棋盘下棋", font=("Arial", 10), fg="gray")
        self.info_label.pack(pady=5)
        
        self._draw()

    def _pixel_to_coords(self, px: int, py: int) -> Optional[Tuple[int, int]]:
        """Convert pixel to board coords"""
        x = px - self.board_offset
        y = py - self.board_offset
        
        if x < 0 or y < 0 or x > self.cell_size * self.board_size or y > self.cell_size * self.board_size:
            return None
        
        col = round(x / self.cell_size)
        row = round(y / self.cell_size)
        
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return (row, col)
        
        return None

    def _draw(self):
        """Draw board"""
        self.canvas.delete("all")
        
        # Grid
        for i in range(self.board_size):
            x = self.board_offset + i * self.cell_size
            y1 = self.board_offset
            y2 = self.board_offset + self.cell_size * (self.board_size - 1)
            self.canvas.create_line(x, y1, x, y2, fill="black", width=1)
            
            y = self.board_offset + i * self.cell_size
            x1 = self.board_offset
            x2 = self.board_offset + self.cell_size * (self.board_size - 1)
            self.canvas.create_line(x1, y, x2, y, fill="black", width=1)
        
        # Stars
        for row, col in [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]:
            x = self.board_offset + col * self.cell_size
            y = self.board_offset + row * self.cell_size
            self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="black")
        
        # Pieces
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board.board[row][col] != Player.EMPTY:
                    self._draw_piece(row, col, self.board.board[row][col])
        
        # Win line
        if self.winning_positions:
            for i in range(len(self.winning_positions) - 1):
                r1, c1 = self.winning_positions[i]
                r2, c2 = self.winning_positions[i + 1]
                x1 = self.board_offset + c1 * self.cell_size
                y1 = self.board_offset + r1 * self.cell_size
                x2 = self.board_offset + c2 * self.cell_size
                y2 = self.board_offset + r2 * self.cell_size
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=3)

    def _draw_piece(self, row: int, col: int, player: Player):
        """Draw piece"""
        x = self.board_offset + col * self.cell_size
        y = self.board_offset + row * self.cell_size
        r = self.cell_size // 2 - 3
        
        color = "black" if player == Player.AI else "white"
        
        self.canvas.create_oval(x - r, y - r, x + r, y + r,
                               fill=color, outline="gray", width=2)

    def _on_click(self, event):
        """Handle click"""
        if self.game_over or self.ai_thinking:
            return
        
        coords = self._pixel_to_coords(event.x, event.y)
        if coords:
            self._human_move(*coords)

    def _human_move(self, row: int, col: int):
        """Human move"""
        if not self.board.is_valid_move(row, col):
            self.info_label.config(text="无效位置！")
            return
        
        self.board.make_move(row, col, Player.HUMAN)
        self._draw()
        
        won, pos = self.board.check_winner(Player.HUMAN)
        if won:
            self.winning_positions = pos
            self._draw()
            self.game_over = True
            self.status_label.config(text="🎉 你赢了！", fg="green")
            messagebox.showinfo("游戏结束", "恭喜！你赢了！")
            return
        
        self.ai_thinking = True
        self.status_label.config(text="AI 思考中...", fg="orange")
        self.root.update()
        
        threading.Thread(target=self._ai_move_thread, daemon=True).start()

    def _ai_move_thread(self):
        """AI move"""
        move = self.ai.get_best_move(self.board)
        
        if move:
            self.root.after(0, lambda m=move: self._ai_move(m))
        else:
            self.root.after(0, lambda: self._end("棋盘已满，平局！"))

    def _ai_move(self, move: Tuple[int, int]):
        """Execute AI move"""
        row, col = move
        self.board.make_move(row, col, Player.AI)
        self._draw()
        
        won, pos = self.board.check_winner(Player.AI)
        if won:
            self.winning_positions = pos
            self._draw()
            self.game_over = True
            self.status_label.config(text="😢 AI 赢了", fg="red")
            self.ai_thinking = False
            messagebox.showinfo("游戏结束", f"AI 在 ({row}, {col}) 赢了！")
            return
        
        self.status_label.config(text="你的回合 (白子)", fg="blue")
        self.info_label.config(text=f"AI 下在: ({row}, {col})")
        self.ai_thinking = False

    def _end(self, msg: str):
        """End game"""
        self.game_over = True
        self.ai_thinking = False
        self.status_label.config(text="游戏结束", fg="red")
        messagebox.showinfo("游戏结束", msg)

    def _undo(self):
        """Undo"""
        if self.game_over:
            messagebox.showinfo("提示", "游戏已结束")
            return
        
        if len(self.board.move_history) >= 2:
            self.board.undo_move()
            self.board.undo_move()
            self.winning_positions = []
            self.game_over = False
            self.status_label.config(text="你的回合 (白子)", fg="blue")
            self.info_label.config(text="已撤销")
            self._draw()

    def _reset(self):
        """Reset"""
        self.board = GomokuBoardAdvanced(self.board_size)
        self.game_over = False
        self.ai_thinking = False
        self.winning_positions = []
        self.status_label.config(text="你的回合 (白子)", fg="blue")
        self.info_label.config(text="游戏已重置")
        self._draw()


def main():
    """Main"""
    root = tk.Tk()
    gui = GomokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
