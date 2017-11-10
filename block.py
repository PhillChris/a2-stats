"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Block class, the main data structure used in the game.
"""
from typing import Optional, Tuple, List, Union
import random
import math
from renderer import COLOUR_LIST, TEMPTING_TURQUOISE, BLACK


HIGHLIGHT_COLOUR = TEMPTING_TURQUOISE
FRAME_COLOUR = BLACK


class Block:
    """A square block in the Blocky game.

    === Public Attributes ===
    position:
        The (x, y) coordinates of the upper left corner of this Block.
        Note that (0, 0) is the top left corner of the window.
    size:
        The height and width of this Block.  Since all blocks are square,
        we needn't represent height and width separately.
    colour:
        If this block is not subdivided, <colour> stores its colour.
        Otherwise, <colour> is None and this block's sublocks store their
        individual colours.
    level:
        The level of this block within the overall block structure.
        The outermost block, corresponding to the root of the tree,
        is at level zero.  If a block is at level i, its children are at
        level i+1.
    max_depth:
        The deepest level allowed in the overall block structure.
    highlighted:
        True iff the user has selected this block for action.
    children:
        The blocks into which this block is subdivided.  The children are
        stored in this order: upper-right child, upper-left child,
        lower-left child, lower-right child.
    parent:
        The block that this block is directly within.

    === Representation Invariations ===
    - len(children) == 0 or len(children) == 4
    - If this Block has children,
        - their max_depth is the same as that of this Block,
        - their size is half that of this Block,
        - their level is one greater than that of this Block,
        - their position is determined by the position and size of this Block,
          as defined in the Assignment 2 handout, and
        - this Block's colour is None
    - If this Block has no children,
        - its colour is not None
    - level <= max_depth
    """

    # TODO: check about floats vs ints for size and position
    # Originally position and size were ints, but update_block_locations()
    # uses floats, so we switched to floats
    position: Tuple[float, float]
    size: float
    colour: Optional[Tuple[int, int, int]]
    level: int
    max_depth: int
    highlighted: bool
    children: List['Block']
    parent: Optional['Block']

    def __init__(self, level: int,
                 colour: Optional[Tuple[int, int, int]] = None,
                 children: Optional[List['Block']] = None) -> None:
        """Initialize this Block to be an unhighlighted root block with
        no parent.

        If <children> is None, give this block no children.  Otherwise
        give it the provided children.  Use the provided level and colour,
        and set everything else (x and y coordinates, size,
        and max_depth) to 0.  (All attributes can be updated later, as
        appropriate.)
        """
        self.position = (0, 0)
        self.size = 0
        self.colour = colour
        self.level = level
        self.max_depth = 0
        self.highlighted = False
        if children is None:
            self.children = []
        else:
            self.children = children
        self.parent = None

    def rectangles_to_draw(self) -> List[Tuple[Tuple[int, int, int],
                                               Tuple[float, float],
                                               Tuple[float, float],
                                               int]]:
        """
        Return a list of tuples describing all of the rectangles to be drawn
        in order to render this Block.

        This includes (1) for every undivided Block:
            - one rectangle in the Block's colour
            - one rectangle in the FRAME_COLOUR to frame it at the same
              dimensions, but with a specified thickness of 3
        and (2) one additional rectangle to frame this Block in the
        HIGHLIGHT_COLOUR at a thickness of 5 if this block has been
        selected for action, that is, if its highlighted attribute is True.

        The rectangles are in the format required by method Renderer.draw.
        Each tuple contains:
        - the colour of the rectangle
        - the (x, y) coordinates of the top left corner of the rectangle
        - the (height, width) of the rectangle, which for our Blocky game
          will always be the same
        - an int indicating how to render this rectangle. If 0 is specified
          the rectangle will be filled with its colour. If > 0 is specified,
          the rectangle will not be filled, but instead will be outlined in
          the FRAME_COLOUR, and the value will determine the thickness of
          the outline.

        The order of the rectangles does not matter.
        """
        rectangles = []
        if self.children == []:
            # Filled rectangle
            colour = self.colour
            position = self.position
            dimensions = (self.size, self.size)
            frame = 0
            rectangles.append((colour, position, dimensions, frame))
            # Frame rectangle
            colour = FRAME_COLOUR
            frame = 3
            rectangles.append((colour, position, dimensions, frame))

        else:
            for child in self.children:
                rectangles.extend(child.rectangles_to_draw())
        if self.highlighted:
            # Highlight rectangle
            colour = HIGHLIGHT_COLOUR
            position = self.position
            dimensions = (self.size, self.size)
            frame = 5
            rectangles.append((colour, position, dimensions, frame))
        return rectangles

    def swap(self, direction: int) -> None:
        """Swap the child Blocks of this Block.

        If <direction> is 1, swap vertically.  If <direction> is 0, swap
        horizontally. If this Block has no children, do nothing.
        """
        if self.children == []:
            return

        elif direction == 0:  # Swap horizontally
            self.children = [self.children[1], self.children[0],
                             self.children[3], self.children[2]]

            self.update_block_locations(self.position, self.size)

        else:  # Swap vertically
            self.children = [self.children[3], self.children[2],
                             self.children[1], self.children[0]]

            self.update_block_locations(self.position, self.size)

    def rotate(self, direction: int) -> None:
        """Rotate this Block and all its descendants.

        If <direction> is 1, rotate clockwise.  If <direction> is 3, rotate
        counterclockwise. If this Block has no children, do nothing.
        """
        if self.children == []:
            return

        elif direction == 1:  # Rotate clockwise
            self.children = [self.children[1], self.children[2],
                             self.children[3], self.children[0]]

            for child in self.children:
                child.rotate(direction)

            self.update_block_locations(self.position, self.size)

        else:  # Rotate counter-clockwise
            self.children = [self.children[3], self.children[0],
                             self.children[1], self.children[2]]

            for child in self.children:
                child.rotate(direction)

            self.update_block_locations(self.position, self.size)

    def smash(self, max_depth: int) -> bool:
        """Smash this block.

        If this Block can be smashed,
        randomly generating four new child Blocks for it.  (If it already
        had child Blocks, discard them.)
        Ensure that the RI's of the Blocks remain satisfied.

        A Block can be smashed iff it is not the top-level Block and it
        is not already at the level of the maximum depth.

        Return True if this Block was smashed and False otherwise.
        """
        if self.level == max_depth or self.level == 0:
            return False

        else:
            self.children = [random_init(self.level+1, max_depth)
                             for _ in range(4)]

            for child in self.children:
                child.parent = self

            self.update_block_locations(self.position, self.size)

            return True

    def update_block_locations(self, top_left: Tuple[float, float],
                               size: float) -> None:
        """
        Update the position and size of each of the Blocks within this Block.

        Ensure that each is consistent with the position and size of its
        parent Block.

        <top_left> is the (x, y) coordinates of the top left corner of
        this Block.  <size> is the height and width of this Block.
        """
        # TODO: check about floats vs ints for size and position
        self.position = top_left
        self.size = size
        if self.children != []:
            x = top_left[0]
            y = top_left[1]
            child_size = size / 2
            # Upper Right
            self.children[0].update_block_locations((x + child_size, y),
                                                    child_size)
            # Upper Left
            self.children[1].update_block_locations((x, y),
                                                    child_size)
            # Lower Left
            self.children[2].update_block_locations((x, y + child_size),
                                                    child_size)
            # Lower Right
            self.children[3].update_block_locations((x + child_size,
                                                     y + child_size),
                                                    child_size)

    def get_colour_at_square(self, x: int, y: int) -> Tuple[int, int, int]:
        """ Pass the coordinates (in unit blocks) whose colour you
        want to find, and return the color at that space.
        === Preconditions ===
        The coordinates are valid (0-indexed)
        """
        halfway = 2**(self.max_depth - self.level - 1)

        if self.children == []:
            return self.colour

        elif _is_upper_right(x, y, halfway):
            return self.children[0].get_colour_at_square(x - halfway, y)

        elif _is_upper_left(x, y, halfway):
            return self.children[1].get_colour_at_square(x, y)

        elif _is_lower_left(x, y, halfway):
            return self.children[2].get_colour_at_square(x, y - halfway)

        elif _is_lower_right(x, y, halfway):
            return self.children[3].get_colour_at_square(x - halfway,
                                                         y - halfway)

    def get_selected_block(self, location: Tuple[float, float], level: int) \
            -> 'Block':
        """Return the Block within this Block that includes the given location
        and is at the given level. If the level specified is lower than
        the lowest block at the specified location, then return the block
        at the location with the closest level value.

        <location> is the (x, y) coordinates of the location on the window
        whose corresponding block is to be returned.
        <level> is the level of the desired Block.  Note that
        if a Block includes the location (x, y), and that Block is subdivided,
        then one of its four children will contain the location (x, y) also;
        this is why <level> is needed.

        Preconditions:
        - 0 <= level <= max_depth
        """
        if self.children == []:
            return self
        elif self.level == level:
            return self
        x, y = location
        halfway = self.size / 2

        if _is_upper_right(x, y, halfway):
            return self.children[0].get_selected_block((x - halfway, y), level)

        elif _is_upper_left(x, y, halfway):
            return self.children[1].get_selected_block((x, y), level)

        elif _is_lower_left(x, y, halfway):
            return self.children[2].get_selected_block((x, y - halfway), level)

        elif _is_lower_right(x, y, halfway):
            return self.children[3].get_selected_block((x - halfway,
                                                        y - halfway), level)

    def flatten(self) -> List[List[Tuple[int, int, int]]]:
        """Return a two-dimensional list representing this Block as rows
        and columns of unit cells.

        Return a list of lists L, where, for 0 <= i, j < 2^{self.level}
            - L[i] represents column i and
            - L[i][j] represents the unit cell at column i and row j.
        Each unit cell is represented by 3 ints for the colour
        of the block at the cell location[i][j]

        L[0][0] represents the unit cell in the upper left corner of the Block.
        """
        width = 2**(self.max_depth - self.level)
        flattened = [[self.get_colour_at_square(x, y) for y in range(width)]
                     for x in range(width)]
        return flattened


def random_init(level: int, max_depth: int) -> 'Block':
    """Return a randomly-generated Block with level <level> and subdivided
    to a maximum depth of <max_depth>.

    Throughout the generated Block, set appropriate values for all attributes
    except position and size.  They can be set by the client, using method
    update_block_locations.

    Precondition:
        level <= max_depth
    """
    # If this Block is not already at the maximum allowed depth, it can
    # be subdivided. Use a random number to decide whether or not to
    # subdivide it further.
    colour = None
    children = None
    if level < max_depth and random.random() < math.exp(-0.25 * level):
        children = [random_init(level + 1, max_depth) for _ in range(4)]
        block = Block(level, colour, children)
        block.max_depth = max_depth
        for child in block.children:
            child.parent = block
    else:
        colour = COLOUR_LIST[random.randint(0, 3)]
        block = Block(level, colour, children)
        block.max_depth = max_depth
    return block


def _is_upper_right(x: Union[int, float], y: Union[int, float],
                    halfway: Union[int, float]) -> bool:
    """A helper method that returns whether or not a given
    coordinate is in the upper right of a block"""
    return y < halfway <= x


def _is_upper_left(x: Union[int, float], y: Union[int, float],
                   halfway: Union[int, float]) -> bool:
    """A helper method that returns whether or not a given
    coordinate is in the upper left of the block"""
    return x < halfway and y < halfway


def _is_lower_left(x: Union[int, float], y: Union[int, float],
                   halfway: Union[int, float]) -> bool:
    """A helper method that returns whether or not a given
    coordinate is in the lower left of the block"""
    return x < halfway <= y


def _is_lower_right(x: Union[int, float], y: Union[int, float],
                    halfway: Union[int, float]) -> bool:
    """A helper method that returns whether or not a given
     coordinate is in the lower right of the block"""
    return x >= halfway and y >= halfway


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer', 'math'
        ],
        'max-attributes': 15
    })
