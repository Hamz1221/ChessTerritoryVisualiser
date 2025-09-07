# Handle user input, display current game state
import pygame as p
import ChessEngine
import Pieces
# from Pieces import PIECES, EMPTY, WHITE, BLACK
from ChessEngine import debug

WIDTH = HEIGHT = 640  # 640 | 512 | 400
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations
IMAGES = {}


def loadImages():
    for piece in Pieces.PIECES:
        IMAGES[piece] = p.transform.scale(p.image.load(
            f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))


def highlightSquares(screen: p.Surface, validMoves: list[ChessEngine.Move], protectionMoves: list[ChessEngine.Move], sqSelected: ChessEngine.Square):
    if sqSelected != ():
        row, col = sqSelected

        # sqSelected is a piece that can be moved
        if gs.board[row][col][0] == (Pieces.WHITE if gs.whiteToMove else Pieces.BLACK):
            #  highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color("blue"))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(
                        s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
    else:
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                sq_colour = (128, 128, 128)
                p.draw.rect(screen, sq_colour, p.Rect(
                    col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                p.draw.rect(screen, "black", p.Rect(
                    col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE), 1)
        (allyColour, enemyColour) = (
            "Blue", "Red") if gs.whiteToMove else ("Red", "Blue")
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(60)  # transparency value -> 0 transparent; 255 opaque
        s.fill(p.Color(allyColour))
        for move in protectionMoves:
            screen.blit(
                s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

        s.fill(p.Color(enemyColour))
        attackMoves = gs.getEnemyTerritory()
        for move in attackMoves:
            screen.blit(
                s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawGameState(screen: p.Surface, validMoves: list[ChessEngine.Move], protectionMoves: list[ChessEngine.Move], sqSelected: ChessEngine.Square):
    '''
    Responsible for all the graphics within a current game state
    '''
    drawBoard(screen)  # draw squares on board
    # add in piece highlighting or move suggestions [later] (code for attack visualiser goes here)
    highlightSquares(screen, validMoves, protectionMoves, sqSelected)
    drawBorder(screen)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares
    drawCoords(screen)


# Top left square is always light
def drawBoard(screen: p.Surface):
    '''
    Draw the squares on the board
    '''
    global colours
    colours = [p.Color("white"), p.Color("dark grey")]

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            colour = colours[(row + col) % 2]
            p.draw.rect(screen, colour, p.Rect(
                col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawCoords(screen: p.Surface):
    for rank in range(DIMENSION):
        txt_surface = font.render(f"{DIMENSION - rank}", True, (0, 0, 0))
        screen.blit(txt_surface, (7, (rank * SQ_SIZE) + 5))

    for i, file in enumerate("abcdefgh"):
        txt_surface = font.render(file, True, (0, 0, 0))
        screen.blit(txt_surface, ((i * SQ_SIZE) + (0.85 * SQ_SIZE),
                    (7 * SQ_SIZE) + (0.65 * SQ_SIZE)))


def drawBorder(screen):
    borderColour = "white" if gs.whiteToMove else "black"
    if gs.stalemate:
        borderColour = "yellow"
    if gs.checkmate:
        borderColour = "green"

    p.draw.rect(screen, borderColour,
                (0, 0, WIDTH, HEIGHT), 5)


def drawPieces(screen: p.Surface, board: list):
    '''
    Draw the pieces on the board using the current GameState.board
    '''
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != Pieces.EMPTY:
                screen.blit(IMAGES[piece], p.Rect(
                    col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def main(moves: list[ChessEngine.Move] = []) -> None:
    global font
    global gs
    p.init()
    font = p.font.SysFont('Comic Sans MS', 15)
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState(moves)
    validMoves, protectionMoves = gs.getValidMoves()
    moveMade = False
    undoMove = False
    canUndo = False
    gameOver = False
    UNDO_DELAY = 0.2  # seconds
    loadImages()  # do this once, before the while loop

    # most recent square player clicked on (basically playerClicks[-1])
    sqSelected = ()
    playerClicks = []  # history of player square clicks of up to 2 records

    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                # break # ?

            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # (x, y)
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        # deselect
                        sqSelected = ()
                        playerClicks = []
                    elif not (playerClicks == [] and (gs.board[row][col] == Pieces.EMPTY or gs.board[row][col][0] == (Pieces.BLACK if gs.whiteToMove else Pieces.WHITE))):
                        sqSelected = (row, col)
                        # append both first and second clicks
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:  # after 2nd click
                        move = ChessEngine.Move(
                            playerClicks[0], playerClicks[1], gs.board)
                        for validMove in validMoves:
                            if move == validMove:
                                if validMove.isPawnPromotion:
                                    print("Pawn promotion!")
                                gs.makeMove(validMove)
                                # print(validMove.getChessNotation())
                                gs.displayNotation(validMoves)
                                moveMade = True
                                undoMove = False
                                canUndo = True
                                break
                        if not moveMade and (gs.board[playerClicks[1][0]][playerClicks[1][1]][0] == (Pieces.WHITE if gs.whiteToMove else Pieces.BLACK)):
                            playerClicks = [sqSelected]
                        else:
                            sqSelected = ()  # reset clicks
                            playerClicks = []

            # key handler
            if e.type == p.KEYDOWN:
                # `shift + command + z` for redo
                if e.key == p.K_z and (p.key.get_mods() & p.KMOD_META) and (p.key.get_mods() & p.KMOD_SHIFT):
                    canUndo = False
                    idxBefore = gs.moveIdx
                    gs.redoMove()
                    idxAfter = gs.moveIdx
                    moveMade = idxBefore != idxAfter
                    undoMove = False
                    p.time.set_timer(p.USEREVENT, int(UNDO_DELAY * 1000))

                # `command + z` for undo
                elif canUndo and e.key == p.K_z and (p.key.get_mods() & p.KMOD_META):
                    canUndo = False
                    idxBefore = gs.moveIdx
                    gs.undoMove()
                    idxAfter = gs.moveIdx
                    moveMade = idxBefore != idxAfter
                    undoMove = idxBefore != idxAfter
                    p.time.set_timer(p.USEREVENT, int(UNDO_DELAY * 1000))

                # `command + r` for restart
                elif e.key == p.K_r and (p.key.get_mods() & p.KMOD_META):
                    gs = ChessEngine.GameState(moves)
                    validMoves, protectionMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    undoMove = False
                    canUndo = True
                    gameOver = False

            if e.type == p.USEREVENT:
                canUndo = True
                p.time.set_timer(p.USEREVENT, 0)

        if moveMade:
            validMoves, protectionMoves = gs.getValidMoves()
            gameOver = gs.checkmate or gs.stalemate
            moveMade = False
            debug(gs.castleRightsUpdates)
            debug(gs.currentCastleRights)
            if gs.moveLogSize > 0:
                animateMove(gs.moveLog, screen,
                            gs.board, clock, undoMove)
            debug(gs.moveIdx)
            debug(gs.moveLogSize)
            debug(len(gs.moveLog))

        drawGameState(screen, validMoves, protectionMoves, sqSelected)
        if gameOver:
            if gs.checkmate:
                if gs.whiteToMove:
                    drawText(screen, "Black wins by checkmate!", "black")
                else:
                    drawText(screen, "White wins by checkmate!", "white")
            else:
                drawText(screen, "Stalemate :/", stalemate=True)
            drawText(screen, "(shft+)cmd+z to re/undo, cmd+r to restart",
                     size=22, yoffset=60)
        clock.tick_busy_loop(MAX_FPS)
        p.display.flip()


def drawText(screen: p.Surface, text: str, colour: str = "black", stalemate: bool = False, size: int = 32, yoffset: int = 0):
    font = p.font.SysFont("Helvetica", size, True, False)
    textObject = font.render(text, 0, p.Color("black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2).move(0, yoffset)
    screen.blit(textObject, textLocation)
    # screen.blit(textObject, textLocation.move(3, 3))
    textObject = font.render(text, 0, p.Color(
        "Green" if not stalemate else "Yellow"))
    screen.blit(textObject, textLocation.move(1, 1))
    textObject = font.render(text, 0, p.Color(colour))
    screen.blit(textObject, textLocation.move(2, 2))


def animateMove(moveLog: list[ChessEngine.Move], screen: p.Surface, board: list[list[int]], clock: p.time.Clock, undoMove: bool):
    global colours
    move = moveLog[gs.moveIdx] if not undoMove else moveLog[gs.moveIdx +
                                                            1 if gs.moveIdx != None else 0]
    startRow, startCol, endRow, endCol = move.startRow, move.startCol, move.endRow, move.endCol
    if undoMove:
        startRow, startCol, endRow, endCol = move.endRow, move.endCol, move.startRow, move.startCol
    dR = endRow - startRow
    dC = endCol - startCol

    if move.isCastle:
        rook_dR = 0
        if dC == 2:  # king side castle
            rook_dC = -2 if not undoMove else -3
            rook_startCol = 7 if not undoMove else 3
            rook_endCol = 5 if not undoMove else 0
        else:
            rook_dC = 3 if not undoMove else 2
            rook_startCol = 0 if not undoMove else 5
            rook_endCol = 3 if not undoMove else 7

    framesPerMove = 10

    for frame in range(framesPerMove + 1):
        row, col = (startRow + (dR * frame/framesPerMove),
                    startCol + (dC * frame/framesPerMove))

        if move.isCastle:
            rookRow, rookCol = (endRow + (rook_dR * frame/framesPerMove),
                                rook_startCol + (rook_dC * frame/framesPerMove))

        drawBoard(screen)
        drawPieces(screen, board)

        # erase the piece moved from its ending square
        colour = colours[(endRow + endCol) % 2]
        endSquare = p.Rect(endCol*SQ_SIZE,
                           endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, colour, endSquare)

        if move.isCastle:
            colour = colours[(endRow + endCol + (0 if dC >
                              0 and undoMove else 1)) % 2]
            endSquare = p.Rect(rook_endCol*SQ_SIZE,
                               endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            p.draw.rect(screen, colour, endSquare)

        # draw captured piece onto rectangle
        if not undoMove and move.pieceCaptured != Pieces.EMPTY:
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        drawCoords(screen)
        drawBorder(screen)

        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(
            col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        if move.isCastle:
            screen.blit(IMAGES[move.pieceMoved[0]+Pieces.ROOK], p.Rect(
                rookCol*SQ_SIZE, rookRow*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    while (choice := input("Will you provide a move set? [y/n]: ")).lower() not in ["y", "n"]:
        continue
    moves: list[ChessEngine.Move] = []
    if choice == "y":
        print("Please enter the moves:")
        contents = []
        while True:
            try:
                line = input()
                if line == "":
                    break
            except EOFError:
                break
            contents.append(line)
        potentialMoves = ' '.join(contents)
        potentialMoves = potentialMoves.split(' ')
        potentialMoves = list(filter(lambda x: '.' not in x, potentialMoves))

        # Check if moves is valid gameplay by converting to list of ChessEngine.Move
        gs = ChessEngine.GameState()
        for move in potentialMoves:
            validMoves, _ = gs.getValidMoves()
            validMove = gs.convertNotationToValidMove(move, validMoves)
            gs.makeMove(validMove)
            moves.append(validMove)

    main(moves)
