#!/usr/bin/env python3
"""
Advanced AI Gomoku with True Intelligence
Features: Real threat detection, double-threat strategy, deep search with optimization
"""

import tkinter as tk
from tkinter import messagebox
from enum import Enum
from typing import List, Tuple, Optional, Dict, Set
import threading
import time


class Player(Enum):
    """Player types"""
    HUMAN = 1
    AI = 2
    EMPTY = 0


class PatternType(Enum):
    """Pattern classification"""
    FIVE = 10000000        # 五连
    LIVE_FOUR = 100000     # 活四（两头空）
    CHONG_FOUR = 10000     # 冲四（一头堵）
    LIVE_THREE = 1000      # 活三（两头空）
    CHONG_THREE = 100      # 冲三（一头堵）
    LIVE_TWO = 10          # 活二
    CHONG_TWO = 1          # 冲二
    ONE = 0.1              # 单子


class GomokuBoardAdvanced:
    """Advanced Gomoku board with strategic analysis"""

    def __init__(self, size: int = 15):
        self.size = size
        self.board = [[Player.EMPTY for _ in range(size)] for _ in range(size)]
        self.move_history = []
        self.last_move = None
        self.zobrist_hash = 0
        self.zobrist_table = self._init_zobrist()
        self.transposition_table = {}
        self.pattern_cache = {}

    def _init_zobrist(self) -> Dict:
        """Initialize Zobrist hash tables for fast board state hashing"""
        import random
        random.seed(42)
        zobrist = {}
        for row in range(self.size):
            for col in range(self.size):
                zobrist[(row, col, Player.AI)] = random.getrandbits(64)
                zobrist[(row, col, Player.HUMAN)] = random.getrandbits(64)
        return zobrist

    def make_move(self, row: int, col: int, player: Player) -> bool:
        """Place a piece on the board"""
        if not self.is_valid_move(row, col):
            return False
        self.board[row][col] = player
        self.move_history.append((row, col, player))
        self.last_move = (row, col)
        self.zobrist_hash ^= self.zobrist_table[(row, col, player)]
        self.pattern_cache.clear()  # Invalidate cache
        return True

    def undo_move(self):
        """Undo the last move"""
        if self.move_history:
            row, col, player = self.move_history.pop()
            self.board[row][col] = Player.EMPTY
            self.zobrist_hash ^= self.zobrist_table[(row, col, player)]
            self.pattern_cache.clear()
            if self.move_history:
                self.last_move = self.move_history[-1][:2]
            else:
                self.last_move = None

    def is_valid_move(self, row: int, col: int) -> bool:
        """Check if a move is valid"""
        return (0 <= row < self.size and 
                0 <= col < self.size and 
                self.board[row][col] == Player.EMPTY)

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Get candidate moves - only near existing pieces"""
        if not self.move_history:
            return [(self.size // 2, self.size // 2)]
        
        moves = set()
        search_range = 3
        
        # Search around recent moves
        for row, col, _ in self.move_history[-3:]:
            for dr in range(-search_range, search_range + 1):
                for dc in range(-search_range, search_range + 1):
                    r, c = row + dr, col + dc
                    if self.is_valid_move(r, c):
                        moves.add((r, c))
        
        return list(moves)

    def check_winner(self, player: Player) -> Tuple[bool, Optional[List[Tuple[int, int]]]]:
        """Check if a player has won"""
        if not self.last_move:
            return False, None
        
        row, col = self.last_move
        
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            positions = self._get_line_positions(row, col, dr, dc, player, length=5)
            if len(positions) >= 5:
                return True, positions[:5]
        
        return False, None

    def _get_line_positions(self, row: int, col: int, dr: int, dc: int, 
                           player: Player, length: int = 9) -> List[Tuple[int, int]]:
        """Get consecutive pieces in a direction"""
        positions = []
        
        # Go backward
        r, c = row - dr, col - dc
        while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
            positions.insert(0, (r, c))
            r -= dr
            c -= dc
        
        # Add center
        positions.append((row, col))
        
        # Go forward
        r, c = row + dr, col + dc
        while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
            positions.append((r, c))
            r += dr
            c += dc
        
        return positions[:length]

    def find_threats(self, player: Player) -> List[Dict]:
        """Find all threats for a player: winning moves, attack opportunities"""
        threats = []
        
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] != player:
                    continue
                
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                    # Skip if we've already analyzed this direction
                    if dr != 0 and dc == 0:  # Only check right and down directions to avoid duplication
                        pass
                    elif dr == 0 and dc == 1:
                        pass
                    elif dr == 1 and dc == 1:
                        pass
                    elif dr == 1 and dc == -1:
                        pass
                    else:
                        continue
                    
                    threat = self._analyze_line_threat(row, col, dr, dc, player)
                    if threat:
                        threats.append(threat)
        
        return threats

    def _analyze_line_threat(self, row: int, col: int, dr: int, dc: int, 
                            player: Player) -> Optional[Dict]:
        """Analyze a single line for threats"""
        # Get extended line (looking for patterns)
        line = []
        positions = []
        
        for i in range(-4, 5):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < self.size and 0 <= c < self.size:
                if self.board[r][c] == player:
                    line.append('X')
                elif self.board[r][c] == Player.EMPTY:
                    line.append('_')
                else:
                    line.append('O')
                positions.append((r, c))
            else:
                line.append('#')
        
        # Find pattern
        threat_moves = []
        
        # Check for "4 in a row" - can win immediately
        for i in range(len(line) - 4):
            segment = line[i:i+5]
            if segment.count('X') == 4 and segment.count('_') == 1:
                empty_idx = segment.index('_')
                threat_moves.append({
                    'type': 'WIN',
                    'pos': positions[i + empty_idx],
                    'priority': 1000000
                })
        
        # Check for "3 in a row with 2 opens" - can create 4
        for i in range(len(line) - 4):
            segment = line[i:i+5]
            if segment == ['_', 'X', 'X', 'X', '_']:
                threat_moves.append({
                    'type': 'LIVE_FOUR',
                    'pos': (positions[i][0], positions[i][1]),
                    'priority': 100000
                })
                threat_moves.append({
                    'type': 'LIVE_FOUR',
                    'pos': (positions[i+4][0], positions[i+4][1]),
                    'priority': 100000
                })
        
        # Check for "3 in a row" 
        for i in range(len(line) - 3):
            segment = line[i:i+4]
            if segment.count('X') == 3 and segment.count('_') == 1:
                empty_idx = segment.index('_')
                threat_moves.append({
                    'type': 'LIVE_THREE',
                    'pos': positions[i + empty_idx],
                    'priority': 5000
                })
        
        return threat_moves if threat_moves else None

    def evaluate_board(self) -> int:
        """Evaluate board state - AI wants to maximize, HUMAN wants to minimize"""
        if self.zobrist_hash in self.transposition_table:
            return self.transposition_table[self.zobrist_hash]
        
        ai_score = self._calculate_player_score(Player.AI)
        human_score = self._calculate_player_score(Player.HUMAN)
        
        score = ai_score - human_score
        self.transposition_table[self.zobrist_hash] = score
        return score

    def _calculate_player_score(self, player: Player) -> int:
        """Calculate score for a player based on piece patterns"""
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        evaluated = set()
        
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == player:
                    for dr, dc in directions:
                        line = self._get_line(row, col, dr, dc)
                        line_key = (row, col, dr, dc)
                        
                        if line_key not in evaluated:
                            evaluated.add(line_key)
                            score += self._evaluate_pattern_line(line, player)
        
        return score

    def _get_line(self, row: int, col: int, dr: int, dc: int) -> Tuple:
        """Get 5-element line centered around (row, col)"""
        line = ['_'] * 5
        
        for i in range(-2, 3):
            r = row + i * dr
            c = col + i * dc
            if 0 <= r < self.size and 0 <= c < self.size:
                cell = self.board[r][c]
                if cell == Player.EMPTY:
                    line[i + 2] = '_'
                elif cell == Player.AI:
                    line[i + 2] = 'X'
                else:
                    line[i + 2] = 'O'
            else:
                line[i + 2] = '#'
        
        return tuple(line)

    def _evaluate_pattern_line(self, line: Tuple, player: Player) -> int:
        """Evaluate pattern value"""
        player_char = 'X' if player == Player.AI else 'O'
        opponent_char = 'O' if player == Player.AI else 'X'
        
        # Convert line to string for pattern matching
        line_str = ''.join(line)
        score = 0
        
        # Five in a row
        if player_char * 5 in line_str:
            score += 1000000
        
        # Four in a row (with opening)
        if f'_{player_char*4}' in line_str or f'{player_char*4}_' in line_str:
            score += 50000
        
        # Four in a row (blocked on one side)
        if f'{opponent_char}{player_char*4}' in line_str or f'{player_char*4}{opponent_char}' in line_str:
            score += 5000
        
        # Three in a row (with both sides open)
        if f'_{player_char*3}_' in line_str:
            score += 8000
        
        # Three in a row (with one side open)
        patterns_3 = [
            f'_{player_char*3}',
            f'{player_char*3}_',
            f'{opponent_char}{player_char*3}_',
            f'_{player_char*3}{opponent_char}'
        ]
        for pattern in patterns_3:
            if pattern in line_str:
                score += 800
                break
        
        # Two in a row (with opening)
        if f'_{player_char*2}_' in line_str:
            score += 100
        
        # Two in a row
        patterns_2 = [f'_{player_char*2}', f'{player_char*2}_']
        for pattern in patterns_2:
            if pattern in line_str:
                score += 20
                break
        
        # Single piece
        if player_char in line_str:
            score += 1
        
        return score


class AdvancedGomokuAI:
    """Advanced AI with strategic planning"""

    def __init__(self, depth: int = 6, time_limit: float = 5.0):
        self.depth = depth
        self.time_limit = time_limit
        self.nodes_evaluated = 0
        self.start_time = 0

    def get_best_move(self, board: GomokuBoardAdvanced) -> Optional[Tuple[int, int]]:
        """Find best move with strategy"""
        self.start_time = time.time()
        self.nodes_evaluated = 0
        
        if len(board.move_history) == 0:
            return (board.size // 2, board.size // 2)
        
        if len(board.move_history) == 1:
            # Opening: place near center
            row, col = board.move_history[0][:2]
            return (row + 1, col) if board.is_valid_move(row + 1, col) else (row, col + 1)
        
        # 1. Check immediate winning moves
        move = self._find_immediate_win(board, Player.AI)
        if move:
            return move
        
        # 2. Check immediate defensive blocks
        move = self._find_immediate_win(board, Player.HUMAN)
        if move:
            return move
        
        # 3. Look for double-threat opportunities
        move = self._find_double_threat(board)
        if move:
            return move
        
        # 4. Deep minimax search for strategic moves
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None
        
        # Prioritize candidate moves
        candidate_moves = self._prioritize_moves(board, valid_moves)
        
        best_move = candidate_moves[0]
        best_score = float('-inf')
        
        for move in candidate_moves:
            row, col = move
            board.board[row][col] = Player.AI
            board.last_move = (row, col)
            
            score = self._minimax(board, self.depth - 1, False, float('-inf'), float('inf'))
            
            board.board[row][col] = Player.EMPTY
            
            if score > best_score:
                best_score = score
                best_move = move
            
            # Time check
            if time.time() - self.start_time > self.time_limit * 0.9:
                break
        
        return best_move

    def _find_immediate_win(self, board: GomokuBoardAdvanced, player: Player) -> Optional[Tuple[int, int]]:
        """Find winning move in 1 ply"""
        for row, col in board.get_valid_moves():
            board.board[row][col] = player
            board.last_move = (row, col)
            
            won, _ = board.check_winner(player)
            board.board[row][col] = Player.EMPTY
            
            if won:
                return (row, col)
        
        return None

    def _find_double_threat(self, board: GomokuBoardAdvanced) -> Optional[Tuple[int, int]]:
        """Find move that creates 2 winning threats"""
        for row, col in board.get_valid_moves():
            board.board[row][col] = Player.AI
            board.last_move = (row, col)
            
            # Count how many moves in one place can win
            winning_threats = 0
            for next_row, next_col in board.get_valid_moves():
                board.board[next_row][next_col] = Player.AI
                board.last_move = (next_row, next_col)
                
                won, _ = board.check_winner(Player.AI)
                board.board[next_row][next_col] = Player.EMPTY
                
                if won:
                    winning_threats += 1
                    if winning_threats >= 2:
                        break
            
            board.board[row][col] = Player.EMPTY
            
            if winning_threats >= 2:
                return (row, col)
        
        return None

    def _prioritize_moves(self, board: GomokuBoardAdvanced, 
                         moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Sort moves by strategic value"""
        scored_moves = []
        
        for move in moves:
            row, col = move
            score = 0
            
            # Distance to last move
            if board.last_move:
                last_row, last_col = board.last_move
                dist = max(abs(row - last_row), abs(col - last_col))
                score += (4 - min(dist, 4)) * 10000
            
            # Adjacent pieces
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    r, c = row + dr, col + dc
                    if 0 <= r < board.size and 0 <= c < board.size:
                        if board.board[r][c] != Player.EMPTY:
                            score += 5000
            
            # Pattern potential
            for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                board.board[row][col] = Player.AI
                line = board._get_line(row, col, dr, dc)
                board.board[row][col] = Player.EMPTY
                
                line_str = ''.join(line)
                
                if line_str.count('X') >= 3:
                    score += 20000
                elif line_str.count('X') == 2:
                    score += 5000
            
            scored_moves.append((score, move))
        
        scored_moves.sort(reverse=True)
        return [move for _, move in scored_moves[:30]]

    def _minimax(self, board: GomokuBoardAdvanced, depth: int, is_maximizing: bool,
                 alpha: float, beta: float) -> int:
        """Minimax with alpha-beta pruning"""
        # Terminal conditions
        won, _ = board.check_winner(Player.AI)
        if won:
            return 100000 + (self.depth - depth) * 100
        
        won, _ = board.check_winner(Player.HUMAN)
        if won:
            return -100000 - (self.depth - depth) * 100
        
        if depth == 0 or time.time() - self.start_time > self.time_limit:
            return board.evaluate_board()
        
        self.nodes_evaluated += 1
        
        if is_maximizing:
            max_eval = float('-inf')
            for row, col in self._prioritize_moves(board, board.get_valid_moves()):
                board.board[row][col] = Player.AI
                board.last_move = (row, col)
                
                eval_score = self._minimax(board, depth - 1, False, alpha, beta)
                board.board[row][col] = Player.EMPTY
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break
            
            return max_eval if max_eval != float('-inf') else board.evaluate_board()
        else:
            min_eval = float('inf')
            for row, col in self._prioritize_moves(board, board.get_valid_moves()):
                board.board[row][col] = Player.HUMAN
                board.last_move = (row, col)
                
                eval_score = self._minimax(board, depth - 1, True, alpha, beta)
                board.board[row][col] = Player.EMPTY
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break
            
            return min_eval if min_eval != float('inf') else board.evaluate_board()


