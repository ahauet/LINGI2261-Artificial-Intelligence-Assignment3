# -*- coding: utf-8 -*-
"""
Common definitions for the Avalam players.
Copyright (C) 2010 - Vianney le Clément, UCLouvain

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
from random import shuffle

PLAYER1 = 1
PLAYER2 = -1

class InvalidAction(Exception):

    """Raised when an invalid action is played."""

    def __init__(self, action=None):
        self.action = action


class Board:

    """Representation of an Avalam Board.

    self.m is a self.rows by self.columns bi-dimensional array representing the
    board.  The absolute value of a cell is the height of the tower.  The sign
    is the color of the top-most counter (negative for red, positive for
    yellow).

    """

    # standard avalam
    max_height = 5
    initial_board = [ [ 0,  0,  1, -1,  0,  0,  0,  0,  0],
                      [ 0,  1, -1,  1, -1,  0,  0,  0,  0],
                      [ 0, -1,  1, -1,  1, -1,  1,  0,  0],
                      [ 0,  1, -1,  1, -1,  1, -1,  1, -1],
                      [ 1, -1,  1, -1,  0, -1,  1, -1,  1],
                      [-1,  1, -1,  1, -1,  1, -1,  1,  0],
                      [ 0,  0,  1, -1,  1, -1,  1, -1,  0],
                      [ 0,  0,  0,  0, -1,  1, -1,  1,  0],
                      [ 0,  0,  0,  0,  0, -1,  1,  0,  0] ]

    def __init__(self, percepts=initial_board, max_height=max_height,
                       invert=False):
        """Initialize the board.

        Arguments:
        percepts -- matrix representing the board
        invert -- whether to invert the sign of all values, inverting the
            players
        max_height -- maximum height of a tower

        """
        self.m = percepts
        self.rows = len(self.m)
        self.columns = len(self.m[0])
        self.max_height = max_height
        self.m = self.get_percepts(invert)  # make a copy of the percepts

    def __str__(self):
        def str_cell(i, j):
            x = self.m[i][j]
            if x:
                return "%+2d" % x
            else:
                return " ."
        return "\n".join(" ".join(str_cell(i, j) for j in range(self.columns))
                         for i in range(self.rows))

    def clone(self):
        """Return a clone of this object."""
        return Board(self.m)

    def get_percepts(self, invert=False):
        """Return the percepts corresponding to the current state.

        If invert is True, the sign of all values is inverted to get the view
        of the other player.

        """
        mul = 1
        if invert:
            mul = -1
        return [[mul * self.m[i][j] for j in range(self.columns)]
                for i in range(self.rows)]

    def get_towers(self):
        """Yield all towers.

        Yield the towers as triplets (i, j, h):
        i -- row number of the tower
        j -- column number of the tower
        h -- height of the tower (absolute value) and owner (sign)

        """
        for i in range(self.rows):
            for j in range(self.columns):
                if self.m[i][j]:
                    yield (i, j, self.m[i][j])

    def is_action_valid(self, action):
        """Return whether action is a valid action."""
        try:
            i1, j1, i2, j2 = action
            if i1 < 0 or j1 < 0 or i2 < 0 or j2 < 0 or \
               i1 >= self.rows or j1 >= self.columns or \
               i2 >= self.rows or j2 >= self.columns or \
               (i1 == i2 and j1 == j2) or (abs(i1-i2) > 1) or (abs(j1-j2) > 1):
                return False
            h1 = abs(self.m[i1][j1])
            h2 = abs(self.m[i2][j2])
            if h1 <= 0 or h1 >= self.max_height or h2 <= 0 or \
                    h2 >= self.max_height or h1+h2 > self.max_height:
                return False
            return True
        except (TypeError, ValueError):
            return False

    def get_tower_actions(self, i, j):
        """Yield all actions with moving tower (i,j)"""
        h = abs(self.m[i][j])
        if h > 0 and h < self.max_height:
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    action = (i, j, i+di, j+dj)
                    if self.is_action_valid(action):
                        yield action

    def is_tower_movable(self, i, j):
        """Return wether tower (i,j) is movable"""
        for action in self.get_tower_actions(i, j):
            return True
        return False

    def get_actions(self):
        """Yield all valid actions on this board."""
        towers = []
        for i, j, h in self.get_towers():
            towers.append((i,j,h))
        shuffle(towers)
        for i,j,h in towers:
            for action in self.get_tower_actions(i, j):
                yield action

    def play_action(self, action):
        """Play an action if it is valid.

        An action is a 4-uple containing the row and column of the tower to
        move and the row and column of the tower to gobble. If the action is
        invalid, raise an InvalidAction exception. Return self.

        """
        if not self.is_action_valid(action):
            raise InvalidAction(action)
        i1, j1, i2, j2 = action
        h1 = abs(self.m[i1][j1])
        h2 = abs(self.m[i2][j2])
        if self.m[i1][j1] < 0:
            self.m[i2][j2] = -(h1 + h2)
        else:
            self.m[i2][j2] = h1 + h2
        self.m[i1][j1] = 0
        return self

    def is_finished(self):
        """Return whether no more moves can be made (i.e., game finished)."""
        for action in self.get_actions():
            return False
        return True

    def get_score(self):
        """Return a score for this board.

        The score is the difference between the number of towers of each
        player. In case of ties, it is the difference between the maximal
        height towers of each player. If self.is_finished() returns True,
        this score represents the winner (<0: red, >0: yellow, 0: draw).

        """
        score = 0
        for i in range(self.rows):
            for j in range(self.columns):
                if self.m[i][j] < 0:
                    score -= 1
                elif self.m[i][j] > 0:
                    score += 1
        if score == 0:
            for i in range(self.rows):
                for j in range(self.columns):
                    if self.m[i][j] == -self.max_height:
                        score -= 1
                    elif self.m[i][j] == self.max_height:
                        score += 1
        return score

    def get_number_tower(self, i, j, weight_player1, weight_player2):
        """
            Return the difference between the number of towers of each
            player.
        """
        score = 0
        if self.m[i][j] < 0:
            score += weight_player2
        elif self.m[i][j] > 0:
            score += weight_player1
        return score

    def get_number_max_tower(self, i, j, weight_player1, weight_player2):
        result = 0
        if self.m[i][j] == 5:
            result += weight_player1
        elif self.m[i][j] == -5:
            result += weight_player2
        return result

    def get_number_tower_level_4(self,weight_player1, weight_player2):
        score = 0
        for i in range(self.rows):
            for j in range(self.columns):
                if self.m[i][j] == 4:
                    score += weight_player1
                elif self.m[i][j] == -4:
                    score += weight_player2
        return score


    def get_score_not_great_tower_level_4(self, i, j, weight):
        score = 0
        if abs(self.m[i][j]) == 4:
            if (self.is_tower_movable(i,j)):
                score +=weight
        return score

    def have_a_tower_with_neighbor_that_complet_it(self,i, j, actions, weight):
        score = 0
        if self.m[i][j] > 0:
            for action in actions:
                (x, y, dx, dy) = action
                if 5-abs(self.get_tower_at_the_origin_of_action(action)) == abs(self.get_tower_targeted_by_action(action)):
                    score += weight
        return score

    def get_pimped_score(self, WEIGHT_TOWER_FIVE_PLAYER1, WEIGHT_TOWER_FIVE_PLAYER2, WEIGHT_TOWER__PLAYER1, WEIGHT_TOWER__PLAYER2, WEIGHT_TOWER_FOUR_PLAYER1, WEIGHT_TOWER_FOUR_PLAYER2,
                         WEIGHT_CAST_AWAY_PLAYER1, WEIGHT_CAST_AWAY_PLAYER2, WEIGHT_DONT_DO_THAT):
        score = 0
        for i in range(self.rows):
            for j in range(self.columns):
                score += self.get_number_max_tower(i, j, WEIGHT_TOWER_FIVE_PLAYER1, WEIGHT_TOWER_FIVE_PLAYER2)
                score += self.get_number_tower(i, j, WEIGHT_TOWER__PLAYER1,WEIGHT_TOWER__PLAYER2)
                score += self.cast_away(i, j, WEIGHT_CAST_AWAY_PLAYER1, WEIGHT_CAST_AWAY_PLAYER2)
                score += self.get_score_not_great_tower_level_4(i, j, WEIGHT_DONT_DO_THAT)
                actions = list(self.get_tower_actions(i, j))
                if len(actions) == 1:
                    score += self.near_a_bad_cast_away(i, j, actions[0], WEIGHT_DONT_DO_THAT)
                score += self.have_a_tower_with_neighbor_that_complet_it(i, j, actions, WEIGHT_DONT_DO_THAT)
        return score


    def cast_away(self, i, j, weight_player1, weight_player2):
        score = 0
        height = self.m[i][j]
        if height > 0:
            if not self.is_tower_movable(i,j):
                score += (6-height) * weight_player1
        elif height < 0:
            if not self.is_tower_movable(i,j):
                score += (6-abs(height)) * weight_player2
        return score

    def near_a_bad_cast_away(self, i, j, action, weight):
        score = 0
        if self.m[i][j] > 0:
            (x,y,dx,dy) = action
            if self.m[x][y] < 0:
                score+= weight
        return score





    def get_tower_at_the_origin_of_action(self, action):
        """
        Get a tower at pos (i,j) of the action
        :return: a tower: positive if belong to current player, negative else
        """
        if not self.is_action_valid(action):
            raise InvalidAction(action)
        i1, j1, i2, j2 = action
        return self.m[i1][j1]

    def get_tower_targeted_by_action(self, action):
        """
        Return the tower targeted by the action
        :param action:
        :return:
        """
        if not self.is_action_valid(action):
            raise InvalidAction(action)
        i1, j1, i2, j2 = action
        return self.m[i2][j2]

    def get_tower_height(self, action):
        """
        Return the height of the tower targeted by the action
        :param action:
        :return:
        """
        if not self.is_action_valid(action):
            raise InvalidAction(action)
        i1, j1, i2, j2 = action
        return abs(self.m[i2][j2])

    def get_color_neighborhood(self):
        return -1


    def action_cover_my_tower_with_an_opponent_tower(self, action):
        """
        Return true if the action cover one of my tower with a tower of the opponent
        :param action:
        :return:
        """
        origin = self.get_tower_at_the_origin_of_action(action)
        target = self.get_tower_targeted_by_action(action)
        return target > 0 and origin < 0

    def action_cover_my_tower_with_an_other_tower(self, action):
        """
        Return true if the action cover one of my tower with another tower
        :param action:
        :return:
        """
        target = self.get_tower_targeted_by_action(action)
        return target > 0

    def abs(n):
        return (n, -n)[n < 0]



def load_percepts(filename):
    """Load percepts from a CSV file."""
    f = None
    try:
        f = open(filename, "r")
        import csv
        percepts = []
        for row in csv.reader(f):
            if not row:
                continue
            row = [int(c.strip()) for c in row]
            if percepts:
                assert len(row) == len(percepts[0]), \
                       "rows must have the same length"
            percepts.append(row)
        return percepts
    finally:
        if f is not None:
            f.close()


class Agent:
  """Interface for a Zombies agent"""

  def initialize(self, percepts, players, time_left):
    """Begin a new game.

    The computation done here also counts in the time credit.

    Arguments:
    percepts -- the initial board in a form that can be fed to the Board
        constructor.
    players -- sequence of players this agent controls
    time_left -- a float giving the number of seconds left from the time
        credit for this agent (all players taken together). If the game is
        not time-limited, time_left is None.

    """
    pass

  def play(self, percepts, player, step, time_left):
    """Play and return an action.

    Arguments:
    percepts -- the current board in a form that can be fed to the Board
        constructor.
    player -- the player to control in this step
    step -- the current step number, starting from 1
    time_left -- a float giving the number of seconds left from the time
        credit. If the game is not time-limited, time_left is None.

    """
    pass

  def agent_main(agent, args_cb=None, setup_cb=None):
    """Launch agent server depending on arguments.

    Arguments:
    agent -- an Agent instance
    args_cb -- function taking two arguments: the agent and an
        ArgumentParser. It can add custom options to the parser.
        (None to disable)
    setup_cb -- function taking three arguments: the agent, the
        ArgumentParser and the options dictionary. It can be used to
        configure the agent based on the custom options. (None to
        disable)
  
    """
    pass
