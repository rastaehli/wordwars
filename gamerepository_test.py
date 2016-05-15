from ww_models import User, GameState, GameStateRepository, PlayerState, LetterBag
from ww_print_view import PrintView
import utils

import unittest

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed


# this tests that GameState can be saved, retrieved via GameStateRepository
class Test():

  def setUp(self):
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    # Then activate the testbed, which prepares the service stubs for use.
    self.testbed.activate()
    # Next, declare which service stubs you want to use.
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    # Clear ndb's in-context cache between tests.
    # This prevents data from leaking between tests.
    # Alternatively, you could disable caching by
    # using ndb.get_context().set_cache_policy(False)
    ndb.get_context().clear_cache()

  def tearDown(self):
    self.testbed.deactivate()
        
  def assertTrue(self, booleanExpression, description):
    if not booleanExpression:
      raise ValueError("{} is not True".format(description))
    else:
      print('passed test: {}'.format(description))

  def testShortGame(self):
    self.setUp()

    repository = GameStateRepository()

    joe = User.create('joe', 'joe@gmail.com')
    steve = User.create('steve', 'steve@gmail.com')
    v = PrintView()

    users = [joe, steve]

    game = GameState.create(users)
    for p in game.players:
      p.bag = LetterBag.fromString('catgegae')
    game.start()
    self.assertTrue(game.leader().score == 0, "leader score==0")
    
    repository.register(game)
    id = repository.id(game)
    self.assertTrue(id != None, 'registering with repository set game id')

    game2 = repository.findById(id)

    self.assertTrue(game2.leader().score == 0, "leader score==0")

    game2.playWord(joe,0,0,True,'cat')
    repository.update(game2)

    game3 = repository.findById(id)     # same id retrieves game2 update
    self.assertTrue(game3.leader().score == 4, "same id retrieves update")

    self.tearDown()

t = Test().testShortGame()