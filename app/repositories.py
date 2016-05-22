
"""repositories.py - contains Repository class definitions that encapsulate the ndb persistence model.
The Repository pattern is used.  For an ndb.Model m and EntityRepository MRepository, clients must:
    - call MRepository().register(m) to persist m and return its id value
    - call m = MRepository().findById( id ) to retrieve the entity by its id (from the register operation above)
    - call MRepository().update(m) to save changes made to m (raises an error if m has not been registered)
"""

import sys
sys.path.insert(1, '/usr/local/google_appengine')
sys.path.insert(1, '/usr/local/google_appengine/lib/yaml/lib')

from google.appengine.ext import ndb
from random import randint
from utils import get_by_urlsafe
from models import User, GameState, PlayerState, LetterBag


"""access persistent collection of User"""
class UserRepository():

    """add user to this collection and set its identity"""
    def register(self, user):
        if user.key == None:
            user.put()
        return user

    """update user in this collection"""
    def update(self, user):
        user.put()
        return user

    """return identity of this user"""
    def id(self, user):
        return user.key.urlsafe()

    """return user with this id"""
    def findById(self, id):
        return get_by_urlsafe(id, User)

    """return user with this name"""
    def findByName(self, name):
        return User.query(User.name == name).get()

    """return list of all users"""
    def all(self):
        return User.query().fetch()


"""access persistent collection of GameState"""
class GameStateRepository():

    """add gameState and its parts to this collection and set its identity"""
    def register(self, gameState):
        self.setPersistents(gameState)
        gameState.put()
        for p in gameState.players:
            p.gameKey = gameState.key
            PlayerStateRepository().register(p)
        return gameState

    """set persistent fields from transient values"""
    def setPersistents(self, state):
        state.letters = state.bagOfLetters.asString()  # set persistent field from transient state
        state.board = ''.join(state.boardContent)      # set persistent field from transient state
        return state

    """set transient values from persistent fields"""
    def restoreTransients(self, state):
        state.bagOfLetters = LetterBag.fromString(state.letters)
        state.boardContent = list(state.board)    # easier to access content as a list
        return state

    """update persistent gameState and its parts in this collection"""
    def update(self, gameState):
        self.setPersistents(gameState)
        gameState.put()
        for p in gameState.players:
            p.gameKey = gameState.key
            PlayerStateRepository().update(p)
        return gameState

    """return identity for this gameState"""
    def id(self, gameState):
        return gameState.key.urlsafe()

    """return gameState with this id"""
    def findById(self, id):
        game = get_by_urlsafe(id, GameState)
        self.restoreTransients(game)
        game.players = PlayerStateRepository().findByGame(game)
        return game

    def allCompleted(self):
        """return all games with mode == 'completed'"""
        all = GameState.query(GameState.mode == 'over').fetch()
        for game in all:
            game.players = PlayerStateRepository().findByGame(game)
            self.restoreTransients(game)
        return all

"""access persistent collection of PlayerState"""
class PlayerStateRepository():

    """add playerState to collection and set unique identity"""
    def register(self, p):
        UserRepository().register(p.player)
        self.setPersistents(p)
        p.put()
        return p

    """update playerState in collection"""
    def update(self, p):
        UserRepository().update(p.player)
        self.setPersistents(p)
        p.put()
        return p

    """return unique identity for player"""
    def id(self, p):
        return p.key.urlsafe()

    """set persistent fields from transient values"""
    def setPersistents(self, state):
        state.gameKey = state.game.key
        state.userKey = state.player.key
        state.letters = state.bag.asString()
        return state

    """set (derive) transient values from persistent fields"""
    def restoreTransients(self, state):
        state.game = state.gameKey.get()
        state.player = state.userKey.get()
        state.bag = LetterBag.fromString(state.letters)
        return state

    """return player with this id"""
    def findById(self, id):
        p = get_by_urlsafe(id, PlayerState)
        return self.restoreTransients(p)

    """return list of players in this game"""
    def findByGame(self, game):
        list =  PlayerState.query(PlayerState.gameKey==game.key).fetch()
        for p in list:
            self.restoreTransients(p)
        return list

    """return list of game-player roles for this user"""
    def findByUser(self, user):
        list =  PlayerState.query(PlayerState.userKey==user.key).fetch()
        for p in list:
            self.restoreTransients(p)
        return list
