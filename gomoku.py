#!/usr/bin/env python3
"""
AI Gomoku (Five in a Row) Game
A Python implementation of Gomoku with AI opponent using minimax algorithm.
"""

import sys
from typing import List, Tuple, Optional
from enum import Enum
import random


class Player(Enum):
    """Player types"""
    HUMAN = 1
    AI = 2
    EMPTY = 0


class GomokuBoard:
    """Represents the Gomoku game board"""

    def __init__(self, size: int = 15):
        self.size = size
        self.board = [[Player.EMPTY for _ in range(size)] for _ in range(size)]
        self.move_history = []

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

    def check_winner(self, player: Player) -> bool:
        """Check if a player has won"""
        # Check horizontal, vertical, and diagonal
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == player:
                    for dr, dc in directions:
                        if self._check_direction(row, col, dr, dc, player):
                            return True
        return False

    def _check_direction(self, row: int, col: int, dr: int, dc: int, player: Player) -> bool:
        """Check if five pieces in a row in a given direction"""
        count = 0
        r, c = row, col
        while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
            count += 1
            r += dr
            c += dc
        return count >= 5

    def is_game_over(self) -> bool:
        """Check if game is over"""
        return self.check_winner(Player.HUMAN) or self.check_winner(Player.AI)

    def evaluate_board(self) -> int:
        """Evaluate board state for AI"""
        ai_score = self._calculate_score(Player.AI)
        human_score = self._calculate_score(Player.HUMAN)
        return ai_score - human_score

    def _calculate_score(self, player: Player) -> int:
        """Calculate score for a player"""
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == player:
                    for dr, dc in directions:
                        score += self._count_in_direction(row, col, dr, dc, player)
        return score

    def _count_in_direction(self, row: int, col: int, dr: int, dc: int, player: Player) -> int:
        """Count consecutive pieces in a direction"""
        count = 0
        r, c = row + dr, col + dc
        while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
            count += 1
            r += dr
            c += dc
        return count

    def display(self):
        """Display the board"""
        print("\n  ", end="")
        for i in range(self.size):
            print(f"{i:2d}", end=" ")
        print()
        
        for row in range(self.size):
            print(f"{row:2d}", end=" ")
            for col in range(self.size):
                cell = self.board[row][col]
                if cell == Player.HUMAN:
                    print(" X", end=" ")
                elif cell == Player.AI:
                    print(" O", end=" ")
                else:
                    print(" .", end=" ")
            print()
        print()

    def undo_move(self):
        """Undo the last move"""
        if self.move_history:
            row, col, _ = self.move_history.pop()
            self.board[row][col] = Player.EMPTY


class GomokuAI:
    """AI player using minimax algorithm with alpha-beta pruning"""

    def __init__(self, depth: int = 3):
        self.depth = depth

    def get_best_move(self, board: GomokuBoard) -> Optional[Tuple[int, int]]:
        """Find the best move using minimax"""
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None
        
        # Prioritize moves near existing pieces
        prioritized_moves = self._prioritize_moves(board, valid_moves)
        
        best_score = float('-inf')
        best_move = prioritized_moves[0]
        
        for move in prioritized_moves[:50]:  # Limit search space
            row, col = move
            board.board[row][col] = Player.AI
            score = self._minimax(board, self.depth - 1, False, float('-inf'), float('inf'))
            board.board[row][col] = Player.EMPTY
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move

    def _minimax(self, board: GomokuBoard, depth: int, is_maximizing: bool, 
                 alpha: float, beta: float) -> int:
        """Minimax with alpha-beta pruning"""
        if board.check_winner(Player.AI):
            return 10000
        if board.check_winner(Player.HUMAN):
            return -10000
        if depth == 0:
            return board.evaluate_board()
        
        if is_maximizing:
            max_eval = float('-inf')
            for row, col in self._get_candidate_moves(board):
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
            for row, col in self._get_candidate_moves(board):
                board.board[row][col] = Player.HUMAN
                eval_score = self._minimax(board, depth - 1, True, alpha, beta)
                board.board[row][col] = Player.EMPTY
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _prioritize_moves(self, board: GomokuBoard, moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Prioritize moves near existing pieces"""
        if not board.move_history:
            center = board.size // 2
            return [(center, center)] + moves
        
        scored_moves = []
        for move in moves:
            score = self._move_score(board, move)
            scored_moves.append((score, move))
        
        scored_moves.sort(reverse=True)
        return [move for _, move in scored_moves]

    def _move_score(self, board: GomokuBoard, move: Tuple[int, int]) -> int:
        """Score a move based on proximity to existing pieces"""
        row, col = move
        score = 0
        
        for dr in [-2, -1, 0, 1, 2]:
            for dc in [-2, -1, 0, 1, 2]:
                r, c = row + dr, col + dc
                if 0 <= r < board.size and 0 <= c < board.size:
                    if board.board[r][c] != Player.EMPTY:
                        score += (3 - max(abs(dr), abs(dc)))
        
        return score

    def _get_candidate_moves(self, board: GomokuBoard, limit: int = 20) -> List[Tuple[int, int]]:
        """Get candidate moves to evaluate"""
        prioritized = self._prioritize_moves(board, board.get_valid_moves())
        return prioritized[:limit]


class GomokuGame:
    """Main game controller"""

    def __init__(self, board_size: int = 15, ai_depth: int = 3):
        self.board = GomokuBoard(board_size)
        self.ai = GomokuAI(ai_depth)
        self.current_player = Player.HUMAN

    def play(self):
        """Main game loop"""
        print("\n=== Welcome to Gomoku (Five in a Row) ===")
        print(f"Board size: {self.board.size}x{self.board.size}")
        print("You are X, AI is O")
        print("Enter moves as: row col (e.g., '7 7')")
        print("Type 'quit' to exit, 'undo' to undo last move\n")
        
        while True:
            self.board.display()
            
            if self.current_player == Player.HUMAN:
                if not self._human_move():
                    print("Game ended.")
                    break
            else:
                self._ai_move()
            
            if self.board.check_winner(Player.HUMAN):
                self.board.display()
                print("🎉 You win!")
                break
            elif self.board.check_winner(Player.AI):
                self.board.display()
                print("😔 AI wins!")
                break
            
            self.current_player = Player.AI if self.current_player == Player.HUMAN else Player.HUMAN

    def _human_move(self) -> bool:
        """Handle human player input"""
        while True:
            user_input = input("Your move (row col): ").strip()
            
            if user_input.lower() == 'quit':
                return False
            elif user_input.lower() == 'undo':
                self.board.undo_move()
                self.board.undo_move()
                print("Move undone.")
                return True
            
            try:
                row, col = map(int, user_input.split())
                if self.board.make_move(row, col, Player.HUMAN):
                    return True
                else:
                    print("Invalid move. Try again.")
            except (ValueError, IndexError):
                print("Invalid input. Use format: row col")

    def _ai_move(self):
        """Handle AI move"""
        print("AI is thinking...")
        move = self.ai.get_best_move(self.board)
        if move:
            row, col = move
            self.board.make_move(row, col, Player.AI)
            print(f"AI plays at: {row} {col}")
        else:
            print("No valid moves available.")


def main():
    """Entry point"""
    game = GomokuGame(board_size=15, ai_depth=3)
    game.play()


if __name__ == "__main__":
    main()
