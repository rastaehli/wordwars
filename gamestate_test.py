from ww_models import User, GameState, PlayerState, LetterBag
from ww_print_view import PrintView

class Test():

  def assertTrue(self, booleanExpression, description):
    if not booleanExpression:
      raise ValueError("{} is not True".format(description))
    else:
      print('passed test: {}'.format(description))

  def testShortGame(self):
    joe = User.create('joe', 'joe@gmail.com')
    steve = User.create('steve', 'steve@gmail.com')
    v = PrintView()

    game = GameState.create()
    game.addPlayer(joe)
    game.addPlayer(steve)

    for p in game.players:
      p.bag = LetterBag.fromString('catgegae')
    game.start()
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

t = Test().testShortGame()
