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
        # find Cell with the lowest cost
        old_i, old_j = prev_max
        lowest_cost, max_prob_loc = 4*dim, (0, 0)
        for i in range(dim):
            for j in range(dim):
                if i == old_i and j == old_j:
                    continue
                # find cell w lowest cost
                # compute cost as dist to cell + (1- prob of finding in cell) * (cost of next move)
                # distacne to cell
                dist = abs(i-old_i)+abs(j-old_j)
                # number of searches at cell
                cur_cell = grid[i][j]
              # multiplies P(target in cell)*P(finding Target|target in cell) -> P(finding Targetin cell |obaservations)
                cur_prob = belief_matrix[i][j] * \
                    (1-probability_dict[cur_cell.terrain_type])
                cost = dist + cur_cell.num_visits + \
                    (1-cur_prob)*one_step_lookahead(belief_matrix, grid, (i, j))
                # print("cell :", (i, j), "cost: ", cost)
                if cost < lowest_cost:
                    lowest_cost = cost
                    max_prob_loc = i, j

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
        if max_prob_cell.already_searched:
            num_searches = int(num_searches/2)

        print("searching cell: ", max_prob_loc, ", ", num_searches, " times.")
        max_prob_cell.increment_visits()
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


def one_step_lookahead(belief_matrix, grid, max_prob_loc):
    '''
    Assumes that we will not find anything in the current cell and checks which cell will be the next searched
    It will then return the distance of that cell from the max
    '''
    i, j = max_prob_loc
    dim = len(belief_matrix)
    max_prob_cell = grid[i][j]
    # deep copy beilef matrix:
    copy_belief = copy.deepcopy(belief_matrix)
    # assume that we do not find in the cell after num_searches
    num_searches = int(
        (probability_dict[max_prob_cell.terrain_type]*10)) + 1

    # if a cell has already been searched many times we dont want to search it as many times(not sure if we want to keep this yet)
    if max_prob_cell.already_searched:
        num_searches = int(num_searches/2)

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
    dist_to_max = dim+dim
    max_loc = (0, 0)
    for k in range(dim):
        for l in range(dim):
            if copy_belief[k][l] > highest_prob:
                max_loc = (k, l)
                highest_prob = copy_belief[k][l]
                dist_to_max = abs(k-i) + abs(l-j)
            if copy_belief[k][l] == highest_prob:
                if dist_to_max > abs(k-i) + abs(l-j):
                    max_loc = (k, l)
                    dist_to_max = abs(k-i) + abs(l-j)

    # print("Max loc: ", max_loc)
    return dist_to_max
