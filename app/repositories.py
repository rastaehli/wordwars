
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

# apply Repository pattern to encapsulate details of persistence
class UserRepository():

    def register(self, user):
        if user.key == None:
            user.put()
        return user

    def update(self, user):
        user.put()
        return user

    def id(self, user):
        return user.key.urlsafe()

    def findById(self, id):
        return get_by_urlsafe(id, User)

    def findByName(self, name):
        return User.query(User.name == name).get()

    def all(self):
        return User.query().fetch()

# apply Repository pattern to encapsulate details of persistence
class GameStateRepository():

    # persist gameState and its parts
    def register(self, gameState):
        self.setPersistents(gameState)
        gameState.put()
        for p in gameState.players:
            p.gameKey = gameState.key
            PlayerStateRepository().register(p)
        return gameState

    def setPersistents(self, state):
        state.letters = state.bagOfLetters.asString()  # set persistent field from transient state
        state.board = ''.join(state.boardContent)      # set persistent field from transient state
        return state

    def restoreTransients(self, state):
        state.bagOfLetters = LetterBag.fromString(state.letters)
        state.boardContent = list(state.board)    # easier to access content as a list
        return state

    # persist gameState and its parts
    def update(self, gameState):
        self.setPersistents(gameState)
        gameState.put()
        for p in gameState.players:
            p.gameKey = gameState.key
            PlayerStateRepository().update(p)
        return gameState

    def id(self, gameState):
        return gameState.key.urlsafe()

    def findById(self, id):
        game = get_by_urlsafe(id, GameState)
        self.restoreTransients(game)
        game.players = PlayerStateRepository().findByGame(game.key)
        return game

# apply Repository pattern to encapsulate details of persistence
class PlayerStateRepository():

    # persist playerState
    def register(self, p):
        UserRepository().register(p.player)
        self.setPersistents(p)
        p.put()
        return p

    # update playerState
    def update(self, p):
        UserRepository().update(p.player)
        self.setPersistents(p)
        p.put()
        return p

    def id(self, p):
        return p.key.urlsafe()

    def setPersistents(self, state):
        state.userKey = state.player.key        # set persistent field from transient state
        state.letters = state.bag.asString()    # set persistent field from transient state
        return state

    def restoreTransients(self, state):
        state.player = state.userKey.get()
        state.bag = LetterBag.fromString(state.letters)
        return state

    def findById(self, id):
        p = get_by_urlsafe(id, PlayerState)
        return self.restoreTransients(p)

    def findByGame(self, aGameKey):
        list =  PlayerState.query(PlayerState.gameKey==aGameKey).fetch()
        for p in list:
            self.restoreTransients(p)
        return list

    def findByUser(self, aUserKey):
        list =  PlayerState.query(PlayerState.userKey==aUserKey).fetch()
        for p in list:
            self.restoreTransients(p)
        return list
