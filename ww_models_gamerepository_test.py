from ww_models import User, GameState, GameStateRepository, PlayerState, LetterBag
from ww_print_view import PrintView

# this tests that GameState can be saved, retrieved via GameStateRepository
class Test():

  def assertTrue(self, booleanExpression, description):
    if not booleanExpression:
      raise ValueError("{} is not True".format(description))
    else:
      print('passed test: {}'.format(description))

  def testShortGame(self):
    repository = GameStateRepository()

    joe = User.create('joe', 'joe@gmail.com')
    steve = User.create('steve', 'steve@gmail.com')
    v = PrintView()

    users = [joe, steve]

    game = GameState.create(users)
    for p in game.players:
      p.letters = LetterBag.fromString('catgegae')
    game.start()
    self.assertTrue(game.leader().score == 0, "leader score==0")
    
    repository.register(game)
    id = repisitory.id(game)
    self.assertTrue(id != None, 'registering with repository set game id')

    game2 = repository.findById(id)
    self.assertTrue(game2.leader().score == 0, "leader score==0")

    game2.playWord(joe,0,0,True,'cat')
    repository.update(game2)

    game3 = repository.findById(id)     # same id retrieves game2 update
    self.assertTrue(game3.leader().score == 5, "same id retrieves update")


t = Test().testShortGame()