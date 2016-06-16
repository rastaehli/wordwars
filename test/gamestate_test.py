import sys
sys.path.append('wordwars-1311')

from models import User, GameState, PlayerState, LetterBag
from print_view import PrintView

class Test():
  joe = User.create('joe', 'joe@gmail.com')
  steve = User.create('steve', 'steve@gmail.com')
  game = GameState.create()
  game.addPlayer(joe)
  game.addPlayer(steve)
  game.start()

  def assertTrue(self, booleanExpression, description):
    if not booleanExpression:
      raise ValueError("{} is not True".format(description))
    else:
      print('passed test: {}'.format(description))

  def testShortGame(self):
    joe = self.joe
    steve = self.steve
    v = PrintView()
    game = self.game

    for p in game.players:
      p.bag = LetterBag.fromString('catgegae')
    self.assertTrue(game.leader().score == 0, "leader score==0")

    game.playWord(joe,0,0,True,'cat')
    game.playWord(steve,0,0,False,'cage')
    game.playWord(joe,0,2,True,'gag')
    game.playWord(steve,2,2,False,'gate')
    game.skipTurn(joe)
    game.skipTurn(steve)
    v.showGameState(game)
    self.assertTrue(game.gameOver(), "game is over")
    self.assertTrue(game.leader().player.name == 'steve', "steve is the winner")
    self.assertTrue(game.leader().score == 13, "winner score is 13")

  def testScoreOnlyWhenAddingLetters(self):
    joe = self.joe
    steve = self.steve
    v = PrintView()
    game = self.game

    for p in game.players:
      p.bag = LetterBag.fromString('catgegae')
    self.assertTrue(game.leader().score == 0, "leader score==0")

    game.playWord(joe,0,0,True,'cat')
    self.assertTrue(game.scoreForUser(joe) == 4, "score for cat is 4")
    try:
        game.playWord(steve,0,0,True,'cat')
        self.assertTrue(False, 'playing word already played should raise exception')
    except ValueError, e:
        self.assertTrue(True, 'playing word already played raised error: {}'.format(e))
    game.playWord(steve,0,0,False,'cage')
    self.assertTrue(game.scoreForUser(steve) == 7, "score for adding cage (reusing the c) is 7")

t = Test().testScoreOnlyWhenAddingLetters()
