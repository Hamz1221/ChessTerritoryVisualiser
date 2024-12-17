# Handle and save game state, determine valid moves, move log, etc.
from typing import Tuple
from Pieces import *

Square = Tuple[int, int]


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq: Square, endSq: Square, board: list) -> None:
        self.startRow, self.startCol = startSq
        self.endRow, self.endCol = endSq
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.boardBefore = board
        self.moveID = self.startRow * 1000 + self.startCol * \
            100 + self.endRow * 10 + self.endCol
        # other checks like takes, checks, etc

    def getChessNotation(self) -> str:
        # can flesh this out more - real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c) -> str:
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


class GameState():
    def __init__(self) -> None:
        self.board = [
            [B_R, B_N, B_B, B_Q, B_K, B_B, B_N, B_R],
            [B_P, B_P, B_P, B_P, B_P, B_P, B_P, B_P],
            [___, ___, ___, ___, ___, ___, ___, ___],
            [___, ___, ___, ___, ___, ___, ___, ___],
            [___, ___, ___, ___, ___, ___, ___, ___],
            [___, ___, ___, ___, ___, ___, ___, ___],
            [W_P, W_P, W_P, W_P, W_P, W_P, W_P, W_P],
            [W_R, W_N, W_B, W_Q, W_K, W_B, W_N, W_R],
        ]
        self.whiteToMove = True
        self.moveLog: list[Move] = []

    # Executes move, not working for castling, en passant and promotions
    def makeMove(self, move: Move):
        self.board[move.startRow][move.startCol] = EMPTY
        self.board[move.endRow][move.endCol] = move.pieceMoved
        #  log move for undos, see history, etc
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove  #  switch turn

    def undoMove(self):
        if len(self.moveLog) > 0:
            move: Move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  #  switch turn back

    def getValidMoves(self) -> list[Move]:
        '''
        All moves considering checks
        '''
        return self.getAllPossibleMoves()  # for now we will not worry about checks

    def getAllPossibleMoves(self) -> list[Move]:
        '''
        All moves without considering checks
        '''
        moves: list[Move] = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    match piece:
                        case "P":
                            self.getPawnMoves(row, col, moves)
                        case "R":
                            self.getRookMoves(row, col, moves)
                        case "N":
                            self.getKnightMoves(row, col, moves)
                        case "B":
                            self.getBishopMoves(row, col, moves)
                        case "K":
                            self.getKingMoves(row, col, moves)
                        case "Q":
                            self.getQueenMoves(row, col, moves)
                        case _:
                            raise ValueError(
                                f"Piece undefined at ({row},{col})")
        return moves

    def getPawnMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all pawn moves at pawn location and add to moves list
        '''
        pass

    def getRookMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all rook moves at rook location and add to moves list
        '''
        pass

    def getKnightMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all knight moves at knight location and add to moves list
        '''
        pass

    def getBishopMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all bishop moves at bishop location and add to moves list
        '''
        pass

    def getKingMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all king moves at king location and add to moves list
        '''
        pass

    def getQueenMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all queen moves at queen location and add to moves list
        '''
        pass
