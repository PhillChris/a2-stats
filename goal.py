"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Goal class hierarchy.
"""

from typing import List, Tuple
from block import Block
from renderer import colour_name


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class BlobGoal(Goal):
    """A goal to create the largest connected blob of this goal's target
    colour, anywhere within the Block.
    """

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
           -1  if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        # If the index is out of bounds
        if (pos[0] < 0 or pos[0] >= len(board)) or (pos[1] < 0 or
                                                    pos[1] >= len(board[0])):
            return 0

        # If we've already visited
        elif visited[pos[0]][pos[1]] == 0 or visited[pos[0]][pos[1]] == 1:
            return 0  # To avoid doublecounting

        # If the blob is of the wrong colour, and we haven't visited
        elif board[pos[0]][pos[1]] != self.colour:
            visited[pos[0]][pos[1]] = 0
            return 0

        #If the blob is of the right colour, and we haven't visited
        else:
            current = 1 # The starting blob own is an unvisited blob
            visited[pos[0]][pos[1]] = 1

            # Add the undiscovered blob sizes of each of the adjacent blocks

            current += self._undiscovered_blob_size((pos[0], pos[1] + 1),
                                                    board,
                                                    visited)
            current += self._undiscovered_blob_size((pos[0], pos[1] - 1),
                                                    board,
                                                    visited)
            current += self._undiscovered_blob_size((pos[0] + 1, pos[1]),
                                                    board,
                                                    visited)
            current += self._undiscovered_blob_size((pos[0] - 1, pos[1]),
                                                    board,
                                                    visited)
            return current

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        max_blob = 0
        flattened = board.flatten()
        visited = [[-1 for _ in range(2**board.max_depth)] \
                   for _ in range(2**board.max_depth)]
        for x in range(len(visited)):
            for y in range(len(visited[0])):
                if visited[x][y] == -1:
                    temp = self._undiscovered_blob_size((x, y), flattened,
                                                        visited)
                    max_blob = max(max_blob, temp)
        return max_blob

    def description(self) -> str:
        """Return a description of this goal.
        """
        colour = colour_name(self.colour)
        return "Create the largest blob of " + colour + " possible."


class PerimeterGoal(Goal):
    """A goal to maximize the amount of the perimeter in the given colour.
    """

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        flattened = board.flatten()
        count = 0
        for x in range(len(flattened)):
            if flattened[x][0] == self.colour:
                count += 1
            if flattened[x][-1] == self.colour:
                count += 1
        for y in range(len(flattened)):
            if flattened[0][y] == self.colour:
                count += 1
            if flattened[-1][y] == self.colour:
                count += 1
        return count

    def description(self) -> str:
        """Return a description of this goal.
        """
        colour = colour_name(self.colour)
        return "Maximize the amount of " + colour + " on the perimeter."


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer'
        ],
        'max-attributes': 15
    })
