# Handle user input, display current game state
import pygame as p
import ChessEngine
import Pieces
# from Pieces import PIECES, EMPTY, WHITE, BLACK


WIDTH = HEIGHT = 512  # 512 | 400
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations
IMAGES = {}


def loadImages():
    for piece in Pieces.PIECES:
        IMAGES[piece] = p.transform.scale(p.image.load(
            f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))


def highlightSquares(screen: p.Surface, validMoves: list[ChessEngine.Move], sqSelected: ChessEngine.Square):
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


def drawGameState(screen: p.Surface, validMoves: list[ChessEngine.Move], sqSelected: ChessEngine.Square):
    '''
    Responsible for all the graphics within a current game state
    '''
    drawBoard(screen)  # draw squares on board
    drawCoords(screen)
    drawBorder(screen)
    # add in piece highlighting or move suggestions [later] (code for attack visualiser goes here)
    highlightSquares(screen, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares


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


def drawCoords(screen):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            txt_surface = font.render(f"({row},{col})", False, (0, 0, 0))
            screen.blit(txt_surface, (col * SQ_SIZE, row * SQ_SIZE))


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


def main() -> None:
    global font
    global gs
    p.init()
    font = p.font.SysFont('Comic Sans MS', 10)
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    undoMove = False
    canUndo = True
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
                location = p.mouse.get_pos()  # (x, y)
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col):
                    # deselect
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    # append both first and second clicks
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:  # after 2nd click
                    move = ChessEngine.Move(
                        playerClicks[0], playerClicks[1], gs.board)
                    for validMove in validMoves:
                        if move == validMove:
                            print(validMove.getChessNotation())
                            gs.makeMove(validMove)
                            moveMade = True
                            undoMove = False
                            sqSelected = ()  # reset clicks
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]

            # key handler
            if e.type == p.KEYDOWN:
                if e.key == p.K_z and (p.key.get_mods() & p.KMOD_META) and (p.key.get_mods() & p.KMOD_SHIFT):
                    # `shift + command + z` for redo
                    idxBefore = gs.moveIdx
                    gs.redoMove()
                    idxAfter = gs.moveIdx
                    moveMade = idxBefore != idxAfter
                    undoMove = False
                # `command + z` for undo
                elif canUndo and e.key == p.K_z and (p.key.get_mods() & p.KMOD_META):
                    canUndo = False
                    idxBefore = gs.moveIdx
                    gs.undoMove()
                    idxAfter = gs.moveIdx
                    moveMade = idxBefore != idxAfter
                    undoMove = idxBefore != idxAfter
                    p.time.set_timer(p.USEREVENT, int(UNDO_DELAY * 1000))

            if e.type == p.USEREVENT:
                canUndo = True
                p.time.set_timer(p.USEREVENT, 0)

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
            print(gs.castleRightsUpdates)
            print(gs.currentCastleRights)
            if gs.moveLogSize > 0:
                animateMove(gs.moveLog, screen,
                            gs.board, clock, undoMove)
            print(gs.moveIdx)
            print(gs.moveLogSize)
            print(len(gs.moveLog))

        drawGameState(screen, validMoves, sqSelected)
        clock.tick_busy_loop(MAX_FPS)
        p.display.flip()


def animateMove(moveLog: list[ChessEngine.Move], screen: p.Surface, board: list[list[int]], clock: p.time.Clock, undoMove: bool):
    global colours
    move = moveLog[gs.moveIdx] if not undoMove else moveLog[gs.moveIdx +
                                                            1 if gs.moveIdx != None else 0]
    startRow, startCol, endRow, endCol = move.startRow, move.startCol, move.endRow, move.endCol
    if undoMove:
        startRow, startCol, endRow, endCol = move.endRow, move.endCol, move.startRow, move.startCol
    dR = endRow - startRow
    dC = endCol - startCol
    framesPerMove = 10

    for frame in range(framesPerMove + 1):
        row, col = (startRow + (dR * frame/framesPerMove),
                    startCol + (dC * frame/framesPerMove))

        drawBoard(screen)
        drawPieces(screen, board)

        # erase the piece moved from its ending square
        colour = colours[(endRow + endCol) % 2]
        endSquare = p.Rect(endCol*SQ_SIZE,
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
        p.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
