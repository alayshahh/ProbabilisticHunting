#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cell import Cell
from pprint import pprint
import time
import random
import copy
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

    while not found:
        # find Cell with the highest probability
        # time.sleep(2)
        old_i, old_j = prev_max
        highest_prob, max_prob_loc = 0, (0, 0)
        # print(belief_matrix)
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
        # look ahead and see if there is a better cell to search instead
        max_prob_loc = one_step_lookahead(
            belief_matrix, grid, max_prob_loc, prev_max)

        i, j = max_prob_loc

        # calculate the moves made to get to the new max prob cell i.e manhattan distance from last max to cur max cell
        dist_travelled = abs(i - old_i) + abs(j - old_j)
        # score = total distance travelled + total # of searches
        score += dist_travelled
        prev_max = max_prob_loc

        max_prob_cell = grid[i][j]
        # search the cell
        num_searches = int(
            (probability_dict[max_prob_cell.terrain_type]*10)) + 1
        # print("searching cell: ", max_prob_loc, ", ", num_searches, " times.")
        for _ in range(num_searches):

            found = max_prob_cell.search()
            score += 1

            if found:  # if the target is found we are done
                return score

            # recompute belief matrix if we havent found the target
            # belief for max_cell =  P(in max cell| not found in max cell)
            # = P(in max cell)*P(not found|in max cell)/ P(not found)
            # numerator = P(in max cell) * P(not found in max cell| in cell)  = belief[i,j]* prob of not finding (given)
        belief_given_obs_numerator = belief_matrix[i][j] * \
            ((probability_dict[max_prob_cell.terrain_type])**num_searches)
        # print("numerator: ", belief_given_obs_numerator)

        # denominator = P(not found in max cell)
        # = P(in max cell) P(not found|in max cell) + P(not in max cell)P(not found| not in max cell)
        # = belief[i,j]* given prob of not finding + [1 - belief[i,j]]*1 (no false positives)
        belief_given_obs_denominator = (belief_matrix[i][j] *
                                        probability_dict[max_prob_cell.terrain_type] +
                                        (1 - belief_matrix[i][j]))**num_searches
        # update value in matrix
        belief_matrix[i][j] = belief_given_obs_numerator / \
            belief_given_obs_denominator
        # update the rest of our beielf matrix
        update_belief_matrix(belief_matrix, (i, j),
                             belief_given_obs_denominator)
        # print(belief_matrix)

        # print(score)

    return score


def update_belief_matrix(belief_matrix, max_location, denominator):
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


def one_step_lookahead(belief_matrix, grid, max_prob_loc, prev_max):
    old_i, old_j = prev_max
    i, j = max_prob_loc
    dim = len(belief_matrix)
    cur_dist = abs(i-old_i)+abs(j-old_j)
    max_prob_cell = grid[i][j]
    # deep copy beilef matrix:
    copy_belief = copy.deepcopy(belief_matrix)
    # assume that we do not find in the cell after num_searches
    num_searches = int(
        (probability_dict[max_prob_cell.terrain_type]*10)) + 1
    # update the copied beilef matrix
    belief_given_obs_numerator = copy_belief[i][j] * \
        ((probability_dict[max_prob_cell.terrain_type])**num_searches)

    belief_given_obs_denominator = (copy_belief[i][j] *
                                    probability_dict[max_prob_cell.terrain_type] +
                                    (1 - copy_belief[i][j]))**num_searches
    copy_belief[i][j] = belief_given_obs_numerator / \
        belief_given_obs_denominator
    update_belief_matrix(copy_belief, (i, j),
                         belief_given_obs_denominator)
    # find max:
    highest_prob = 0
    highest_prob_loc = (0, 0)
    dist_to_max = dim+dim
    for k in range(dim):
        for l in range(dim):
            if copy_belief[k][l] > highest_prob:
                highest_prob = copy_belief[k][l]
                highest_prob_loc = (k, l)
                dist_to_max = abs(k-old_i) + abs(l-old_j)
            if copy_belief[k][l] == highest_prob:
                dist_to_max = abs(k-old_i) + abs(l-old_j)
                highest_prob_loc = (k, l)

    if dist_to_max < cur_dist:
        return highest_prob_loc
    else:
        return max_prob_loc
