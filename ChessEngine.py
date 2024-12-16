# Handle and save game state, determine valid moves, move log, etc.
import numpy as np
from pieces import *


class GameState():
    def __init__(self) -> None:
        self.board = np.array([
            [B_R, B_N, B_B, B_Q, B_K, B_B, B_N, B_R],
            [B_P, B_P, B_P, B_P, B_P, B_P, B_P, B_P],
            [___, ___, ___, ___, ___, ___, ___, ___],
            [___, ___, ___, ___, ___, ___, ___, ___],
            [___, ___, ___, ___, ___, ___, ___, ___],
            [___, ___, ___, ___, ___, ___, ___, ___],
            [W_P, W_P, W_P, W_P, W_P, W_P, W_P, W_P],
            [W_R, W_N, W_B, W_Q, W_K, W_B, W_N, W_R],
        ])
        self.whiteToMove = True
        self.moveLog = np.array([])
