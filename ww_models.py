
"""ww-models.py - This file contains the class definitions for the Datastore
entities used by Word Wars. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

"""The Repository pattern is used.  For an entity (ndb.Model) e and EntityRepository r, clients must:
    - call r.register(e) to persist e and return its id value
    - call e = r.findById( id ) to retrieve the entity by its id (from r.register(e) above)
    - call r.save(e) to save changes made to e (raises an error if r has not been registered)
"""

# import sys
# sys.path.insert(1, '/usr/local/google_appengine')
# sys.path.insert(1, '/usr/local/google_appengine/lib/yaml/lib')

# from google.appengine.ext import ndb
from random import randint

# class User(ndb.Model):
class User():
    # User may be a player in many games via one PlayerState for each GameState
    # name = ndb.StringProperty(required=True)
    # email = ndb.StringProperty()

    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.id = None

    def identity(self):
        return self.email

# # apply Repository pattern to encapsulate details of persistence
# class UserRepository():

#     def register(user):
#         user.put()
#         return user

#     def id(user):
#         return user.key.urlsafe()

#     def findById(id):
#         return get_by_urlsafe(id, User)


# a few declarations to support WordWars game logic

#simple set of all letters of the alphabet
alphabet = "abcdefghijklmnopqrstuvwxyz"

# simple map from each letter to its scoring value when placed on the board
letterValue = {'a': 1, 'b': 2, 'c': 2, 'd': 2, 'e': 1, 'f': 3, 'g': 3, 
        'h': 2, 'i': 1, 'j': 5, 'k': 3, 'l': 2, 'm': 1, 'n': 1, 'o': 1, 'p': 2, 
        'q': 5, 'r': 2, 's': 1, 't': 1, 'u': 2, 'v': 3, 'w': 3, 'x': 9, 'y': 5, 'z': 5}

# a poor algorithm for determining how many of each letter to put in inital bag
def duplicates(l):
    return 10/letterValue[l]


# class GameState(ndb.Model):
class GameState():
    #a GameState may have many players state
    # bagOfLetters = ndb.StringProperty(required=True)
    # boardWidth = ndb.IntegerProperty(required=True)
    # boardHeight = ndb.IntegerProperty(required=True)
    # boardContent = ndb.StringProperty(required=True)
    # consecutivePasses = ndb.IntegerProperty(required=True)
    # createdTime = ndb.DateTimeProperty(auto_now_add=True)
    # turn = ndb.IntegerProperty(required=True)

    def __init__(self, users):
        self.turn = -1  # negative value until start() called
        self.bagOfLetters = LetterBag()
        for l in alphabet:
            for i in range(duplicates(l)):
                self.bagOfLetters.add(l)
        self.width = 17
        self.height = 17
        self.boardContent = []
        for x in range(self.width):
            for y in range(self.height):
                self.boardContent.append('_')    # init board with underscores
        self.players = []
        for u in users:
            self.addPlayer(u)
        self.consecutivePasses = 0

    def addPlayer(self, player):
        if self.started():
            raise ValueError('Cannot add player to game in progress.')
        # okay to add players until started with first turn
        playerSequence = len(self.players)  # zero for first player
        lettersForPlayer = self.bagOfLetters.removeRandom(7) # init with 7 from game bag
        pState = PlayerState(self, player, playerSequence, lettersForPlayer)
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
        playerState = self.nextPlayer()
        if not playerState.player.identity() == user.identity():
            raise ValueError('next turn is for {}, not {}'.format(self.nextPlayer().player.name, user.name))
        return playerState

    def incrementTurn(self):
        self.turn = self.turn + 1
        if self.turn == len(self.players):
            self.turn = 0

    def playWord(self, user, x, y, across, word):
        self.addWordToBoard(self.getPlayerState(user), x, y, across, word)
        self.incrementTurn()
        self.consecutivePasses = 0

    def addWordToBoard(self, playerState, x, y, across, word):
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
            # print('removing {} from {}'.format(letter,playerState.letters.asString()))
            playerState.letters.remove(letter)  # raises error if not there
            self.setBoardContent(x,y,letter)
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


# # apply Repository pattern to encapsulate details of persistence
# class GameStateRepository():

#     # persist gameState and its parts
#     def register(gameState):
#         gameState.put()
#         for p in gameState.players:
#             p.put
#         return gameState

#     def id(gameState):
#         return gameState.key.urlsafe()

#     def findById(id):
#         return get_by_urlsafe(id, GameState)

# part of a gameState that describes player
# class PlayerState(ndb.Model):
class PlayerState():
    # game = ndb.KeyProperty(required=True, kind='Game')
    # player = ndb.KeyProperty(required=True, kind='User')
    # turnNumber = ndb.IntegerProperty(required=True)
    # letters = ndb.StringProperty(required=True)
    # score = ndb.IntegerProperty(required=True)

    def __init__(self, game, user, turnNumber, letters):
        self.game = game
        self.player = user
        self.turnNumber = turnNumber
        self.letters = letters
        self.score = 0


# # apply Repository pattern to encapsulate details of persistence
# class PlayerStateRepository():

#     # persist playerState
#     def register(playerState):
#         playerState.put()
#         return playerState

#     def id(playerState):
#         return playerState.key.urlsafe()

#     def findById(id):
#         return get_by_urlsafe(id, PlayerState)

# # Store count of letters held.
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

    def add(self, l):
        # print('LetterBag.add(l)')
        # print(l)
        # print(self.map[l])
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
        # print('removeRandom returning {}'.format(removed))
        return removed

    def removeByIndex(self, i):
        # print('removing item {}'.format(i))
        # print(self)
        l = self.letterAtIndex(i)
        # print('found letter {}'.format(l))
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
        # result = ''
        # for l in alphabet:
        #     result += '{}:{}, '.format(l, self.map[l])
        return self.map.__repr__()




