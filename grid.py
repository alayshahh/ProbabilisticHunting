#!/usr/bin/env python
# -*- coding: utf-8 -*-

import enum
from random import randint
from PIL import Image
import numpy as np
import agent1
import random


class TERRAIN_TYPES(enum.Enum):
    FLAT = 0
    HILLY = 1
    FORESTED = 2
    MAZE = 3  # Complex Maze of Caves and Tunnels


# False negative dictionary
#   Maps terrain type to the corresponding false negative rate
#   We define false negative rate by the following:
#
#   P(Target not found in Cell i | Target)
PROBABILITY_DICT = {
    TERRAIN_TYPES.FLAT: 0.1,
    TERRAIN_TYPES.HILLY: 0.3,
    TERRAIN_TYPES.FORESTED: 0.7,
    TERRAIN_TYPES.MAZE: 0.9
}


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


def generate_grid(dim: int = 50):
    """
    Generate a grid of a particular dimension, and randomly assign each
    a terrain type. We assign cells based on the following probability dist
        Distribution:
            TERRAIN_TYPES.FLAT = 0.25
            TERRAIN_TYPES.HILLY = 0.25
            TERRAIN_TYPES.FORESTED = 0.25
            TERRAIN_TYPES.MAZE = 0.25
    """
    # initialize our grid to flat by default
    grid = [[None for _ in range(dim)] for _ in range(dim)]

    agent_i, agent_j = randint(0, dim - 1), randint(0, dim - 1)

    # To achieve our distrobution, we are going to use a random number
    # generator, and branch accordingly

    for i in range(dim):
        for j in range(dim):
            val = randint(0, 3)
            grid[i][j] = Cell(TERRAIN_TYPES(randint(0, 3)), i == agent_i
                              and j == agent_j)

    return grid


def create_image_from_grid(grid: list, factor: int = 1):
    """
    Given a grid that came from generate_grid(), return
    a PIL Image object that can be either saved as a file.

    factor will scale the image by a factor of len(grid)
    agent is a tuple (i,j) representing the i,j position of the agent (it will draw a dot there on the image)
    """

    # convert terrain types to color codes
    RGB_VALUES = {
        TERRAIN_TYPES.FLAT: (255, 255, 255),
        TERRAIN_TYPES.HILLY: (217, 217, 217),
        TERRAIN_TYPES.FORESTED: (106, 168, 79),
        TERRAIN_TYPES.MAZE: (67, 67, 67)
    }

    dim = len(grid)
    image_array = np.zeros((dim * factor, dim * factor, 3), dtype=np.uint8)
    for i in range(dim):
        for j in range(dim):
            r, g, b = RGB_VALUES[grid[i][j].terrain_type]

            for ki in range(factor):
                for kj in range(factor):
                    image_array[i * factor + ki, j * factor + kj,
                                0] = r  # red channel
                    image_array[i * factor + ki, j * factor + kj,
                                1] = g  # green channel
                    image_array[i * factor + ki, j * factor + kj,
                                2] = b  # blue channel

    # draw an X on the square that has the agent if the param is not none
    # The math here is gross but no real other way to do it

    # find the agent
    agent_i = agent_j = 0
    for i in range(dim):
        for j in range(dim):
            if grid[i][j].is_agent:
                agent_i, agent_j = i, j
                break

    i, j = agent_i, agent_j
    for ki in range(factor):
        for kj in range(factor):
            if abs(ki - kj) < 3:
                image_array[i * factor + ki, j * factor + kj, 0] = 255
                image_array[i * factor + ki, j * factor + kj, 1] = 0
                image_array[i * factor + ki, j * factor + kj, 2] = 0
                image_array[(i + 1) * factor - ki - 1, j * factor + kj,
                            0] = 255
                image_array[(i + 1) * factor - ki - 1, j * factor + kj, 1] = 30
                image_array[(i + 1) * factor - ki - 1, j * factor + kj, 2] = 30

    img = Image.fromarray(image_array, 'RGB')
    return img


if __name__ == '__main__':
    grid = generate_grid(50)
    dim = len(grid)
    # make belief matrix (initial belief is 1/ # of cells)
    belief_matrix = [[1 / (dim**2) for _ in range(dim)] for _ in range(dim)]

    # Agent 1
    agent_1_score = agent1.run(grid, belief_matrix, PROBABILITY_DICT)
    print("Found agent. Took " + str(agent_1_score) + " steps")
