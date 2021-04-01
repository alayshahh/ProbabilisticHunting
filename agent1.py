#!/usr/bin/env python
# -*- coding: utf-8 -*-


def run(grid, belief_matrix, probability_dict):
    score = 0
    found = False

    dim = len(grid)

    while True:
        # find Cell with the highest probability

        highest_prob, max_prob_loc = 0, (0, 0)
        for i in range(dim):
            for j in range(dim):
                if belief_matrix[i][j] > highest_prob:
                    highest_prob = belief_matrix[i][j]
                    max_prob_loc = i, j

        i, j = max_prob_loc
        score += 1

        found = grid[i][j].search()
        if found:
            break

        # recompute belief matrix
        belief_given_obs_numerator = belief_matrix[i][j] * \
            (1 - probability_dict[grid[i][j].terrain_type])
        belief_given_obs_denominator = belief_matrix[i][j] * \
            probability_dict[grid[i][j].terrain_type] + (1-belief_matrix[i][j])

        belief_matrix[i][j] = belief_given_obs_numerator / \
            belief_given_obs_denominator

        update_belief_matrix(grid, belief_matrix, (i, j),
                             belief_given_obs_denominator, probability_dict)

        print(score)

    return score


def update_belief_matrix(grid, belief_matrix, max_location, denominator, probability_dict):
    dim = len(belief_matrix)
    for i in range(dim):
        for j in range(dim):
            if (i, j) != max_location:
                numerator = belief_matrix[i][j] * \
                    probability_dict[grid[i][j].terrain_type]

                belief_matrix[i][j] = numerator / denominator
