# Handle user input, display current game state
import pygame as p
import ChessEngine
import Pieces
from Pieces import PIECES, EMPTY


WIDTH = HEIGHT = 512  # 512 | 400
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations
IMAGES = {}


def loadImages():
    for piece in PIECES:
        IMAGES[piece] = p.transform.scale(p.image.load(
            f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))


def drawGameState(screen: p.surface, gs: ChessEngine.GameState, font: p.font.Font):
    '''
    Responsible for all the graphics within a current game state
    '''
    drawBoard(screen, gs.whiteToMove, gs.checkmate,
              gs.stalemate, font)  # draw squares on board
    # add in piece highlighting or move suggestions [later] (code for attack visualiser goes here)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares


# Top left square is always light
def drawBoard(screen: p.Surface, whiteToMove: bool, checkmate: bool, stalemate: bool, font: p.font.Font):
    '''
    Draw the squares on the board
    '''
    colours = [p.Color("white"), p.Color("dark grey")]
    borderColour = "white" if whiteToMove else "black"
    if stalemate:
        borderColour = "yellow"
    if checkmate:
        borderColour = "green"

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            colour = colours[(row + col) % 2]
            p.draw.rect(screen, colour, p.Rect(
                col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            txt_surface = font.render(f"({row},{col})", False, (0, 0, 0))
            screen.blit(txt_surface, (col * SQ_SIZE, row * SQ_SIZE))

    p.draw.rect(screen, borderColour,
                (0, 0, WIDTH, HEIGHT), 5)


def drawPieces(screen: p.Surface, board: list):
    '''
    Draw the pieces on the board using the current GameState.board
    '''
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != EMPTY:
                screen.blit(IMAGES[piece], p.Rect(
                    col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def main() -> None:
    p.init()
    font = p.font.SysFont('Comic Sans MS', 10)
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
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
                            sqSelected = ()  # reset clicks
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]

            # key handler
            if e.type == p.KEYDOWN:
                if e.key == p.K_z and p.key.get_mods() & p.KMOD_META:  # `command + z` for undo
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, font)
        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == "__main__":
    main()
