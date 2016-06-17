"""Domain model classes (mostly persistent)."""
# Because this application requires both ndb.Model subclasses
# to persist entities and domain objects that encapsulate
# wordwars game logic we could have created two separate
# layers: the persistence layer and the domain layer.
# Instead we have all but eliminated the persistence layer.
# These models are our domain objects but they subclass
# ndb.Model so that we can persist them as well.  The
# only concession to the persistence model is the need
# to define all persistent fields with ndb.XProperty(...)
# annotations.  All actual persistence operations are
# handled by classes in repositories.py.

# have to add sys.path.inserts to get unit tests to work
# import sys
# sys.path.insert(1, '/usr/local/google_appengine')
# sys.path.insert(1, '/usr/local/google_appengine/lib/yaml/lib')

from google.appengine.ext import ndb
from random import randint
from utils import get_by_urlsafe
import datetime


class User(ndb.Model):
    """Model of user that can play in a game."""
    # User may be a player in many games: one PlayerState for each GameState
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()

    @classmethod
    def create(cls, name, email):
        """Class factory method to create a User."""
        user = cls()
        user.name = name
        user.email = email
        return user

    def identity(self):
        """Return unique identity for this User."""
        return self.email

# a few declarations to support GameState logic

# simple set of all letters of the alphabet
alphabet = "abcdefghijklmnopqrstuvwxyz"

# simple map from each letter to its scoring value when placed on the board
letterValue = {'a': 1, 'b': 2, 'c': 2, 'd': 2, 'e': 1, 'f': 3, 'g': 3,
               'h': 2, 'i': 1, 'j': 5, 'k': 3, 'l': 2, 'm': 1, 'n': 1,
               'o': 1, 'p': 2, 'q': 5, 'r': 2, 's': 1, 't': 1, 'u': 2,
               'v': 3, 'w': 3, 'x': 9, 'y': 5, 'z': 5}


# a cheap way to compute how many of each letter to put in inital bag
def duplicates(l):
    return 10/letterValue[l]

# Game state constant strings
MODE_NEW = 'new'
MODE_PLAYING = 'playing'
MODE_CANCELLED = 'cancelled'
MODE_OVER = 'over'


