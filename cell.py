from constants import PROBABILITY_DICT
import random


class Cell:
    def __init__(self, terrain_type, is_agent):
        self._terrain_type = terrain_type
        self._is_agent = is_agent
        self.searched = False
        self.num_visits = 0

    @property
    def terrain_type(self):
        return self._terrain_type

    # USED ONLY FOR RENDERING!!
    @property
    def is_agent(self):
        return self._is_agent

    @property
    def already_searched(self) -> bool:
        return self.searched

    @property
    def visits(self) -> int:
        return self.num_visits

    def increment_visits(self):
        self.num_visits += 1

    def search(self):
        self.searched = True
        if not self._is_agent:
            return False
        else:
            return PROBABILITY_DICT[self._terrain_type] <= random.random()
