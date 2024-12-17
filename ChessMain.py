# Handle user input, display current game state
import pygame as p
import ChessEngine
import numpy as np
import Pieces
from Pieces import *


WIDTH = HEIGHT = 512  # 512 | 400
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations
IMAGES = {}


def loadImages():
    pieces = [globals()[piece]
              for piece in Pieces.__all__ if globals()[piece] != EMPTY]

    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(
            f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))


def drawGameState(screen: p.surface, gs: ChessEngine.GameState):
    '''
    Responsible for all the graphics within a current game state
    '''
    drawBoard(screen)  # draw squares on board
    # add in piece highlighting or move suggestions [later] (code for attack visualiser goes here)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares


# Top left square is always light
def drawBoard(screen: p.Surface):
    '''
    Draw the squares on the board
    '''
    colours = [p.Color("white"), p.Color("dark grey")]

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            colour = colours[(row + col) % 2]
            p.draw.rect(screen, colour, p.Rect(
                col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen: p.Surface, board: np.ndarray):
    '''
    Draw the pieces on the board using the current GameState.board
    '''
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row, col]
            if piece != EMPTY:
                screen.blit(IMAGES[piece], p.Rect(
                    col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def main() -> None:
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    loadImages()  # do this once, before the while loop

    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                # break # ?
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == "__main__":
    main()
