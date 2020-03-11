import os, subprocess, time, signal
import copy
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding
import open_mtg

class MtgEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.players = [player.Player(gold_deck), player.Player(silver_deck)]
        self.env = game.Game(self.players)
        self.env.start_game()
    
    @property
    def action_space(self, player):
        if player == self.env.player_with_priority.index:
            legal_moves = self.env.get_legal_moves(self.env.player_with_priority)
            return spaces.Discrete(len(legal_moves))
        else:
            return spaces.Discrete(1)

    @property
    def observation_space(self, player):
        player_object = self.env.players[player]
        player_decklist = copy.deepcopy(player_object.deck)
        player_decklist.sort()

        return spaces.Dict({
            "life", len(player_object.life),
            "hand": len(player_object.hand),
            "graveyard": len(player_object.graveyard),
            "deck": len(players_decklist),
            "battlefield": len(self.env.battlefield),
            "attackers": len(self.env.attackers),
            "blockers": len(self.env.blockers),
            "empty_stack": 1,
            "damage_targets": len(self.env.damage_targets),
            "active_player": 1,
            "nonactive_player": 1,
            "priority": 1,
            "current_phase": 1
        })

    def _step(self, action, player):
        """

        Parameters
        ----------
        action : index of action to take
        player : index of player to make move

        Returns
        -------
        ob, reward, episode_over, info : tuple
            ob (object) :
                an environment-specific object representing your observation of
                the environment.
            reward (float) :
                amount of reward achieved by the previous action. The scale
                varies between environments, but the goal is always to increase
                your total reward.
            episode_over (bool) :
                whether it's time to reset the environment again. Most (but not
                all) tasks are divided up into well-defined episodes, and done
                being True indicates the episode has terminated. (For example,
                perhaps the pole tipped too far, or you lost your last life.)
            info (dict) :
                 diagnostic information useful for debugging. It can sometimes
                 be useful for learning (for example, it might contain the raw
                 probabilities behind the environment's last state change).
                 However, official evaluations of your agent are not allowed to
                 use this for learning.
        """

        self._take_action(action, player)
        reward = self._get_reward(player)
        ob = self.env.get_state(player)
        episode_over = self.env.is_over()
        return ob, reward, episode_over, {}

    def _reset(self):
        self.players = [player.Player(gold_deck), player.Player(silver_deck)]
        self.env = game.Game(self.players)
        self.env.start_game()

    def _render(self, mode='human', close=False):
        print("Player 0:")
        print(self.env.get_state(0))
        print("Player 1:")
        print(self.env.get_state(1))

    def _take_action(self, action, player):
        if player == current_game.player_with_priority.index:
            legal_moves = self.env.get_legal_moves(self.env.player_with_priority)
            self.env.make_move(legal_moves[action], False)

    def _get_reward(self, player):
        if not self.env.players[player].has_lost:
            return 1
        elif self.env.players[1 - player].has_lost:
            return 100
        else:
            return 0
