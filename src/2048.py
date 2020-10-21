#!/usr/bin/env python3

import os
import random
import sys


###############################################################################
# Configuration

# Number of rows and columns of the grid
N = 5

# Basic grid elements
ZERO = 0
ONE = 1

# User interaction
QUIT = 'Q'
LEFT, DOWN, UP, RIGHT = 'H', 'J', 'K', 'L'
VALID_DIRECTIONS = [LEFT, DOWN, UP, RIGHT]
GREETINGS = '''
    *********************************************************
    *                                                       *
    *   Welcome to 2048.                                    *
    *                                                       *
    *   Equal numbers are summed when pressed together.     *
    *                                                       *
    *   The sums may get as high as you like,               *
    *   as long as the board can be moved.                  *
    *                                                       *
    *   Press [%s %s %s %s] to move [LEFT DOWN UP RIGHT].       *
    *   (These are the Vim navigation keys.)                *
    *                                                       *
    *   Press %s to QUIT.                                    *
    *                                                       *
    *   Enjoy!                                              *
    *                                                       *
    *********************************************************
''' % (LEFT, DOWN, UP, RIGHT, QUIT)


###############################################################################
# I/O 

def getch():
    '''
    Read a single character from standard input. Do not echo to the screen.
    Courtesy: https://code.activestate.com/recipes/134892-getch-like-unbuffered-character-reading-from-stdin
    '''
    try:
        # POSIX
        import termios
    except ImportError:
        # Non-POSIX
        import msvcrt
        return msvcrt.getch()
    # POSIX
    import sys, tty
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


###############################################################################
# Core (grid primitives)

def bubble_zeros(row):
    '''
    Return a new list the same length as the input row where the ZEROs of the
    input row are all on the right hand side, and the non-ZEROs on the left
    hand side keep their order.
    '''
    nonzeros = [x for x in row if x != ZERO]
    zeros = [ZERO for _ in range(len(row) - len(nonzeros))]
    return nonzeros + zeros

def double(x):
    return 2 * x

def sum_twins(row):
    '''
    If any two neighbors row[i], row[i + 1] are equal, then double the amount of
    row[i], set row[i + 1] to ZERO, and leave the rest of the row as is.
    Continue with the rest of the row. When finished, return the modified row.
    '''
    for i in range(len(row) - 1):
        if row[i] == row[i + 1]:
            row[i] = double(row[i])
            row[i + 1] = ZERO
            i += 1
    return row

def compress(row):
    return bubble_zeros(sum_twins(bubble_zeros(row)))

def reverse(row):
    return row[::-1]

def transpose(grid):
    '''
    NOTE: zip() produces tuples, but we need lists for random update.
    '''
    return [list(row) for row in zip(*grid)]

def move(grid, direction):
    '''
    Return the grid after it has been compressed in the given direction.
    '''
    return {
        LEFT: lambda grid: [compress(row) for row in grid],
        RIGHT: lambda grid: [reverse(compress(reverse(row))) for row in grid],
        UP: lambda grid: transpose(move(transpose(grid), LEFT)),
        DOWN: lambda grid: transpose(move(transpose(grid), RIGHT))
    }[direction](grid)


###############################################################################
# Shell (game flow)

class Game(object):

    def __init__(self):
        '''
        Make an N by N list of lists of ZEROs with a single random ONE.
        '''
        self.grid = self.enter_random_one(
            [[ZERO for _ in range(N)] for _ in range(N)])

    def enter_random_one(self, grid):
        i, j = random.choice([
            (i, j) for i in range(N) for j in range(N) 
            if grid[i][j] == ZERO])
        grid[i][j] = ONE
        return grid

    def clear(self):
        os.system('clear')

    def greet(self):
        print(GREETINGS)

    def display(self):
        print('')
        for row in self.grid:
            print('%5d'*N % tuple(row))
        print('')

    def get_move(self):
        return getch().upper()

    def update(self, direction):
        '''
        NOTE: The grid is unchanged exactly if the chosen direction has no
        equal neighbors or no unbubbled ZEROs.
        '''
        updated_grid = move(self.grid, direction)
        if updated_grid != self.grid:
            self.grid = self.enter_random_one(updated_grid)

    def play(self):
        self.clear()
        self.greet()
        self.display()
        while True:
            move = self.get_move()
            if move == QUIT:
                self.clear()
                break
            elif move in VALID_DIRECTIONS:
                self.update(move)
                self.clear()
                self.display()


###############################################################################
# Main

if __name__ == '__main__':
    Game().play()
