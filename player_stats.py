"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the player class hierarchy.
"""

import random
from typing import Optional
import pygame
from renderer import Renderer
from block import Block
from goal import Goal

# THIS IS NOT THE RIGHT TIME, I'M DOING IT FOR SPEED
TIME_DELAY = 0


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    renderer:
        The object that draws our Blocky board on the screen
        and tracks user interactions with the Blocky board.
    id:
        This player's number.  Used by the renderer to refer to the player,
        for example as "Player 2"
    goal:
        This player's assigned goal for the game.
    """
    renderer: Renderer
    id: int
    goal: Goal

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.renderer = renderer
        self.id = player_id

    def make_move(self, board: Block) -> int:
        """Choose a move to make on the given board, and apply it, mutating
        the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.
        """
        raise NotImplementedError


class HumanPlayer(Player):
    """A human player.

    A HumanPlayer can do a limited number of smashes.

    === Public Attributes ===
    num_smashes:
        number of smashes which this HumanPlayer has performed
    === Representation Invariants ===
    num_smashes >= 0
    """
    # === Private Attributes ===
    # _selected_block
    #     The Block that the user has most recently selected for action;
    #     changes upon movement of the cursor and use of arrow keys
    #     to select desired level.
    # _level:
    #     The level of the Block that the user selected
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0

    # The total number of 'smash' moves a HumanPlayer can make during a game.
    MAX_SMASHES = 1

    num_smashes: int
    _selected_block: Optional[Block]
    _level: int

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        super().__init__(renderer, player_id, goal)
        self.num_smashes = 0

        # This HumanPlayer has done no smashes yet.
        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._selected_block = None

    def process_event(self, board: Block,
                      event: pygame.event.Event) -> Optional[int]:
        """Process the given pygame <event>.

        Identify the selected block and mark it as highlighted.  Then identify
        what it is that <event> indicates needs to happen to <board>
        and do it.

        Return
           - None if <event> was not a board-changing move (that is, if was
             a change in cursor position, or a change in _level made via
            the arrow keys),
           - 1 if <event> was a successful move, and
           - 0 if <event> was an unsuccessful move (for example in the case of
             trying to smash in an invalid location or when the player is not
             allowed further smashes).
        """
        # Get the new "selected" block from the position of the cursor
        block = board.get_selected_block(pygame.mouse.get_pos(), self._level)

        # Remove the highlighting from the old "_selected_block"
        # before highlighting the new one
        if self._selected_block is not None:
            self._selected_block.highlighted = False
        self._selected_block = block
        self._selected_block.highlighted = True

        # Since get_selected_block may have not returned the block at
        # the requested level (due to the level being too low in the tree),
        # set the _level attribute to reflect the level of the block which
        # was actually returned.
        self._level = block.level

        if event.type == pygame.MOUSEBUTTONDOWN:
            block.rotate(event.button)
            return 1
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if block.parent is not None:
                    self._level -= 1
                return None

            elif event.key == pygame.K_DOWN:
                if len(block.children) != 0:
                    self._level += 1
                return None

            elif event.key == pygame.K_h:
                block.swap(0)
                return 1

            elif event.key == pygame.K_v:
                block.swap(1)
                return 1

            elif event.key == pygame.K_s:
                if self.num_smashes >= self.MAX_SMASHES:
                    print('Can\'t smash again!')
                    return 0
                if block.smash(board.max_depth):
                    self.num_smashes += 1
                    return 1
                else:
                    print('Tried to smash at an invalid depth!')
                    return 0

    def make_move(self, board: Block) -> int:
        """Choose a move to make on the given board, and apply it, mutating
        the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.

        This method will hold focus until a valid move is performed.
        """
        self._level = 0
        self._selected_block = board

        # Remove all previous events from the queue in case the other players
        # have added events to the queue accidentally.
        pygame.event.clear()

        # Keep checking the moves performed by the player until a valid move
        # has been completed. Draw the board on every loop to draw the
        # selected block properly on screen.
        while True:
            self.renderer.draw(board, self.id)
            # loop through all of the events within the event queue
            # (all pending events from the user input)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 1

                result = self.process_event(board, event)
                self.renderer.draw(board, self.id)
                if result is not None and result > 0:
                    # un-highlight the selected block
                    self._selected_block.highlighted = False
                    return 0

