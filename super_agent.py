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

class Agent:
    """This is the skeleton of an agent to play the Avalam game."""

    WEIGHT_TOWER_FIVE_PLAYER1 = 100
    WEIGHT_TOWER_FIVE_PLAYER2 = 4
    WEIGHT_TOWER__PLAYER1 = 2
    WEIGHT_TOWER__PLAYER2 = 4
    WEIGHT_TOWER_FOUR_PLAYER1 = 4
    WEIGHT_TOWER_FOUR_PLAYER2 = 2
    WEIGHT_CAST_AWAY_PLAYER1 = 10
    WEIGHT_CAST_AWAY_PLAYER2 = 20


    def __init__(self, name="Agent"):
        self.name = name

    def successors(self, state):
        """The successors function must return (or yield) a list of
        pairs (a, s) in which a is the action played to reach the
        state s; s is the new state, i.e. a triplet (b, p, st) where
        b is the new board after the action a has been played,
        p is the player to play the next move and
        st is the next step number.
        """
        #the received state is a tuple: 0:board, 1:player, 2:step
        board, player, step = state
        ignored_mov = []
        nbr_mov_yielded = 0
        for action in board.get_actions():
            if(not board.action_cover_my_tower_with_an_other_tower(action)):
                newBoard = board.clone()
                newBoard.play_action(action)
                nextPlayer = player * -1
                nextStep = step + 1
                newState = (newBoard, nextPlayer, nextStep)
                nbr_mov_yielded += 1
                yield (action, newState)
            else:
                ignored_mov.append(action)
        if nbr_mov_yielded == 0:
            for action in ignored_mov:
                newBoard = board.clone()
                newBoard.play_action(action)
                nextPlayer = player * -1
                nextStep = step + 1
                newState = (newBoard, nextPlayer, nextStep)
                nbr_mov_yielded += 1
                yield (action, newState)

    def cutoff(self, state, depth):
        """The cutoff function returns true if the alpha-beta/minimax
        search has to stop; false otherwise.
        """
        if(state[0].is_finished()):
            return True
        if(depth >= 2):
            return True
        return False

    def evaluate(self, state):
        """The evaluate function must return an integer value
        representing the utility function of the board.
        """
        score = state[0].get_score()
        score += state[0].get_number_max_tower(self.WEIGHT_TOWER_FIVE_PLAYER1, self.WEIGHT_TOWER_FIVE_PLAYER2)
        score += state[0].get_number_tower(self.WEIGHT_TOWER__PLAYER1, self.WEIGHT_TOWER__PLAYER2)
        score += state[0].get_number_tower_level_4(self.WEIGHT_TOWER_FOUR_PLAYER1,self.WEIGHT_TOWER_FOUR_PLAYER2)
        score += state[0].cast_away(self.WEIGHT_CAST_AWAY_PLAYER1, self.WEIGHT_CAST_AWAY_PLAYER2)
        return score

    def play(self, board, player, step, time_left):
        """This function is used to play a move according
        to the board, player and time left provided as input.
        It must return an action representing the move the player
        will perform.
        """
        self.time_left = time_left
        newBoard = avalam.Board(board.get_percepts(player==avalam.PLAYER2)) #We are always the positive player
        state = (newBoard, player, step)
        return minimax.search(state, self)


if __name__ == "__main__":
    avalam.agent_main(Agent())
