import copy
import sys
import pygame
from constants import *
import numpy as np
import random

#pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Krizic-kruzic')
screen.fill(BG_COLOUR)

class Board:
    def __init__(self):
        self.squares = np.zeros((ROWS, COLS))
        self.empty_squares = self.squares
        self.marked_squares = 0

    def final_state(self, show=False):
        #vertical wins
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    ipos = (col * SQUARE_SIZE + SQUARE_SIZE // 2, 20)
                    fpos = (col * SQUARE_SIZE + SQUARE_SIZE // 2, HEIGHT - OFFSET)
                    pygame.draw.line(screen, END_COLOR, ipos, fpos, LINE_WIDTH)
                return self.squares[0][col]
            
        #horizontal wins
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    ipos = (20, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                    fpos = (WIDTH - 20, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                    pygame.draw.line(screen, END_COLOR, ipos, fpos, LINE_WIDTH)
                return self.squares[row][0]
            
        #desc diagonal
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                ipos = (20, 20)
                fpos = (WIDTH - 20, HEIGHT - 20)
                pygame.draw.line(screen, END_COLOR, ipos, fpos, LINE_WIDTH)
            return self.squares[1][1]
        
        #asc diagonal
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                ipos = (20, HEIGHT - 20)
                fpos = (WIDTH - 20, 20)
                pygame.draw.line(screen, END_COLOR, ipos, fpos, LINE_WIDTH)
            return self.squares[1][1]
        
        #no win yet
        return 0
    
    def mark_square(self, row, col, player):
        self.squares[row][col] = player
        self.marked_squares +=1

    def empty_square(self, row, col):
        return self.squares[row][col] == 0
    
    def get_empty_squares(self):
        empty_squares = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_square(row, col):
                    empty_squares.append((row, col))

        return empty_squares
    
    def isfull(self):
        return self.marked_squares == 9
    
    def isempty(self):
        return self.marked_squares == 0
    
class AI:
    def __init__(self, level=1, player=2):
        self.level = level
        self.player = player
        
    def random(self, board):
        empty_squares = board.get_empty_squares()
        index = random.randrange(0, len(empty_squares))
        return empty_squares[index]

    def minimax(self, board, maximizing):
        case = board.final_state()

        # player 1 wins
        if case == 1:
            return 1, None # eval, move
        #player 2 wins
        if case == 2:
            return -1, None
        #draw
        elif board.isfull():
            return 0, None
        
        if maximizing:
            max_eval = -100
            best_move = None
            empty_squares = board.get_empty_squares()

            for (row, col) in empty_squares:
                temp_board = copy.deepcopy(board)
                temp_board.mark_square(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

            return max_eval, best_move
        
        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_squares = board.get_empty_squares()

            for (row, col) in empty_squares:
                temp_board = copy.deepcopy(board)
                temp_board.mark_square(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)

            return min_eval, best_move

    def eval(self, main_board):
        if self.level == 0:
            eval = 'random'
            move = self.random(main_board)
        else:
            # minimax
            eval, move = self.minimax(main_board, False)

        print(f'AI has chosen to mark the position {move} with an evaluation of: {eval}')
        return move


class Game:
    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.player = 1 # 1 = X, 2 = O
        self.gamemode = 'ai'
        self.running = True
        self.show_lines()

    def make_move(self, row, col):
        self.board.mark_square(row, col, self.player)
        self.draw_fig(row, col)
        self.change_player()

    def show_lines(self):
        screen.fill(BG_COLOUR)
        #vertical
        pygame.draw.line(screen, LINE_COLOUR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOUR, (WIDTH - SQUARE_SIZE, 0), (WIDTH - SQUARE_SIZE, HEIGHT), LINE_WIDTH)

        #horizontal
        pygame.draw.line(screen, LINE_COLOUR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOUR, (0, HEIGHT - SQUARE_SIZE), (WIDTH, HEIGHT - SQUARE_SIZE), LINE_WIDTH)

    def draw_fig(self, row, col):
        if self.player == 1:
            # desc line
            start_desc = (col * SQUARE_SIZE + OFFSET, row * SQUARE_SIZE + OFFSET)
            end_desc = (col * SQUARE_SIZE + SQUARE_SIZE - OFFSET, row * SQUARE_SIZE + SQUARE_SIZE - OFFSET)
            pygame.draw.line(screen, FIG_COLOUR, start_desc, end_desc, CROSS_WIDTH)
            # asc line
            start_asc = (col * SQUARE_SIZE + OFFSET, row * SQUARE_SIZE + SQUARE_SIZE - OFFSET)
            end_asc = (col * SQUARE_SIZE + SQUARE_SIZE - OFFSET, row * SQUARE_SIZE + OFFSET)
            pygame.draw.line(screen, FIG_COLOUR, start_asc, end_asc, CROSS_WIDTH)
        elif self.player == 2:
            center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
            pygame.draw.circle(screen, FIG_COLOUR, center, RADIUS, CIRC_WIDTH)

    def change_player(self):
        self.player = self.player % 2 + 1

    def change_gamemode(self):
        if self.gamemode == 'pvp':
            self.gamemode = 'ai'
        else:
            self.gamemode = 'pvp'

    def isover(self):
        return self.board.final_state(show=True) != 0 or self.board.isfull()

    def reset(self):
        self.__init__()

def main():
    #game object
    game = Game()
    board = game.board
    ai = game.ai

    #main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # g - gamemode
                if event.key == pygame.K_g:
                    game.change_gamemode()

                # restart
                if event.key == pygame.K_r:
                    game.reset()
                    board = game.board
                    ai = game.ai

                # 0 - random ai
                if event.key == pygame.K_0:
                    ai.level = 0

                # 1 - minimax ai
                if event.key == pygame.K_1:
                    ai.level = 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                row = pos[1] // SQUARE_SIZE
                col = pos[0] // SQUARE_SIZE
                
                if board.empty_square(row, col) and game.running:
                    game.make_move(row, col)

                    if game.isover():
                        game.running = False

        if game.gamemode == 'ai' and game.player == ai.player and game.running:
            pygame.display.update()
            row, col = ai.eval(board)

            game.make_move(row, col)

            if game.isover():
                game.running = False

        pygame.display.update()

main()