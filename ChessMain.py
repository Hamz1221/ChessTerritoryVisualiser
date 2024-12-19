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
    animate = False
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
                            animate = True
                            sqSelected = ()  # reset clicks
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]

            # key handler
            if e.type == p.KEYDOWN:
                if e.key == p.K_z and p.key.get_mods() & p.KMOD_META:  # `command + z` for undo
                    gs.undoMove()
                    moveMade = True
                    animate = False

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
            print(gs.castleRightsUpdates)
            print(gs.currentCastleRights)
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)

        drawGameState(screen, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()


def animateMove(move: ChessEngine.Move, screen: p.Surface, board: list[list[int]], clock: p.time.Clock):
    global colours
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerMove = 10

    for frame in range(framesPerMove + 1):
        row, col = (move.startRow + (dR * frame/framesPerMove),
                    move.startCol + (dC * frame/framesPerMove))

        drawBoard(screen)
        drawPieces(screen, board)

        # erase the piece moved from its ending square
        colour = colours[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE,
                           move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, colour, endSquare)

        # draw captured piece onto rectangle
        if move.pieceCaptured != Pieces.EMPTY:
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
