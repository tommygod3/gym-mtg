import os, subprocess, time, signal
import copy
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding
from open_mtg import player, deck, game

class MtgEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.gold_deck = deck.get_8ed_core_gold_deck()
        self.silver_deck = deck.get_8ed_core_silver_deck()
        self.players = [player.Player(self.gold_deck), player.Player(self.silver_deck)]
        self.env = game.Game(self.players)
        self.env.start_game()
        self.current_player = 0
    
    @property
    def action_space(self):
        if self.current_player == self.env.player_with_priority.index:
            legal_moves = self.env.get_legal_moves(self.env.player_with_priority)
            return spaces.Discrete(len(legal_moves))
        else:
            return spaces.Discrete(1)

    @property
    def observation_space(self):
        player_object = self.env.players[self.current_player]
        player_decklist = copy.deepcopy(player_object.deck)

        return spaces.Dict({
            "life": spaces.Discrete(1),
            "hand": spaces.Discrete(len(player_object.hand)),
            "graveyard": spaces.Discrete(len(player_object.graveyard)),
            "deck": spaces.Discrete(len(player_decklist)),
            "battlefield": spaces.Discrete(len(self.env.battlefield)),
            "attackers": spaces.Discrete(len(self.env.attackers)),
            "blockers": spaces.Discrete(len(self.env.blockers)),
            "empty_stack": spaces.Discrete(1),
            "damage_targets": spaces.Discrete(len(self.env.damage_targets)),
            "active_player": spaces.Discrete(1),
            "nonactive_player": spaces.Discrete(1),
            "priority": spaces.Discrete(1),
            "current_phase": spaces.Discrete(1)
        })

    def step(self, action):
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

        self._take_action(action)
        reward = self._get_reward()
        ob = self.env.get_state(self.current_player)
        episode_over = self.env.is_over()
        self.current_player = 1 - self.current_player
        return ob, reward, episode_over, {}

    def reset(self):
        self.current_player = 0
        self.players = [player.Player(self.gold_deck), player.Player(self.silver_deck)]
        self.env = game.Game(self.players)
        self.env.start_game()

    def _render(self, mode='human', close=False):
        print("Player 0:")
        print(self.env.get_state(0))
        print("Player 1:")
        print(self.env.get_state(1))

    def _take_action(self, action):
        if self.current_player == self.env.player_with_priority.index:
            legal_moves = self.env.get_legal_moves(self.env.player_with_priority)
            self.env.make_move(legal_moves[action], False)

    def _get_reward(self):
        if not self.env.players[self.current_player].has_lost:
            return 1
        elif self.env.players[1 - self.current_player].has_lost:
            return 100
        else:
            return 0
