import enum


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


# convert terrain types to color codes
RGB_VALUES = {
    TERRAIN_TYPES.FLAT: (255, 255, 255),
    TERRAIN_TYPES.HILLY: (217, 217, 217),
    TERRAIN_TYPES.FORESTED: (106, 168, 79),
    TERRAIN_TYPES.MAZE: (67, 67, 67)
}
