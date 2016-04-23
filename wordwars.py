#!/usr/bin/env python
import random
import copy

"""wordwars.py - responsible for WordWars game behavior, support for multi-user access to multiple games."""
class Game(object):

    letterValue = {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 
        'h': 1, 'i': 1, 'j': 1, 'k': 1, 'l': 1, 'm': 1, 'n': 1, 'o': 1, 'p': 1, 
        'q': 1, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 1, 'w': 1, 'x': 1, 'y': 1, 'z': 1}

    def __init__(self, width, height, users):
        if len(users) < 1:
            raise ValueError("can't have a game with less than one player")
        self.players = users
        self.letters = {}
        for p in self.players:
            self.letters[p] = self.countLetters(['c', 'a', 't', 'e', 'g', 'b', 'q', 'a', 't', 'e'])
        self.width = width
        self.height = height
        # initialize board with all underscore characters
        self.board = [['_' for x in range(width)] for y in range(height)] 
        self.turn = 0   # first players turn
        self.passed = {}
        for p in self.players:
            self.passed[p] = False
        self.scores = {}
        for p in self.players:
            self.scores[p] = 0
        #self.id = random.randint(0, 32767)
        self.id = 1

    def getId(self):
        return self.id

    def whoseTurn(self):
        return self.players[self.turn]

    def validatePosition(self, x, y):
        problem = None
        if x < 0 or y < 0:
            problem = "less than zero"
        if x >= self.width or y >= self.height:
            problem = "too large"
        if problem != None:
            raise ValueError('index is '+problem)
        return True

    def endX(self, x, across, word):
        if across:
            return x + len(word) - 1
        else:
            return x

    def endY(self, y, across, word):
        if not across: # must go down
            return y + len(word) - 1
        else:
            return y

    def wordFits(self, x, y, across, word):
        self.validatePosition(x,y)
        xEnd = self.endX(x, across, word)
        yEnd = self.endY(y, across, word)
        if (self.endX(x, across, word) > self.width) or (self.endY(y, across, word) > self.height):
            return False
        return True

    def lettersNeeded(self, x, y, across, word):
        needed = []     # add character from word for each empty board space
        for i in range(len(word)):
            if across:
                if self.board[y][x+i] == '_':
                    needed.append(word[i])
            else:
                if self.board[y+i][x] == '_':
                    needed.append(word[i]) 
        return needed

    def countLetters(self, list):
        bag = {}
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            bag[letter] = 0
        for letter in list:
            bag[letter] = bag[letter] + 1
        return bag

    def playerHas(self, player, lettersToPlay):
        bag = copy.deepcopy(self.letters[player])
        for letter in lettersToPlay:
            if bag[letter] <= 0:
                return False
            else:
                bag[letter] = bag[letter] - 1
        return True

    def play(self, player, x, y, across, word):
        bag = self.letters[player]
        score = 0
        nextX = x
        nextY = y
        for i in range(len(word)):
            letter = word[i]
            if across:
                nextX = x + i
            else:
                nextY = y + i
            score = score + self.playLetter(bag, nextX, nextY, letter)
        self.turn = self.turn + 1
        if self.turn == len(self.players):
            self.turn = 0
        self.passed[player] = False
        self.scores[player] = self.scores[player] + score
        return score

    def skipTurn(self, player):
        self.turn = self.turn + 1
        if self.turn == len(self.players):
            self.turn = 0
        self.passed[player] = True

    def playLetter(self, bag, x, y, letter):
        score = 0
        if self.board[y][x] == '_':
            count = 0
            count = bag[letter]
            count = count - 1
            bag[letter] = bag[letter] - 1   # remove letter from player's bag
            score = self.letterValue[letter]     # accumulate score
            self.board[y][x] = letter       # update board
        else:
            score = self.letterValue[letter]
        return score


games = {}

class WordWars():
    def newGame(self, users):
        """create a new game for the given list of users"""
        game = Game(6, 6, users)
        id = game.getId()
        games[id] = game
        return id
    
    def direction(self, across):
        if across:
            return 'across'
        else:
            return 'down'

    def playWord(self, id, user, x, y, across, word):
        game = games[id]
        if game.whoseTurn() != user:
            raise ValueError('not your turn: {}'.format(user))
        if not game.wordFits(x, y, across, word):
            raise ValueError('{} does not fit at ({},{}) running {}.'.format(word, x, y, self.direction(across)))
        lettersToPlay = game.lettersNeeded(x, y, across, word)
        if not game.playerHas(user, lettersToPlay):
            raise ValueError('{} does not have needed letters: {}.'.format(user, lettersToPlay))
        score = game.play(user, x, y, across, word)
        self.showBoard(id)
        return 'player {} gets {} points for the word {}'.format(user, score, word)

    def skipTurn(self, id, user):
        game = games[id]
        if game.whoseTurn() != user:
            raise ValueError('not your turn: {}'.format(user))
        game.skipTurn(user)
        for player in game.players:
            if not game.passed[player]:
                return 'player {} passed.'.format(user)
        # if line above not executed, all players passed.  Game is over!
        results = game.scores
        winner = None
        highScore = 0
        for player in game.players:
            if results[player] > highScore:
                highScore = results[player]
                winner = player
        return 'game over!  winner {} has score of {}.'.format(winner, highScore)

    def showBoard(self, id):
        for row in games[id].board:
            print row






