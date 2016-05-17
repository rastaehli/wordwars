
"""ww-models.py - This file contains the class definitions for the Datastore
entities used by WordWars. As in any good object oriented design, methods that
need to know the internal state of the model objects are made part of the class."""

import sys
sys.path.insert(1, '/usr/local/google_appengine')
sys.path.insert(1, '/usr/local/google_appengine/lib/yaml/lib')

from google.appengine.ext import ndb
from random import randint
from utils import get_by_urlsafe

class User(ndb.Model):
    # User may be a player in many games via one PlayerState for each GameState
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()

    @classmethod
    def create(cls, name, email):
        user = cls()
        user.name = name
        user.email = email
        return user 

    def identity(self):
        return self.email

# a few declarations to support GameState logic

#simple set of all letters of the alphabet
alphabet = "abcdefghijklmnopqrstuvwxyz"

# simple map from each letter to its scoring value when placed on the board
letterValue = {'a': 1, 'b': 2, 'c': 2, 'd': 2, 'e': 1, 'f': 3, 'g': 3, 
        'h': 2, 'i': 1, 'j': 5, 'k': 3, 'l': 2, 'm': 1, 'n': 1, 'o': 1, 'p': 2, 
        'q': 5, 'r': 2, 's': 1, 't': 1, 'u': 2, 'v': 3, 'w': 3, 'x': 9, 'y': 5, 'z': 5}

# a poor algorithm for determining how many of each letter to put in inital bag
def duplicates(l):
    return 10/letterValue[l]


class GameState(ndb.Model):
    # a GameState is referenced by PlayerState for each player
    letters = ndb.StringProperty(required=True)
    width = ndb.IntegerProperty(required=True)
    height = ndb.IntegerProperty(required=True)
    board = ndb.StringProperty(required=True)
    consecutivePasses = ndb.IntegerProperty(required=True)
    createdTime = ndb.DateTimeProperty(auto_now_add=True)
    turn = ndb.IntegerProperty(required=True)

    @classmethod
    def create(cls):
        game = cls()    # get new ndb.Model instance
        game.turn = -1  # negative value until start() called
        game.bagOfLetters = LetterBag.standardSet()
        game.width = 17
        game.height = 17
        game.boardContent = []
        for x in range(game.width):
            for y in range(game.height):
                game.boardContent.append('_')    # init board with underscores
        game.players = []
        game.consecutivePasses = 0
        return game

    def addPlayer(self, user):
        if self.started():
            raise ValueError('Cannot add player to game in progress.')
        # okay to add players until started with first turn
        playerSequence = len(self.players)  # zero for first player
        lettersForPlayer = self.bagOfLetters.removeRandom(7) # init with 7 from game bag
        pState = PlayerState.create(self, user, playerSequence, lettersForPlayer)
        self.players.append(pState)

    def start(self):
        self.turn = 0
        return self.nextPlayer()

    def started(self):
        return self.turn >= 0

    def nextPlayer(self):
        for p in self.players:
            if p.turnNumber == self.turn:
                return p
        return None

    def directionString(self, across):
        if across:
            return 'across'
        else: 
            return 'down'

    def getPlayerState(self, user):
        for p in self.players:
            if p.player.identity() == user.identity():
                return p
        return None

    def incrementTurn(self):
        self.turn = self.turn + 1
        if self.turn == len(self.players):
            self.turn = 0

    def playWord(self, user, x, y, across, word):
        self.addWordToBoard(self.getPlayerState(user), x, y, across, word)
        self.incrementTurn()
        self.consecutivePasses = 0

    def addWordToBoard(self, playerState, x, y, across, word):
        print('===============player {} adding {}'.format(playerState.player.name, word))
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
        if self.letter(x,y) == '_':
            playerState.bag.remove(letter)  # raises error if not there
            self.setBoardContent(x,y,letter)
        print('===============played {} with value {}'.format(letter, letterValue[letter]))
        playerState.score = playerState.score + letterValue[letter]     # accumulate score
       
    def skipTurn(self, user):
        ps = self.getPlayerState(user)
        self.consecutivePasses += 1
        self.incrementTurn()

    def gameOver(self):
        return self.consecutivePasses >= len(self.players) 

    def boardIndex(self, x,y):
        i = x + (y * self.width)
        if i >= len(self.boardContent):
            raise ValueError('cannot access board position ({},{})'.format(x,y))
        return i

    def letter(self, x,y):
        return self.boardContent[ self.boardIndex(x,y) ]

    def setBoardContent(self, x, y, letter):
        self.boardContent[ self.boardIndex(x,y) ] = letter

    def leader(self):
        leader = self.players[0]
        for p in self.players:
            if p.score > leader.score:
                leader = p
        return leader

    def scoreForUser(self, user):
        for p in self.players:
            if p.player.identity() == user.identity():
                return p.score
        raise ValueError('user {} is not a player'.format(user.name))

# part of a gameState that describes player
class PlayerState(ndb.Model):
    gameKey = ndb.KeyProperty(required=True, kind='GameState')
    userKey = ndb.KeyProperty(required=True, kind='User')
    turnNumber = ndb.IntegerProperty(required=True)
    letters = ndb.StringProperty(required=True)
    score = ndb.IntegerProperty(required=True)

    @classmethod
    def create(cls, game, user, turnNumber, bag):
        state = cls()       # new instance of class
        state.player = user
        state.turnNumber = turnNumber
        state.bag = bag
        state.score = 0
        return state

# Store count of letters held.
class LetterBag():

    def __init__(self):
        self.map = {}
        for l in alphabet:
            self.map[l] = 0

    @classmethod
    def fromString(cls, s):
        bag = cls()
        for l in s:
            bag.add(l)
        return bag 

    @classmethod
    def standardSet(cls):
        bag = LetterBag()
        for l in alphabet:
            for i in range(duplicates(l)):
                bag.add(l)
        return bag

    def add(self, l):
        self.map[l] += 1

    def addAll(self, bag):
        for l in alphabet:
            self.map[l] += bag.map[l]

    def remove(self, l):
        if self.map[l] > 0:
            self.map[l] -= 1
        else:
            raise ValueError('no letter {} to remove'.format(l))

    def removeRandom(self, itemCount):
        removed = LetterBag()
        selfSize = self.contentCount()
        for i in range(itemCount):
            if self.contentCount() <= 0:
                return removed
            l = self.removeByIndex(randint(0,selfSize-1))
            selfSize -= 1
            removed.add(l)
        return removed

    def removeByIndex(self, i):
        l = self.letterAtIndex(i)
        self.remove(l)
        return l

    def letterAtIndex(self, i):
        lettersToGo = i
        for l in alphabet:
            if self.map[l] > lettersToGo:
                return l                   # we are at the index we were looking for
            else:
                lettersToGo -= self.map[l] # skip past this letter

    def contentCount(self):
        count = 0
        for l in alphabet:
            count += self.map[l]
        return count

    def asString(self):
        letters = ""
        for l in alphabet:
            for i in range(self.map[l]):
                letters += l
        return letters

    def __repr__(self):
        return self.map.__repr__()