class GomokuGUI:
    """GUI for Gomoku game"""

    def __init__(self, root):
        self.root = root
        self.root.title("AI 五子棋 - 智能版 (Advanced AI)")
        self.root.geometry("900x1000")
        
        self.board_size = 15
        self.cell_size = 50
        self.board = GomokuBoardAdvanced(self.board_size)
        self.ai = AdvancedGomokuAI(depth=6)
        
        self.game_over = False
        self.ai_thinking = False
        self.winning_positions = []
        
        self._create_widgets()

    def _create_widgets(self):
        """Create GUI widgets"""
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10)
        
        title_label = tk.Label(title_frame, text="AI 五子棋 - 智能版", font=("Arial", 24, "bold"))
        title_label.pack()
        
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=5)
        
        self.status_label = tk.Label(status_frame, text="你的回合 (白子)", font=("Arial", 14), fg="blue")
        self.status_label.pack()
        
        board_frame = tk.Frame(self.root)
        board_frame.pack()
        
        self.canvas = tk.Canvas(board_frame, 
                                width=self.cell_size * self.board_size + 50,
                                height=self.cell_size * self.board_size + 50,
                                bg="wheat")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        
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
        outline = "gray" if player == Player.HUMAN else "gray"
        
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
        
        won, positions = self.board.check_winner(Player.HUMAN)
        if won:
            self.winning_positions = positions
            self._draw_board()
            self.game_over = True
            self.status_label.config(text="🎉 你赢了！", fg="green")
            messagebox.showinfo("游戏结束", "恭喜！你赢了！")
            return
        
        self.ai_thinking = True
        self.status_label.config(text="AI 思考中...", fg="orange")
        self.root.update()
        
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
        
        won, positions = self.board.check_winner(Player.AI)
        if won:
            self.winning_positions = positions
            self._draw_board()
            self.game_over = True
            self.status_label.config(text="😢 AI 赢了", fg="red")
            self.ai_thinking = False
            messagebox.showinfo("游戏结束", f"AI 在位置 ({row}, {col}) 赢了！")
            return
        
        self.status_label.config(text="你的回合 (白子)", fg="blue")
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
            self.board.undo_move()
            self.board.undo_move()
            self.winning_positions = []
            self.game_over = False
            self.status_label.config(text="你的回合 (白子)", fg="blue")
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
        self.status_label.config(text="你的回合 (白子)", fg="blue")
        self.info_label.config(text="游戏已重置")
        self._draw_board()


def main():
    """Entry point"""
    root = tk.Tk()
    gui = GomokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
