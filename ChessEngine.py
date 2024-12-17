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

    def canCaptureSquare(self, row, col) -> bool:
        '''
        Assumes valid square given, returns true is square empty or contains enemy piece, false otherwise
        '''
        return not ((self.board[row][col][0] == 'b' and not self.whiteToMove) or (self.board[row][col][0] == 'w' and self.whiteToMove))

    def onBoard(self, row, col) -> bool:
        return row >= 0 and row < len(self.board) and col >= 0 and col < len(self.board[row])

    def getPawnMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all pawn moves at pawn location and add to moves list
        '''
        if self.whiteToMove:  # white pawn moves
            # 1 square pawn advance
            if row > 0 and self.board[row - 1][col] == EMPTY:
                moves.append(Move((row, col), (row - 1, col), self.board))
                # 2 square pawn advance
                if row == 6 and self.board[row - 2][col] == EMPTY:
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if row > 0 and col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == 'b':  # enemy piece to capture
                    moves.append(
                        Move((row, col), (row - 1, col - 1), self.board))
            if row > 0 and col + 1 < len(self.board[row - 1]):
                if self.board[row - 1][col + 1][0] == 'b':  # enemy piece to capture
                    moves.append(
                        Move((row, col), (row - 1, col + 1), self.board))

        else:  #  black moves
            # 1 square pawn advance
            if row < len(self.board) - 1 and self.board[row + 1][col] == EMPTY:
                moves.append(Move((row, col), (row + 1, col), self.board))
                # 2 square pawn advance
                if row == 1 and self.board[row + 2][col] == EMPTY:
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if row < len(self.board) - 1 and col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == 'w':  # enemy piece to capture
                    moves.append(
                        Move((row, col), (row + 1, col - 1), self.board))
            if row < len(self.board) - 1 and col + 1 < len(self.board[row - 1]):
                if self.board[row + 1][col + 1][0] == 'w':  # enemy piece to capture
                    moves.append(
                        Move((row, col), (row + 1, col + 1), self.board))

    def getRookMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all rook moves at rook location and add to moves list
        '''
        #  Check above and below rook
        for rowShiftInc in [-1, 1]:
            rowShift = rowShiftInc
            while True:
                newRow = row + rowShift
                if newRow < len(self.board) and newRow >= 0:  # row is on the board
                    if self.board[newRow][col] == EMPTY:
                        moves.append(
                            Move((row, col), (newRow, col), self.board))
                    elif (self.board[newRow][col][0] == 'b' and self.whiteToMove) or (self.board[newRow][col][0] == 'w' and not self.whiteToMove):
                        moves.append(
                            Move((row, col), (newRow, col), self.board))
                        break  # cannot look further
                    else:
                        break  # hit wall or ally piece
                    rowShift += rowShiftInc
                else:
                    break  # looking off the board

        # Check to the sides of rook
        for colShiftInc in [-1, 1]:
            colShift = colShiftInc
            while True:
                newCol = col + colShift
                # col is on the board
                if newCol < len(self.board[row]) and newCol >= 0:
                    if self.board[row][newCol] == EMPTY:
                        moves.append(
                            Move((row, col), (row, newCol), self.board))
                    elif (self.board[row][newCol][0] == 'b' and self.whiteToMove) or (self.board[row][newCol][0] == 'w' and not self.whiteToMove):
                        moves.append(
                            Move((row, col), (row, newCol), self.board))
                        break  # cannot look further
                    else:
                        break  # hit wall or ally piece
                    colShift += colShiftInc
                else:
                    break  # looking off the board

    def getKnightMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all knight moves at knight location and add to moves list
        '''
        for rowMultiplier, colMultiplier in [(2, 1), (1, 2)]:
            for rowInc in [-1, 1]:
                newRow = row + (rowMultiplier * rowInc)
                if newRow >= 0 and newRow < len(self.board):  # row on board
                    for colInc in [-1, 1]:
                        newCol = col + (colMultiplier * colInc)
                        # col on board
                        if newCol >= 0 and newCol < len(self.board[newRow]):
                            if self.canCaptureSquare(newRow, newCol):
                                moves.append(
                                    Move((row, col), (newRow, newCol), self.board))

    def getBishopMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all bishop moves at bishop location and add to moves list
        '''
        for rowShiftInc in [-1, 1]:
            for colShiftInc in [-1, 1]:
                rowShift = rowShiftInc
                colShift = colShiftInc
                while True:
                    newRow = row + rowShift
                    newCol = col + colShift
                    if self.onBoard(newRow, newCol):
                        if self.board[newRow][newCol] == EMPTY:
                            moves.append(
                                Move((row, col), (newRow, newCol), self.board))
                        elif self.canCaptureSquare(newRow, newCol):
                            moves.append(
                                Move((row, col), (newRow, newCol), self.board))
                            break  # cannot look further
                        else:
                            break  # hit wall or ally
                        rowShift += rowShiftInc
                        colShift += colShiftInc
                    else:
                        break  # looking off the board

    def getKingMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all king moves at king location and add to moves list
        '''
        for rowShift in [-1, 0, 1]:
            for colShift in [-1, 0, 1]:
                if not (rowShift == 0 and colShift == 0):  # not looking at curr pos
                    newRow, newCol = row + rowShift, col + colShift
                    if self.onBoard(newRow, newCol) and self.canCaptureSquare(newRow, newCol):
                        moves.append(
                            Move((row, col), (newRow, newCol), self.board))

    def getQueenMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all queen moves at queen location and add to moves list
        '''
        pass
