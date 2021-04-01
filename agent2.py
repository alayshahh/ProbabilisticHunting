#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cell import Cell
from pprint import pprint
import time
import random
from constants import PROBABILITY_DICT as probability_dict


def run(grid, belief_matrix):
    '''
    Moves through the grid and looks at cells with the highest probability of finding the target to search. 
    '''

    score = 0
    found = False
    dim = len(grid)

    # we will start at random start point since all probs are equal
    prev_max = (random.randint(0, dim), random.randint(0, dim))

    while True:
        # find Cell with the highest probability
        old_i, old_j = prev_max
        highest_prob, max_prob_loc = 0, (0, 0)
        for i in range(dim):
            for j in range(dim):
                # find cell w highes prob
                cur_cell = grid[i][j]
                # multiplies P(target in cell)*P(finding Target|target in cell) -> P(finding Targetin cell |obaservations)
                cur_prob = belief_matrix[i][j] * \
                    (1-probability_dict[cur_cell.terrain_type])
                if cur_prob > highest_prob:
                    highest_prob = cur_prob
                    max_prob_loc = i, j
                    dist_to_max = abs(i-old_i) + abs(j-old_j)
                # pick the cell w highest prob and closest to current location
                if cur_prob == highest_prob:
                    dist = abs(i-old_i) + abs(j-old_j)
                    if dist < dist_to_max:
                        max_prob_loc = i, j
                        dist_to_max = dist

        i, j = max_prob_loc
        # calculate the moves made to get to the new max prob cell i.e manhattan distance from last max to cur max cell
        dist_travelled = abs(i - old_i) + abs(j - old_j)
        # score = total distance travelled + total # of searches
        score += (1+dist_travelled)
        prev_max = max_prob_loc

        max_prob_cell = grid[i][j]
        # search the cell
        found = max_prob_cell.search()

        if found:  # if the target is found we are done
            break

        # recompute belief matrix if we havent found the target
        # belief for max_cell =  P(in max cell| not found in max cell)
        # = P(in max cell)*P(not found|in max cell)/ P(not found)
        # numerator = P(in max cell) * P(not found in max cell| in cell)  = belief[i,j]* prob of not finding (given)
        belief_given_obs_numerator = belief_matrix[i][j] * \
            probability_dict[max_prob_cell.terrain_type]

        # denominator = P(not found in max cell)
        # = P(in max cell) P(not found|in max cell) + P(not in max cell)P(not found| not in max cell)
        # = belief[i,j]* given prob of not finding + [1 - belief[i,j]]*1 (no false positives)
        belief_given_obs_denominator = belief_matrix[i][j] * \
            probability_dict[max_prob_cell.terrain_type] + \
            (1 - belief_matrix[i][j])
        # update value in matrix
        belief_matrix[i][j] = belief_given_obs_numerator / \
            belief_given_obs_denominator
        # update the rest of our beielf matrix
        update_belief_matrix(grid, belief_matrix, (i, j),
                             belief_given_obs_denominator, probability_dict)

        # print(score)

    return score


def update_belief_matrix(grid, belief_matrix, max_location, denominator, probability_dict):
    ''' 
    Update rest of beief belief_matrix
    '''
    # P(in cur cell| not found in max cell) = P(in cur cell && not found in max cell)/ P (not found in max cell)
    # we have already computed the denominator from before, so we do not need to redo it
    # numerator:  P(in cur cell && not found in max cell) = P(in cur cell)P(not found in max cell| in cur cell) = P(in cur cell)*1 (no false positives)
    # = beief[cur_i, cur_j]/ denominator
    dim = len(belief_matrix)
    for i in range(dim):
        for j in range(dim):
            if (i, j) != max_location:  # do not update the max cell
                numerator = belief_matrix[i][j]
                belief_matrix[i][j] = numerator / denominator
