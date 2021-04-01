from constants import PROBABILITY_DICT
import random


class Cell:
    def __init__(self, terrain_type, is_agent):
        self._terrain_type = terrain_type
        self._is_agent = is_agent

    @property
    def terrain_type(self):
        return self._terrain_type

    # USED ONLY FOR RENDERING!!
    @property
    def is_agent(self):
        return self._is_agent

    def search(self):
        if not self._is_agent:
            return False
        else:
            return PROBABILITY_DICT[self._terrain_type] <= random.random()