class GameState(ndb.Model):
    """Model of wordwars game state."""
    # a GameState is referenced by PlayerState for each player
    letters = ndb.StringProperty(required=True)
    width = ndb.IntegerProperty(required=True)
    height = ndb.IntegerProperty(required=True)
    board = ndb.StringProperty(required=True)
    consecutivePasses = ndb.IntegerProperty(required=True)
    createdTime = ndb.DateTimeProperty(auto_now_add=True)
    turn = ndb.IntegerProperty(required=True)
    mode = ndb.StringProperty(required=True)
    lastUpdate = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def create(cls):
        """Class factory method to create a GameState."""
        game = cls()    # get new ndb.Model instance
        game.mode = MODE_NEW
        game.turn = 0
        game.bagOfLetters = LetterBag.standardSet()
        game.width = 10
        game.height = 10
        game.boardContent = []
        for x in range(game.width):
            for y in range(game.height):
                game.boardContent.append('_')    # init board with underscores
        game.players = []
        game.consecutivePasses = 0
        return game

    def addPlayer(self, user):
        """Add user as a player in this game."""
        if self.started():
            raise ValueError('Cannot add player to game in progress.')
        # okay to add players until started with first turn
        playerSequence = len(self.players)   # zero for first player
        # initialize each player with 7 letters from game bag
        lettersForPlayer = self.bagOfLetters.removeRandom(7)
        pState = PlayerState.create(
            self, user, playerSequence, lettersForPlayer)
        self.players.append(pState)

    def start(self):
        """Start the game.  No more players may be added."""
        self.turn = 0
        self.mode = MODE_PLAYING
        return self.nextPlayer()

    def cancel(self):
        """Cancel the game.  There is no winner."""
        self.mode = MODE_CANCELLED

    def started(self):
        """Return True if game has started."""
        return self.mode != MODE_NEW

    def cancelled(self):
        """Return True if game has been cancelled."""
        return self.mode == MODE_CANCELLED

    def nextPlayer(self):
        """Return PlayerState for player with next turn."""
        if self.mode != MODE_PLAYING:
            return None
        for p in self.players:
            if p.turnNumber == self.turn:
                return p
        return None

    def directionString(self, across):
        """Translate boolean direction to 'across' or 'down'."""
        if across:
            return 'across'
        else:
            return 'down'

    def getPlayerState(self, user):
        """Return PlayerState for user or None."""
        for p in self.players:
            if p.player.identity() == user.identity():
                return p
        return None

    def incrementTurn(self):
        """Advance game state to next turn."""
        self.turn += 1
        if self.turn == len(self.players):
            self.turn = 0

    def playWord(self, user, x, y, across, word):
        """Play word as instructed by user."""
        playerState = self.getPlayerState(user)
        beforeScore = playerState.score  # so we can reset on error
        beforeLetters = playerState.bag.copy()
        try:
            self.addWordToBoard(playerState, x, y, across, word)
            lettersPlayed = 7 - playerState.bag.contentCount()
            self.enforceMinimumOneLetterRule(lettersPlayed)
            playerState.bag.addAll(
                self.bagOfLetters.removeRandom(lettersPlayed))
            self.incrementTurn()
            self.consecutivePasses = 0
        except Exception, e:
            # reset state
            playerState.score = beforeScore
            playerState.bag = beforeLetters
            raise e

    def enforceMinimumOneLetterRule(self, lettersPlayed):
        if lettersPlayed < 1:
            dir = 'across'
            if not across:
                dir = 'down'
            raise ValueError(
                'Playing {} {} at {},{} adds no letters to the board.'.format(
                    word, dir, x, y))

    def addWordToBoard(self, playerState, x, y, across, word):
        """Implement algorithm for updating board and accumulating score."""
        nextX = x
        nextY = y
        for i in range(len(word)):
            letter = word[i]
            if across:
                nextX = x + i
            else:
                nextY = y + i
            self.addLetterToBoard(playerState, nextX, nextY, letter)

    def addLetterToBoard(self, playerState, x, y, letter):
        """Implement algorithm for adding single letter to the board."""
        if self.letter(x, y) == '_':
            playerState.bag.remove(letter)  # raises error if not there
            self.setBoardContent(x, y, letter)
        playerState.score = playerState.score + letterValue[letter]

    def skipTurn(self, user):
        """Advance turn without playing a word."""
        ps = self.getPlayerState(user)  # confirm it is this user's turn
        self.consecutivePasses += 1
        if self.consecutivePasses >= len(self.players):
            self.mode = MODE_OVER
        self.incrementTurn()

    def gameOver(self):
        """Return True if game is complete/over or cancelled."""
        return self.mode == MODE_OVER or self.mode == MODE_CANCELLED

    def gameComplete(self):
        """Return True if game is over."""
        return self.mode == MODE_OVER

    def boardIndex(self, x, y):
        i = x + (y * self.width)
        if i >= len(self.boardContent):
            raise ValueError(
                'cannot access board position ({},{})'.format(x, y))
        return i

    def letter(self, x, y):
        return self.boardContent[self.boardIndex(x, y)]

    def setBoardContent(self, x, y, letter):
        self.boardContent[self.boardIndex(x, y)] = letter

    def leader(self):
        """Return PlayerState with current high score."""
        if not self.players:
            return None
        leader = self.players[0]
        for p in self.players:
            if p.score > leader.score:
                leader = p
        return leader

    def scoreForUser(self, user):
        """Return current score for user."""
        for p in self.players:
            if p.player.identity() == user.identity():
                return p.score
        raise ValueError('user {} is not a player'.format(user.name))


