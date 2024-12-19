# Handle and save game state, determine valid moves, move log, etc.
from typing import Tuple
from Pieces import *
from Pieces import ___
import Pieces

Square = Tuple[int, int]


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq: Square, endSq: Square, board: list, enPassant: bool = False, pawnPromotion: bool = False) -> None:
        self.startRow, self.startCol = startSq
        self.endRow, self.endCol = endSq
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.boardBefore = board
        self.moveID = self.startRow * 1000 + self.startCol * \
            100 + self.endRow * 10 + self.endCol

        self.isPawnPromotion = pawnPromotion

        self.isEnPassant = enPassant

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
        self.whiteKingLoc = (7, 4)
        self.blackKingLoc = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []

        self.checkmate = False
        self.stalemate = False

        # coordinates for the square where en passant capture is possible
        self.enPassantPossible = ()

    # Executes move, not working for castling, en passant and promotions
    def makeMove(self, move: Move):
        self.board[move.startRow][move.startCol] = EMPTY
        self.board[move.endRow][move.endCol] = move.pieceMoved
        #  log move for undos, see history, etc
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove  #  switch turn

        # track kings
        if move.pieceMoved == W_K:
            self.whiteKingLoc = (move.endRow, move.endCol)
        elif move.pieceMoved == B_K:
            self.blackKingLoc = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + QUEEN

        # en passant
        if move.isEnPassant:
            self.board[move.startRow][move.endCol] = EMPTY

        # update en passant field
        # only on 2 square pawn advances
        if move.pieceMoved[1] == PAWN and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = (
                (move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enPassantPossible = ()

    def undoMove(self):
        if len(self.moveLog) > 0:
            move: Move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  #  switch turn back

            # track kings
            if move.pieceMoved == W_K:
                self.whiteKingLoc = (move.startRow, move.startCol)
            elif move.pieceMoved == B_K:
                self.blackKingLoc = (move.startRow, move.startCol)

            self.checkmate = False
            self.stalemate = False

            if move.isEnPassant:
                self.board[move.startRow][move.endCol] = B_P if move.pieceMoved[0] == WHITE else W_P
                self.enPassantPossible = (move.endRow, move.endCol)

            if move.pieceMoved[1] == PAWN and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()

    def checkForPinsAndChecks(self, phantom: bool = False):
        pins = []  # squares where the allied pinned piece is and direction pinned from
        checks = []  #  squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColour = BLACK
            allyColour = WHITE
            startRow, startCol = self.whiteKingLoc
        else:
            enemyColour = WHITE
            allyColour = BLACK
            startRow, startCol = self.blackKingLoc

        # check outward from king for pins and checks, keep track of pins
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dir_idx, dir in enumerate(directions):
            possiblePin = ()  # reset possible pins
            for dist in range(1, 8):
                endRow = startRow + dir[0] * dist
                endCol = startCol + dir[1] * dist

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]

                    if endPiece[0] == allyColour and endPiece[1] != KING:
                        if possiblePin == ():  #  1st allied piece could be pinned
                            possiblePin = (endRow, endCol, dir[0], dir[1])
                            if not phantom:
                                print(
                                    f"Possible pin by {endPiece} on ({endRow},{endCol})")
                        else:  # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColour:
                        type = endPiece[1]
                        # 5 possibilities here in this complex conditional
                        # 1.) Orthogonally away from king and piece is a rook
                        # 2.) Diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally and piece is a pawn
                        # 4.) Any direction and piece is a Queen
                        # 5.) Any direction 1 square away and piece is a King (prevents king move to enemy king territory)
                        if (0 <= dir_idx <= 3 and type == ROOK) or \
                            (4 <= dir_idx <= 7 and type == BISHOP) or \
                                (dist == 1 and type == PAWN and ((enemyColour == WHITE and 6 <= dir_idx <= 7) or (enemyColour == BLACK and 4 <= dir_idx <= 5))) or \
                                (type == QUEEN) or (dist == 1 and type == KING):
                            if possiblePin == ():  #  no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, dir[0], dir[1]))
                                if not phantom:
                                    print(
                                        f"Checked by {endPiece} on ({endRow},{endCol})")
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                if not phantom:
                                    print(
                                        f"{self.board[possiblePin[0]][possiblePin[1]]} on ({possiblePin[0]},{possiblePin[1]}) pinned by {endPiece} on ({endRow},{endCol})")
                                break
                        else:  # enemy piece not applying check
                            break
                else:  # looking off board
                    break

        # check for knights
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        for move in knightMoves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                enemyKnight = enemyColour + KNIGHT

                if endPiece == enemyKnight:  # enemy knight attacking our King
                    inCheck = True
                    checks.append((endRow, endCol, move[0], move[1]))
                    if not phantom:
                        print(f"Checked by {endPiece} on ({endRow},{endCol})")

        return inCheck, pins, checks

    def getValidMoves(self) -> list[Move]:
        '''
        All moves considering checks
        '''
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        kingRow, kingCol = self.whiteKingLoc if self.whiteToMove else self.blackKingLoc
        allyColour = WHITE if self.whiteToMove else BLACK
        myKing = allyColour + KING

        if self.inCheck:
            if len(self.checks) == 1:  # only 1 check, move king or block/capture
                print("only one check, move king or block/capture")
                moves = self.getAllPossibleMoves()
                # to block a check you must move a piece into one of the squares between the enemy piece and king
                checkRow, checkCol, checkDirV, checkDirH = self.checks[0]
                # enemy piece causing check
                pieceChecking = self.board[checkRow][checkCol]
                validSqs = []  # squares pieces can move to
                # if knight, must capture or move king, other pieces can be blocked
                if pieceChecking[1] == KNIGHT:
                    validSqs = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSq = (kingRow + checkDirV * i,
                                   kingCol + checkDirH * i)
                        validSqs.append(validSq)
                        # reached checking enemy piece
                        if validSq[0] == checkRow and validSq[1] == checkCol:
                            break

                # get rid of any moves that don't block check or move king
                for move in moves[::-1]:
                    if move.pieceMoved != myKing:  # move doesn't move king so it must block or capture
                        #  move does not block or capture checking enemy piece
                        if not (move.endRow, move.endCol) in validSqs:
                            moves.remove(move)
            else:  # double check, king has to move
                print("Double check!")
                self.getKingMoves(kingRow, kingCol, moves)
        else:  #  not in check, all moves are fine
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True

        return moves  # for now we will not worry about checks

    def getAllPossibleMoves(self) -> list[Move]:
        '''
        All moves without considering checks
        '''
        moves: list[Move] = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == WHITE and self.whiteToMove) or (turn == BLACK and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    match piece:
                        case Pieces.PAWN:
                            self.getPawnMoves(row, col, moves)
                        case Pieces.ROOK:
                            self.getRookMoves(row, col, moves)
                        case Pieces.KNIGHT:
                            self.getKnightMoves(row, col, moves)
                        case Pieces.BISHOP:
                            self.getBishopMoves(row, col, moves)
                        case Pieces.KING:
                            self.getKingMoves(row, col, moves)
                        case Pieces.QUEEN:
                            self.getQueenMoves(row, col, moves)
                        case _:
                            raise ValueError(
                                f"Piece undefined at ({row},{col})")
        return moves

    def canCaptureSquare(self, row, col) -> bool:
        '''
        Assumes valid square given, returns true is square empty or contains enemy piece, false otherwise
        '''
        return not ((self.board[row][col][0] == BLACK and not self.whiteToMove) or (self.board[row][col][0] == WHITE and self.whiteToMove))

    def onBoard(self, row, col) -> bool:
        return row >= 0 and row < len(self.board) and col >= 0 and col < len(self.board[row])

    def getPawnMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all pawn moves at pawn location and add to moves list
        '''
        piecePinned = False
        pinDirection = ()

        for pin in self.pins[::-1]:
            if pin[0] == row and pin[1] == col:
                piecePinned = True
                pinDirection = (pin[2], pin[3])
                self.pins.remove(pin)
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColour = BLACK
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColour = WHITE

        # pawn got to back rank and needs promotion
        pawnPromotion = (row + moveAmount == backRow)

        # Pawn advance
        if self.board[row + moveAmount][col] == EMPTY:
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(
                    Move((row, col), (row + moveAmount, col), self.board, pawnPromotion=pawnPromotion))
                if row == startRow and self.board[row + 2 * moveAmount][col] == EMPTY:
                    moves.append(
                        Move((row, col), (row + 2 * moveAmount, col), self.board))

        # Pawn captures
        if col - 1 >= 0:
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[row + moveAmount][col - 1][0] == enemyColour:
                    moves.append(
                        Move((row, col), (row + moveAmount, col - 1), self.board, pawnPromotion=pawnPromotion))
                if (row + moveAmount, col - 1) == self.enPassantPossible:
                    moves.append(
                        Move((row, col), (row + moveAmount, col - 1), self.board, enPassant=True))

        if col + 1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[row + moveAmount][col + 1][0] == enemyColour:
                    moves.append(
                        Move((row, col), (row + moveAmount, col + 1), self.board, pawnPromotion=pawnPromotion))
                if (row + moveAmount, col + 1) == self.enPassantPossible:
                    moves.append(
                        Move((row, col), (row + moveAmount, col + 1), self.board, enPassant=True))

    def getRookMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all rook moves at rook location and add to moves list
        '''
        piecePinned = False
        pinDirection = ()

        for pin in self.pins[::-1]:
            if pin[0] == row and pin[1] == col:
                piecePinned = True
                pinDirection = (pin[2], pin[3])
                # cant remove queen from pin on rook moves, only remove it on bishop moves
                if self.board[row][col][1] != QUEEN:
                    self.pins.remove(pin)
                break

        #  Check above and below rook
        for rowShiftInc in [-1, 1]:
            rowShift = rowShiftInc
            while True:
                newRow = row + rowShift
                if newRow < len(self.board) and newRow >= 0:  # row is on the board
                    if not piecePinned or pinDirection == (rowShiftInc, 0) or pinDirection == (-rowShiftInc, 0):
                        if self.board[newRow][col] == EMPTY:
                            moves.append(
                                Move((row, col), (newRow, col), self.board))
                        elif (self.board[newRow][col][0] == BLACK and self.whiteToMove) or (self.board[newRow][col][0] == WHITE and not self.whiteToMove):
                            moves.append(
                                Move((row, col), (newRow, col), self.board))
                            break  # cannot look further
                        else:
                            break  # hit wall or ally piece
                    else:
                        break  # piece cant move in this direction at all
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
                    if not piecePinned or pinDirection == (0, colShiftInc) or pinDirection == (0, -colShiftInc):
                        if self.board[row][newCol] == EMPTY:
                            moves.append(
                                Move((row, col), (row, newCol), self.board))
                        elif (self.board[row][newCol][0] == BLACK and self.whiteToMove) or (self.board[row][newCol][0] == WHITE and not self.whiteToMove):
                            moves.append(
                                Move((row, col), (row, newCol), self.board))
                            break  # cannot look further
                        else:
                            break  # hit wall or ally piece
                    else:  #  cant move
                        break
                    colShift += colShiftInc
                else:
                    break  # looking off the board

    def getKnightMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all knight moves at knight location and add to moves list
        '''
        for pin in self.pins[::-1]:
            if pin[0] == row and pin[1] == col:  # Knight is pinned, cannot move the knight at all
                self.pins.remove(pin)
                return

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
        piecePinned = False
        pinDirection = ()

        for pin in self.pins[::-1]:
            if pin[0] == row and pin[1] == col:
                piecePinned = True
                pinDirection = (pin[2], pin[3])
                self.pins.remove(pin)
                break

        for rowShiftInc in [-1, 1]:
            for colShiftInc in [-1, 1]:
                if not piecePinned or pinDirection == (rowShiftInc, colShiftInc) or pinDirection == (-rowShiftInc, -colShiftInc):
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
                else:  # cant move in this direction
                    break

    def getKingMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all king moves at king location and add to moves list
        '''

        for rowShift in [-1, 0, 1]:
            for colShift in [-1, 0, 1]:
                if not (rowShift == 0 and colShift == 0):  # not looking at curr pos
                    newRow, newCol = row + rowShift, col + colShift
                    if self.onBoard(newRow, newCol) and self.canCaptureSquare(newRow, newCol):
                        if self.whiteToMove:  # place King on end square and check for checks
                            self.whiteKingLoc = (newRow, newCol)
                        else:
                            self.blackKingLoc = (newRow, newCol)
                        inCheck, pins, checks = self.checkForPinsAndChecks(
                            phantom=True)
                        if not inCheck:
                            moves.append(
                                Move((row, col), (newRow, newCol), self.board))
                            print(f"King can move to ({newRow},{newCol})")
                        if self.whiteToMove:
                            self.whiteKingLoc = (row, col)
                        else:
                            self.blackKingLoc = (row, col)

    def getQueenMoves(self, row: int, col: int, moves: list[Move]):
        '''
        Get all queen moves at queen location and add to moves list
        '''
        # rook + bishop moves
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)
