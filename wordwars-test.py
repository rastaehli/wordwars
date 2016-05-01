import wordwars

class Test():

  def assertTrue(self, booleanExpression, description):
    if not booleanExpression:
      raise ValueError("{} is not True".format(description))
    else:
      print('passed test: {}'.format(description))

  def testShortGame(self):
    w = wordwars.WordWars()
    users = ['rich','jan']

    game = wordwars.Game(6, 6, users)
    game.play('rich',0,0,True,'cat')
    game.play('jan',0,0,False,'cage')
    game.play('rich',0,2,True,'gag')
    game.play('jan',2,2,False,'gate')
    game.skipTurn('rich')
    game.skipTurn('jan')
    self.assertTrue(game.scores['jan'] == 8, "scores['jan']==8")
    self.assertTrue(game.scores['jan'] > game.scores['rich'], "jan is the winner")

t = Test().testShortGame()