class PlayerState(ndb.Model):
    """Part of a gameState that describes player."""
    gameKey = ndb.KeyProperty(required=True, kind='GameState')
    userKey = ndb.KeyProperty(required=True, kind='User')
    turnNumber = ndb.IntegerProperty(required=True)
    letters = ndb.StringProperty(required=True)
    score = ndb.IntegerProperty(required=True)

    @classmethod
    def create(cls, game, user, turnNumber, bag):
        """Class factory method to create a PlayerState."""
        state = cls()       # new instance of class
        state.game = game
        state.player = user
        state.turnNumber = turnNumber
        state.bag = bag
        state.score = 0
        return state


class Notification(ndb.Model):
    """Part of a gameState that describes player."""
    gameKey = ndb.KeyProperty(required=True, kind='GameState')
    userKey = ndb.KeyProperty(required=True, kind='User')
    description = ndb.StringProperty(required=True)
    createdTime = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def create(cls, game, user, description):
        """Class factory method to create a PlayerState."""
        note = cls()       # new instance of class
        note.game = game
        note.user = user
        note.description = description
        return note


class LetterBag():
    """Store count of letters held."""

    def __init__(self):
        self.map = {}
        for l in alphabet:
            self.map[l] = 0

    @classmethod
    def fromString(cls, s):
        """Construct a LetterBag from string."""
        bag = cls()
        for l in s:
            bag.add(l)
        return bag

    @classmethod
    def standardSet(cls):
        """Construct a LetterBag with WordWars standard initial set."""
        bag = LetterBag()
        for l in alphabet:
            for i in range(duplicates(l)):
                bag.add(l)
        return bag

    def add(self, l):
        """Add a letter to this bag."""
        self.map[l] += 1

    def addAll(self, bag):
        """Add all letters from another bag to this bag."""
        for l in alphabet:
            self.map[l] += bag.map[l]
        return self

    def remove(self, l):
        """Remove letter l from this bag."""
        if self.map[l] > 0:
            self.map[l] -= 1
        else:
            raise ValueError('no letter {} to remove'.format(l))

    def removeRandom(self, count):
        """Remove and return 'count' random letters from this bag."""
        removed = LetterBag()
        selfSize = self.contentCount()
        for i in range(count):
            if self.contentCount() <= 0:
                return removed
            l = self.removeByIndex(randint(0, selfSize - 1))
            selfSize -= 1
            removed.add(l)
        return removed

    def removeByIndex(self, i):
        """Remove the ith letter (alphabetic order) from bag."""
        l = self.letterAtIndex(i)
        self.remove(l)
        return l

    def letterAtIndex(self, i):
        """Compute ith letter (alphabetic order) in bag."""
        lettersToGo = i
        for l in alphabet:
            if self.map[l] > lettersToGo:
                return l   # we are at the index we were looking for
            else:
                lettersToGo -= self.map[l]   # skip past this letter

    def contentCount(self):
        """Return count of all letters in bag."""
        count = 0
        for l in alphabet:
            count += self.map[l]
        return count

    def asString(self):
        """Return string representation of bag contents."""
        letters = ''
        for l in alphabet:
            for i in range(self.map[l]):
                letters += l
        return letters

    def copy(self):
        """Return copy of this bag."""
        return LetterBag().addAll(self)

    def __repr__(self):
        """Return string representation of my map."""
        return self.map.__repr__()


class Move(ndb.Model):
    """Model of a move played in a game."""
    gameKey = ndb.KeyProperty(required=True, kind='GameState')
    userKey = ndb.KeyProperty(required=True, kind='User')
    time = ndb.DateTimeProperty(required=True)
    moveScore = ndb.IntegerProperty(required=True)
    word = ndb.StringProperty(required=True)
    across = ndb.BooleanProperty(required=False)
    x = ndb.IntegerProperty(required=False)
    y = ndb.IntegerProperty(required=False)

    @classmethod
    def create(cls, game, user, word, across, x, y, score):
        """Class factory method to create a User."""
        move = cls()
        move.game = game  # set gameKey from this game
        move.user = user  # set userKey from this user
        move.word = word
        move.across = across
        move.x = x
        move.y = y
        move.moveScore = score
        move.time = datetime.datetime.now()
        return move
