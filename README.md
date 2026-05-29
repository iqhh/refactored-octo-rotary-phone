# AI Gomoku Game (Five in a Row)

A Python implementation of Gomoku with an AI opponent using the minimax algorithm with alpha-beta pruning.

## Overview

Gomoku is a classic strategy board game where two players take turns placing stones on a 15×15 board. The objective is to be the first to form a continuous line of five stones in any direction (horizontal, vertical, or diagonal).

## Features

- **15×15 Game Board**: Classic Gomoku board size
- **AI Opponent**: Intelligent AI using minimax algorithm with alpha-beta pruning
- **Game Features**:
  - Undo moves
  - Real-time board display
  - Winner detection
  - Move history tracking

## How to Play

### Installation

No external dependencies required. Just Python 3.6+

```bash
python gomoku.py
```

### Game Rules

1. You play as **X**, the AI plays as **O**
2. Players alternate turns
3. On your turn, enter the row and column where you want to place your stone
4. Coordinates range from 0 to 14
5. The first to get 5 stones in a row (horizontally, vertically, or diagonally) wins

### Commands

- **Normal move**: Enter `row col` (e.g., `7 7` for the center)
- **Undo**: Type `undo` to take back your last move and the AI's last move
- **Quit**: Type `quit` to exit the game

## AI Algorithm

The AI uses the **minimax algorithm with alpha-beta pruning** to evaluate moves:

1. **Minimax**: Recursively evaluates game states by simulating both players' moves
2. **Alpha-Beta Pruning**: Optimizes the search by eliminating branches that cannot affect the final decision
3. **Move Prioritization**: Prioritizes moves near existing pieces to reduce search space
4. **Board Evaluation**: Scores board positions based on potential winning patterns

### Configuration

You can adjust the AI difficulty by changing the `ai_depth` parameter in the `main()` function:

- `ai_depth=2`: Faster, easier
- `ai_depth=3`: Balanced (default)
- `ai_depth=4`: Slower, harder

```python
game = GomokuGame(board_size=15, ai_depth=4)
```

## Example Game Session

```
=== Welcome to Gomoku (Five in a Row) ===
Board size: 15x15
You are X, AI is O
Enter moves as: row col (e.g., '7 7')
Type 'quit' to exit, 'undo' to undo last move

    0  1  2  3  4  5  6  7  8  9 10 11 12 13 14
 0  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
...
 7  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
...
Your move (row col): 7 7
AI is thinking...
AI plays at: 8 7
```

## File Structure

- `gomoku.py`: Main game implementation
- `requirements.txt`: Project dependencies (none required)
- `README.md`: This file

## Classes

### `Player` (Enum)
Represents different player types: HUMAN, AI, EMPTY

### `GomokuBoard`
Manages the game board state:
- `make_move()`: Place a piece on the board
- `check_winner()`: Check if a player has won
- `evaluate_board()`: Score the current board state
- `display()`: Print the current board

### `GomokuAI`
AI player implementation:
- `get_best_move()`: Find the best move using minimax
- `_minimax()`: Core minimax algorithm with alpha-beta pruning
- `_prioritize_moves()`: Prioritize moves for faster evaluation

### `GomokuGame`
Main game controller:
- `play()`: Main game loop
- `_human_move()`: Handle player input
- `_ai_move()`: Execute AI move

## Performance Notes

- The AI evaluates up to 50 candidate moves per turn for performance balance
- Alpha-beta pruning significantly reduces the search space
- Move prioritization focuses on strategically important positions
- With `ai_depth=3`, the AI typically responds within a few seconds

## Future Enhancements

- [ ] GUI interface using tkinter or pygame
- [ ] Different board sizes
- [ ] Difficulty settings
- [ ] Game statistics and analysis
- [ ] Opening book for better early-game play
- [ ] Transposition tables for faster evaluation
- [ ] Monte Carlo Tree Search (MCTS) implementation

## License

MIT License

## Contributing

Feel free to submit issues and enhancement requests!
