#!/usr/bin/env python

import sys
sys.path.insert(1, '/usr/local/google_appengine')
sys.path.insert(1, '/usr/local/google_appengine/lib/yaml/lib')

import random
import copy
import ww_models

class WordWars():
    def newGame(self, user):
        game = ww_models.GameState([user])
        savedGame = games.register(game)
        return games.id(savedGame)      # use this id to retrieve game state

    def joinGame(self, gameId, user):
        game = games.findById(gameId)
        game.addPlayer(user)
        games.update(game)



