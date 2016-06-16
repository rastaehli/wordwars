"""repositories.py - contains Repository class definitions that encapsulate the ndb persistence model.
The Repository pattern is used.  For an ndb.Model m and EntityRepository MRepository, clients must:
    - call MRepository().register(m) to persist m and return its id value
    - call m = MRepository().findById( id ) to retrieve the entity by its id (from the register operation above)
    - call MRepository().update(m) to save changes made to m (raises an error if m has not been registered)
"""

# had to add sys.path.inserts to resolve imports when run from unit test (as opposed to dev_appserver)
# import sys
# sys.path.insert(1, '/usr/local/google_appengine')
# sys.path.insert(1, '/usr/local/google_appengine/lib/yaml/lib')

from google.appengine.ext import ndb
from random import randint
from utils import get_by_urlsafe
from models import User, GameState, PlayerState, LetterBag, Move, Notification
import datetime


class UserRepository():
    """access persistent collection of User"""

    def register(self, user):
        """add user to this collection and set its identity"""
        return self.update(user)

    def update(self, user):
        """update user in this collection"""
        user.put()
        return user

    def id(self, user):
        """return identity of this user"""
        return user.key.urlsafe()

    def findById(self, id):
        """return user with this id"""
        return get_by_urlsafe(id, User)

    def findByName(self, name):
        """return user with this name"""
        return User.query(User.name == name).get()

    def all(self):
        """return list of all users"""
        return User.query().fetch()


class GameStateRepository():
    """access persistent collection of GameState"""

    def register(self, gameState):
        """add gameState and its parts to this collection and set its identity"""
        return self.update(gameState)

    def setPersistents(self, state):
        """set persistent fields from transient values"""
        state.letters = state.bagOfLetters.asString()  # set persistent field from transient state
        state.board = ''.join(state.boardContent)      # set persistent field from transient state
        return state

    def restoreTransients(self, state):
        """set transient values from persistent fields"""
        state.bagOfLetters = LetterBag.fromString(state.letters)
        state.boardContent = list(state.board)    # easier to access content as a list
        return state

    def update(self, gameState):
        """update persistent gameState and its parts in this collection"""
        self.setPersistents(gameState)
        gameState.put()
        for p in gameState.players:
            p.gameKey = gameState.key
            PlayerStateRepository().update(p)
        return gameState

    def id(self, gameState):
        """return identity for this gameState"""
        return gameState.key.urlsafe()

    def findById(self, id):
        """return gameState with this id"""
        try:
            game = get_by_urlsafe(id, GameState)
            self.restoreTransients(game)
            game.players = PlayerStateRepository().findByGame(game)
        except Exception:
            game = None
        return game

    def allCompleted(self):
        """Return all games in completed state."""
        all = GameState.query(GameState.mode == 'over').fetch()
        for game in all:
            game.players = PlayerStateRepository().findByGame(game)
            self.restoreTransients(game)
        return all

    def allActive(self):
        """Return all games in active state."""
        all = GameState.query(GameState.mode == 'playing').fetch()
        for game in all:
            game.players = PlayerStateRepository().findByGame(game)
            self.restoreTransients(game)
        return all

    def playersToNotify(self):
        """Find players who've taken more than 5 minutes to play their turn.
        but filter out those who've already been notified."""

        # get all games in play
        activeGames = self.allActive()
        # get those NOT updated in the last five minutes
        now = datetime.datetime.now()
        fiveMinutesAgo = now - datetime.timedelta(minutes=5)
        idleGames = [game for game in activeGames if (game.lastUpdate < fiveMinutesAgo)]
        # get list of users whose turn it is
        playersUp = [game.nextPlayer() for game in idleGames]
        # filter by those who have not been notified in the last day
        notifications = NotificationRepository()
        usersNotified = notifications.getUsersRecentlyNotified()
        playersToNotify = []
        users = UserRepository()
        for playerState in playersUp:
            notify = True
            for u in usersNotified:
                if users.id(u) == users.id(playerState.player):
                    notify = False
            if notify:
                playersToNotify.append(playerState)
        return playersToNotify


class PlayerStateRepository():
    """access persistent collection of PlayerState"""

    def register(self, p):
        """add playerState to collection and set unique identity"""
        return self.update(p)

    def update(self, p):
        """update playerState in collection"""
        UserRepository().update(p.player)
        self.setPersistents(p)
        p.put()
        return p

    def id(self, p):
        """return unique identity for player"""
        return p.key.urlsafe()

    def setPersistents(self, state):
        """set persistent fields from transient values"""
        state.gameKey = state.game.key
        state.userKey = state.player.key
        state.letters = state.bag.asString()
        return state

    def restoreTransients(self, state):
        """set (derive) transient values from persistent fields"""
        state.game = state.gameKey.get()
        state.player = state.userKey.get()
        state.bag = LetterBag.fromString(state.letters)
        return state

    def findById(self, id):
        """return player with this id"""
        p = get_by_urlsafe(id, PlayerState)
        return self.restoreTransients(p)

    def findByGame(self, game):
        """return list of players in this game"""
        list = PlayerState.query(PlayerState.gameKey == game.key).fetch()
        for p in list:
            self.restoreTransients(p)
        return list

    def findByUser(self, user):
        """return list of game-player roles for this user"""
        list = PlayerState.query(PlayerState.userKey == user.key).fetch()
        for p in list:
            self.restoreTransients(p)
        return list


class MoveRepository():
    """access persistent collection of Move"""

    def register(self, move):
        """add move to collection and set unique identity"""
        return self.update(move)

    def update(self, move):
        """update move in collection"""
        self.setPersistents(move)
        move.put()
        return move

    def setPersistents(self, move):
        """set persistent fields from transient values"""
        move.gameKey = move.game.key
        move.userKey = move.user.key
        return move

    def id(self, move):
        """return unique identity for move"""
        return move.key.urlsafe()

    def historyForGame(self, game):
        """return list of moves from this game"""
        list = Move.query(Move.gameKey == game.key).fetch()
        for move in list:
            move.game = game
            move.user = self.getPlayer(game, move)
        return list

    def getPlayer(self, game, move):
        """get user for this move from game by userKey"""
        for p in game.players:
            if p.player.key == move.userKey:
                return p.player
        return None


# constants describing types of notifications.
YOUR_TURN = 'your turn'


class NotificationRepository():
    """Keep persistent collection of Notification emails sent."""

    def getUsersRecentlyNotified(self):
        "Return list of Users notified in the last 24 hours."
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        lastDaysNotes = Notification.query(Notification.createdTime > yesterday).fetch()
        for note in lastDaysNotes:
            self.restoreTransients(note)
        return [note.user for note in lastDaysNotes]

    def registerTurnNotification(self, user, game):
        "Register an It's Your Turn email has been sent to user."
        self.register(Notification.create(game, user, YOUR_TURN))

    def register(self, note):
        """add note to collection and set unique identity"""
        return self.update(note)

    def update(self, note):
        """update note in collection"""
        self.setPersistents(note)
        note.put()
        return note

    def setPersistents(self, note):
        """set persistent fields from transient values"""
        note.gameKey = note.game.key
        note.userKey = note.user.key
        return note

    def restoreTransients(self, note):
        """set (derive) transient values from persistent fields"""
        note.game = note.gameKey.get()
        note.user = note.userKey.get()
        return note
