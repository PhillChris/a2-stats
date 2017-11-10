"""Not for assignment: collecting stats on the winners of games"""

from typing import List
import game_stats

def collect_stats (size: int, diff_1: int, diff_2: int) -> int:
    """Returns the number of wins of the first player"""
    wins = 0
    for _ in range(size):
        new_game = game_stats.Game(3, 0, 0, [diff_1, diff_2])
        winner = new_game.run_game(10)
        if winner == 0:
            wins += 1
    return wins

def list_of_wins() -> List[int]:
    return[collect_stats(1000, 0, 5), collect_stats(1000, 1, 5),
           collect_stats(1000, 2, 5), collect_stats(1000, 3, 5),
           collect_stats(1000, 4, 5), collect_stats(1000, 5, 5)]

if __name__ == '__main__':
    print(list_of_wins())
