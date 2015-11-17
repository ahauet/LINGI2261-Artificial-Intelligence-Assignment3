#!/usr/bin/env python3
"""
Avalam agent.
Copyright (C) 2015, Hauet Alexandre & Vaessen Tanguy

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.

"""

import avalam
import minimax
import time


class Agent:
    """This is the skeleton of an agent to play the Avalam game."""

    WEIGHT_TOWER_FIVE_PLAYER1 = 2
    WEIGHT_TOWER_FIVE_PLAYER2 = -3
    WEIGHT_TOWER__PLAYER1 = 1
    WEIGHT_TOWER__PLAYER2 = -2
    WEIGHT_TOWER_FOUR_PLAYER1 = 0
    WEIGHT_TOWER_FOUR_PLAYER2 = 0
    WEIGHT_CAST_AWAY_PLAYER1 = 10
    WEIGHT_CAST_AWAY_PLAYER2 = -10
    WEIGHT_DONT_DO_THAT = -100

    def __init__(self, name="Super Agent"):
        self.name = name

    def successors(self, state):
        """The successors function must return (or yield) a list of
        pairs (a, s) in which a is the action played to reach the
        state s; s is the new state, i.e. a triplet (b, p, st) where
        b is the new board after the action a has been played,
        p is the player to play the next move and
        st is the next step number.
        """
        # the received state is a tuple: 0:board, 1:player, 2:step
        board, player, step = state
        ignored_mov = []
        nbr_mov_yielded = 0
        for action in board.get_actions():
            if not board.action_cover_my_tower_with_an_other_tower(action):
                new_board = board.clone()
                new_board.play_action(action)
                next_player = player * -1
                next_step = step + 1
                new_state = (new_board, next_player, next_step)
                nbr_mov_yielded += 1
                yield (action, new_state)
            else:
                ignored_mov.append(action)
        if nbr_mov_yielded == 0:
            for action in ignored_mov:
                new_board = board.clone()
                new_board.play_action(action)
                next_player = player * -1
                next_step = step + 1
                new_state = (new_board, next_player, next_step)
                nbr_mov_yielded += 1
                yield (action, new_state)

    def cutoff(self, state, depth):
        """The cutoff function returns true if the alpha-beta/minimax
        search has to stop; false otherwise.
        """
        board, player, step = state
        # first, let's check if the game is finished before computing some things
        if board.is_finished():
            return True
        max_depth = 1  # by default

        # en moyenne on joue 32 coups / partie
        # on aimerait calculer le temps moyen d'un coup de profondeur 1
        # puis au fur et à mesure que le jeu avance, augmenter le depth_max (en escalier)
        # current_time = time.time()
        # elapsed_time = self.init_time - current_time

        #if self.time_left - elapsed_time < 10:
        #    max_depth = 1
        #else:
        #    max_depth = int(state[2] / 10 + 1.6)

        if depth >= max_depth:
            return True
        return False

    def evaluate(self, state):
        """The evaluate function must return an integer value
        representing the utility function of the board.
        """
        score = state[0].get_pimped_score(self.WEIGHT_TOWER_FIVE_PLAYER1, self.WEIGHT_TOWER_FIVE_PLAYER2,
                                          self.WEIGHT_TOWER__PLAYER1,
                                          self.WEIGHT_TOWER__PLAYER2, self.WEIGHT_TOWER_FOUR_PLAYER1,
                                          self.WEIGHT_TOWER_FOUR_PLAYER2,
                                          self.WEIGHT_CAST_AWAY_PLAYER1, self.WEIGHT_CAST_AWAY_PLAYER2,
                                          self.WEIGHT_DONT_DO_THAT
                                          )

        return score

    def play(self, board, player, step, time_left):
        """This function is used to play a move according
        to the board, player and time left provided as input.
        It must return an action representing the move the player
        will perform.
        """
        self.init_time = time.time()

        self.time_left = time_left
        newBoard = avalam.Board(board.get_percepts(player == avalam.PLAYER2))  # We are always the positive player
        state = (newBoard, player, step)
        return minimax.search(state, self)


if __name__ == "__main__":
    avalam.agent_main(Agent())
