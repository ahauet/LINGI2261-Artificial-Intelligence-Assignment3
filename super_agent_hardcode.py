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
        self.max_depth = 1 #at the beginning, we only explore one step


    def comp(self,action):
        score1 = self.comparable_score
        x1, y1, dx1, dy1 = action
        if self.comparable_board.m[x1][y1] > 0 and self.comparable_board.m[dx1][dy1] < 0:
            score1 += 3
        elif self.comparable_board.m[x1][y1] < 0 and self.comparable_board.m[dx1][dy1] < 0:
            score1 += 1
        elif self.comparable_board.m[x1][y1] > 0 and self.comparable_board.m[dx1][dy1] > 0:
            score1 += -1
        else :
            score1 == -3

        return score1

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
        list = []
        self.comparable_board = board
        self.comparable_score = board.get_score()
        for action in board.get_actions():
            if not board.action_cover_my_tower_with_an_other_tower(action):
                list.append(action)
                nbr_mov_yielded += 1
            else:
                ignored_mov.append(action)
        list.sort(key=self.comp)
        #print("noeuds = ", nbr_mov_yielded)
        if nbr_mov_yielded > 0:
            for action in list :
                new_board = board.clone()
                new_board.play_action(action)
                next_player = player * -1
                next_step = step + 1
                new_state = (new_board, next_player, next_step)
                yield((action,new_state))
        else:
             for action in ignored_mov :
                new_board = board.clone()
                new_board.play_action(action)
                next_player = player * -1
                next_step = step + 1
                new_state = (new_board, next_player, next_step)
                yield((action,new_state))




    def cutoff(self, state, depth):
        """The cutoff function returns true if the alpha-beta/minimax
        search has to stop; false otherwise.
        """
        board, player, step = state
        # first, let's check if the game is finished before computing some things
        if board.is_finished():
            return True

        self.compute_max_depth(step, self.time_left, time.time() - self.init_time, self.previous_step_time, self.total_time)

        if depth >= int(self.max_depth):
            return True
        return False

    def compute_max_depth(self, step, time_left, elapsed_time, previous_step_time, total_time):
        if time_left - elapsed_time <= 10:
            self.max_depth = 1
        else:
            if step <= 6:
                self.max_depth = 1
            elif step <= 14:
                self.max_depth = 2
            else :
                self.max_depth = 3

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
        print(int(self.max_depth))
        if step <= 2:
            self.total_time = time_left #we store the total time that we have to play
            self.previous_step_time = 1
        self.init_time = time.time() #we store the time at the beginning of our tour to use it in cutoff to know if we can continue to think or not
        self.time_left = time_left

        new_board = avalam.Board(board.get_percepts(player == avalam.PLAYER2))  # We are always the positive player
        state = (new_board, player, step)
        result = minimax.search(state, self)
        self.previous_step_time = time.time() - self.init_time
        return result

if __name__ == "__main__":
    avalam.agent_main(Agent())