class RandomPlayer(Player):
    """A random player, who makes random moves with random blocks on the board.
    RandomPlayer is not the most formidable of opponents, at least not
    on average.
    """
    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """ Initializes an instance of class RandomPlayer
        """
        Player.__init__(self, renderer, player_id, goal)

    def make_move(self, board: Block) -> int:
        """ Makes a random move for RandomPlayer
        """
        if board.children == []:
            _random_move(board)
            return 0
        else:
            block = _random_block(board)
            block.highlighted = True
            #self.renderer.draw(board, self.id)
            #pygame.time.wait(TIME_DELAY)
            _random_move(block)
            block.highlighted = False
            #self.renderer.draw(board, self.id)
            return 0

class SmartPlayer(Player):
    """ A smart player, which is slightly smarter than the RandomPlayer,
    calculating the best move from a random choice of them.

    However, a SmartPlayer cannot do smashes at all.
    """
    # === Private Attributes ===
    #     _difficulty:
    #       The difficulty of this SmartPlayer
    #
    # === Representation Invariants == =
    #      difficulty >= 0
    _difficulty: int
    def __init__(self, renderer: Renderer, player_id: int, goal: Goal,
                 diff: int) -> None:
        """ Initializes an instance of class SmartPlayer

        === Precondition ===
        _difficulty >= 0
        """
        Player.__init__(self, renderer, player_id, goal)
        self._difficulty = diff

    def make_move(self, board: Block) -> int:
        """ Makes a random move for SmartPlayer.
        """
        possible_moves_to_consider = [5, 10, 25, 50, 100, 150]
        moves_to_consider = 0
        # Determines how many moves to consider
        if self._difficulty > 5:
            moves_to_consider = possible_moves_to_consider[5]
        else:
            moves_to_consider = possible_moves_to_consider[self._difficulty]
        # A list containing the random moves to consider, represented by
        # the block they affect and their move code (0 and 1 for rotation,
        # 2 and 3 for swapping, given that the smart player cannot smash)
        moves = [[_random_block(board), random.randint(0, 3)]
                 for _ in range(moves_to_consider)]
        # Finding the right move to do in moves
        max = 0
        max_score = 0
        antimoves = [1, 0, 2, 3]

        for i in range(len(moves)):
            _move_smart(moves[i][0], moves[i][1])
            if self.goal.score(board) > max_score:
                max = i
                max_score = self.goal.score(board)
            # Undoes the prior move
            _move_smart(moves[i][0], antimoves[moves[i][1]])
        # Doing the right move in moves
        moves[max][0].highlighted = True
        #self.renderer.draw(board, self.id)
        #pygame.time.wait(TIME_DELAY)
        _move_smart(moves[max][0], moves[max][1])
        moves[max][0].highlighted = False
        #self.renderer.draw(board, self.id)
        return 0

def _random_move(block: Block) -> None:
    """ A helper function for RandomPlayer's make_move,
     which makes a random move on a given block
    """
    move = random.randint(0, 4)
    if move == 0:
        block.rotate(1)
    elif move == 1:
        block.rotate(3)
    elif move == 2:
        block.swap(0)
    elif move == 3:
        block.swap(1)
    elif move == 4:
        block.smash(block.max_depth)

def _move_smart(block: Block, move: int) -> None:
    """ A helper function for SmartPlayer's make_move, which makes a given move
    on a given block (the given move represented by an integer). 0 represents
    clockwise rotation, 1 represents counterclockwise rotation, 2 represents
    a horizontal swap, and 3 a vertical one. Smashes cannot be done by
    SmartPlayers and as such are not included here.
    """
    if move == 0:
        block.rotate(1)
    elif move == 1:
        block.rotate(3)
    elif move == 2:
        block.swap(0)
    elif move == 3:
        block.swap(1)

def _random_block(block: Block) -> Block:
    """ A helper function to all player classes which
    returns a random block in a block
    """
    if block.children == []:
        return block
    else:
        quadrant = random.randint(0, 3)
        go_deep = [True, False][random.randint(0, 1)]
        if go_deep:
            # Make the move at a lower level
            return _random_block(block.children[quadrant])
        else:
            return block.children[quadrant]

if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer',
            'pygame'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
