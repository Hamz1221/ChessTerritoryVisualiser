# Handle and save game state, determine valid moves, move log, etc.
from typing import Tuple
from Pieces import *
from Pieces import ___
import Pieces

Square = Tuple[int, int]
CastlingRights = Tuple[bool, bool, bool, bool]


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq: Square, endSq: Square, board: list, enPassant: bool = False, pawnPromotion: bool = False, castleRightsChanged: bool = False, isCastle: bool = False) -> None:
        self.startRow, self.startCol = startSq
        self.endRow, self.endCol = endSq
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.boardBefore = board
        self.moveID = self.startRow * 1000 + self.startCol * \
            100 + self.endRow * 10 + self.endCol

        self.isPawnPromotion = pawnPromotion

        self.isEnPassant = enPassant

        self.castleRightsChanged = castleRightsChanged
        self.isCastle = isCastle

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
        self.moveLogSize = 0
        self.moveIdx: int = None
        self.whiteKingLoc = (7, 4)
        self.blackKingLoc = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []

        self.checkmate = False
        self.stalemate = False

        # coordinates for the square where en passant capture is possible
        self.enPassantPossible = ()

        self.currentCastleRights: CastlingRights = (True, True, True, True)
        self.castleRightsUpdates: list[CastlingRights] = [
            self.currentCastleRights]

        # self.protectionMoves = []

    # Executes move, not working for castling, en passant and promotions

    def makeMove(self, move: Move, redo: bool = False):
        self.board[move.startRow][move.startCol] = EMPTY
        self.board[move.endRow][move.endCol] = move.pieceMoved
        if self.moveIdx == None:
            self.moveIdx = -1
        #  log move for undos, see history, etc
        if self.moveIdx != self.moveLogSize - 1 and not redo:
            del self.moveLog[self.moveIdx + 1:]
            self.moveLogSize = self.moveIdx + 1
        self.moveIdx += 1
        if not redo:
            self.moveLog.append(move)
            self.moveLogSize += 1

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

        # castle rights updates
        wks, wqs, bks, bqs = self.currentCastleRights
        if move.pieceCaptured == W_R and (move.endRow, move.endCol) == (7, 7):
            wks = False
        elif move.pieceCaptured == W_R and (move.endRow, move.endCol) == (7, 0):
            wqs = False
        elif move.pieceCaptured == B_R and (move.endRow, move.endCol) == (0, 7):
            bks = False
        elif move.pieceCaptured == B_R and (move.endRow, move.endCol) == (0, 0):
            bqs = False

        if move.castleRightsChanged:
            if move.pieceMoved == W_K:
                wks, wqs = False, False
            elif move.pieceMoved == B_K:
                bks, bqs = False, False
            elif move.pieceMoved == W_R and (move.startRow, move.startCol) == (7, 7):
                wks = False
            elif move.pieceMoved == W_R and (move.startRow, move.startCol) == (7, 0):
                wqs = False
            elif move.pieceMoved == B_R and (move.startRow, move.startCol) == (0, 7):
                bks = False
            elif move.pieceMoved == B_R and (move.startRow, move.startCol) == (0, 0):
                bqs = False

        if (wks, wqs, bks, bqs) != self.currentCastleRights:
            move.castleRightsChanged = True
            self.castleRightsUpdates.append((wks, wqs, bks, bqs))
            self.currentCastleRights = self.castleRightsUpdates[-1]
        else:
            move.castleRightsChanged = False

        # castling
        if move.isCastle:
            if move.endCol - move.startCol == 2:  # castled king side
                self.board[move.endRow][move.endCol -
                                        1] = self.board[move.endRow][7]
                print(self.board[move.endRow][7])
                self.board[move.endRow][7] = EMPTY
            else:
                self.board[move.endRow][move.endCol +
                                        1] = self.board[move.endRow][0]
                self.board[move.endRow][0] = EMPTY

        self.whiteToMove = not self.whiteToMove  #  switch turn

    def undoMove(self):
        if self.moveIdx != None:
            move: Move = self.moveLog[self.moveIdx]
            self.moveIdx = self.moveIdx - 1 if self.moveIdx > 0 else None
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

            if move.castleRightsChanged:
                self.castleRightsUpdates.pop()
                self.currentCastleRights = self.castleRightsUpdates[-1]

            if move.isCastle:
                if move.endCol - move.startCol == 2:  # castled king side
                    self.board[move.endRow][7] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = EMPTY
                else:
                    self.board[move.endRow][0] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = EMPTY

    def redoMove(self):
        if self.moveLogSize > 0:
            print(f"move idx before redo: {self.moveIdx}")
            if self.moveIdx == None:
                self.makeMove(self.moveLog[0], redo=True)
            elif self.moveIdx < self.moveLogSize - 1:
                self.makeMove(self.moveLog[self.moveIdx + 1], redo=True)
            print(f"move idx after redo: {self.moveIdx}")

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

    def getEnemyTerritory(self) -> list[Move]:
        self.whiteToMove = not self.whiteToMove
        _, enemy_protectionMoves = self.getValidMoves()
        self.whiteToMove = not self.whiteToMove

        return enemy_protectionMoves

    def getValidMoves(self) -> Tuple[list[Move], list[Move]]:
        '''
        All moves considering checks
        '''
        moves = []
        protectionMoves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        kingRow, kingCol = self.whiteKingLoc if self.whiteToMove else self.blackKingLoc
        allyColour = WHITE if self.whiteToMove else BLACK
        myKing = allyColour + KING

        if self.inCheck:
            if len(self.checks) == 1:  # only 1 check, move king or block/capture
                print("only one check, move king or block/capture")
                moves, _ = self.getAllPossibleMoves()
                protectionMoves = moves
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
                self.getKingMoves(kingRow, kingCol, moves, [])
                protectionMoves = moves
        else:  #  not in check, all moves are fine
            moves, protectionMoves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True

        return (moves, protectionMoves)

    def getAllPossibleMoves(self) -> Tuple[list[Move], list[Move]]:
        '''
        All moves without considering checks
        '''
        moves: list[Move] = []
        protectionMoves: list[Move] = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == WHITE and self.whiteToMove) or (turn == BLACK and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    match piece:
                        case Pieces.PAWN:
                            self.getPawnMoves(
                                row, col, moves, protectionMoves)
                        case Pieces.ROOK:
                            self.getRookMoves(
                                row, col, moves, protectionMoves)
                        case Pieces.KNIGHT:
                            self.getKnightMoves(
                                row, col, moves, protectionMoves)
                        case Pieces.BISHOP:
                            self.getBishopMoves(
                                row, col, moves, protectionMoves)
                        case Pieces.KING:
                            self.getKingMoves(
                                row, col, moves, protectionMoves)
                        case Pieces.QUEEN:
                            self.getQueenMoves(
                                row, col, moves, protectionMoves)
                        case _:
                            raise ValueError(
                                f"Piece undefined at ({row},{col})")
        return (moves, protectionMoves)

    def canCaptureSquare(self, row, col) -> bool:
        '''
        Assumes valid square given, returns true is square empty or contains enemy piece, false otherwise
        '''
        return not ((self.board[row][col][0] == BLACK and not self.whiteToMove) or (self.board[row][col][0] == WHITE and self.whiteToMove))

    def onBoard(self, row, col) -> bool:
        return row >= 0 and row < len(self.board) and col >= 0 and col < len(self.board[row])

    def getPawnMoves(self, row: int, col: int, moves: list[Move], protectionMoves: list[Move]):
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

                protectionMoves.append(
                    Move((row, col), (row + moveAmount, col - 1), self.board, pawnPromotion=pawnPromotion))

        if col + 1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[row + moveAmount][col + 1][0] == enemyColour:
                    moves.append(
                        Move((row, col), (row + moveAmount, col + 1), self.board, pawnPromotion=pawnPromotion))
                if (row + moveAmount, col + 1) == self.enPassantPossible:
                    moves.append(
                        Move((row, col), (row + moveAmount, col + 1), self.board, enPassant=True))

                protectionMoves.append(
                    Move((row, col), (row + moveAmount, col + 1), self.board, pawnPromotion=pawnPromotion))

    def getRookMoves(self, row: int, col: int, moves: list[Move], protectionMoves: list[Move]):
        '''
        Get all rook moves at rook location and add to moves list
        '''
        piecePinned = False
        pinDirection = ()
        castleRightsChanged = False

        if self.whiteToMove:
            enemyColour = BLACK
            if (row == 7 and col == 7) or (row == 7 and col == 0):
                castleRightsChanged = True
        else:
            enemyColour = WHITE
            if (row == 0 and col == 7) or (row == 0 and col == 0):
                castleRightsChanged = True

        for pin in self.pins[::-1]:
            if pin[0] == row and pin[1] == col:
                piecePinned = True
                pinDirection = (pin[2], pin[3])
                # cant remove queen from pin on rook moves, only remove it on bishop moves
                if self.board[row][col][1] != QUEEN:
                    self.pins.remove(pin)
                break

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for rowShift, colShift in directions:
            for i in range(1, 8):
                endRow = row + rowShift * i
                endCol = col + colShift * i

                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # looking on the board
                    if not piecePinned or pinDirection == (rowShift, colShift) or pinDirection == (-rowShift, -colShift):
                        if self.board[endRow][endCol] == EMPTY:
                            moves.append(
                                Move((row, col), (endRow, endCol), self.board, castleRightsChanged=castleRightsChanged))
                            protectionMoves.append(
                                Move((row, col), (endRow, endCol), self.board, castleRightsChanged=castleRightsChanged))
                        elif self.board[endRow][endCol][0] == enemyColour:
                            moves.append(
                                Move((row, col), (endRow, endCol), self.board, castleRightsChanged=castleRightsChanged))
                            protectionMoves.append(
                                Move((row, col), (endRow, endCol), self.board, castleRightsChanged=castleRightsChanged))
                            break  # cant look beyond this piece
                        else:
                            protectionMoves.append(
                                Move((row, col), (endRow, endCol), self.board, castleRightsChanged=castleRightsChanged))
                            break  # hit ally piece, cannot attack or go further
                    else:
                        break  # cant move rook in this direction due to pin
                else:
                    break  # off the board

    def getKnightMoves(self, row: int, col: int, moves: list[Move], protectionMoves: list[Move]):
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

                            protectionMoves.append(
                                Move((row, col), (newRow, newCol), self.board))

    def getBishopMoves(self, row: int, col: int, moves: list[Move], protectionMoves: list[Move]):
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
                                protectionMoves.append(
                                    Move((row, col), (newRow, newCol), self.board))
                            elif self.canCaptureSquare(newRow, newCol):
                                moves.append(
                                    Move((row, col), (newRow, newCol), self.board))
                                protectionMoves.append(
                                    Move((row, col), (newRow, newCol), self.board))
                                break  # cannot look further
                            else:
                                protectionMoves.append(
                                    Move((row, col), (newRow, newCol), self.board))
                                break  # hit ally
                            rowShift += rowShiftInc
                            colShift += colShiftInc
                        else:
                            break  # looking off the board
                else:  # cant move in this direction
                    break

    def getKingMoves(self, row: int, col: int, moves: list[Move], protectionMoves: list[Move]):
        '''
        Get all king moves at king location and add to moves list
        '''
        # wks, wqs, bks, bqs = self.currentCastleRights

        castlingRightsChanged = True if (self.whiteToMove and (row, col) == (7, 4)) \
            or (not self.whiteToMove and (row, col) == (0, 4)) else False

        for rowShift in [-1, 0, 1]:
            for colShift in [-1, 0, 1]:
                if not (rowShift == 0 and colShift == 0):  # not looking at curr pos
                    newRow, newCol = row + rowShift, col + colShift
                    if self.onBoard(newRow, newCol):
                        if self.canCaptureSquare(newRow, newCol):
                            if self.whiteToMove:  # place King on end square and check for checks
                                self.whiteKingLoc = (newRow, newCol)
                            else:
                                self.blackKingLoc = (newRow, newCol)
                            inCheck, pins, checks = self.checkForPinsAndChecks(
                                phantom=True)
                            if not inCheck:
                                moves.append(
                                    Move((row, col), (newRow, newCol), self.board, castleRightsChanged=castlingRightsChanged))
                                protectionMoves.append(Move(
                                    (row, col), (newRow, newCol), self.board, castleRightsChanged=castlingRightsChanged))
                                print(f"King can move to ({newRow},{newCol})")
                            elif len(checks) == 1:
                                protectionMoves.append(Move(
                                    (row, col), (newRow, newCol), self.board, castleRightsChanged=castlingRightsChanged))
                            if self.whiteToMove:
                                self.whiteKingLoc = (row, col)
                            else:
                                self.blackKingLoc = (row, col)
                        else:
                            protectionMoves.append(Move(
                                (row, col), (newRow, newCol), self.board, castleRightsChanged=castlingRightsChanged))

        self.getCastlingMoves(row, col, moves)

    def getCastlingMoves(self, row: int, col: int, moves: list[Move]):
        if self.inCheck:
            return  #  cant castle out of a check!

        if self.whiteToMove:
            castleRights = self.currentCastleRights[:2]
        else:
            castleRights = self.currentCastleRights[2:]

        for idx, castleRight in enumerate(castleRights):
            if castleRight:
                dir = 1 if idx == 0 else -1
                maxDepth = 2 if idx == 0 else 3
                clearSight = True
                for i in range(1, maxDepth + 1):
                    if (self.board[row][col + dir * i] != EMPTY):
                        clearSight = False
                        break

                if clearSight:
                    canCastle = True
                    # check empty squares are not being attacked
                    if self.whiteToMove:  # white king
                        for i in range(1, 3):
                            self.whiteKingLoc = (row, col + dir * i)
                            inCheck, _, _ = self.checkForPinsAndChecks(
                                phantom=True)
                            if inCheck:
                                canCastle = False
                                break

                        if canCastle:
                            moves.append(Move((row, col), (row, col + dir * 2),
                                         self.board, castleRightsChanged=True, isCastle=True))

                        self.whiteKingLoc = (row, col)

                    else:  #  black king
                        for i in range(1, 3):
                            self.blackKingLoc = (row, col + dir * i)
                            inCheck, _, _ = self.checkForPinsAndChecks(
                                phantom=True)
                            if inCheck:
                                canCastle = False
                                break

                        if canCastle:
                            moves.append(Move((row, col), (row, col + dir * 2),
                                         self.board, castleRightsChanged=True, isCastle=True))

                        self.blackKingLoc = (row, col)

    def getQueenMoves(self, row: int, col: int, moves: list[Move], protectionMoves: list[Move]):
        '''
        Get all queen moves at queen location and add to moves list
        '''
        # rook + bishop moves
        self.getRookMoves(row, col, moves, protectionMoves)
        self.getBishopMoves(row, col, moves, protectionMoves)
