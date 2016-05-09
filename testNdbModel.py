import sys
sys.path.insert(1, '/usr/local/google_appengine')
sys.path.insert(1, '/usr/local/google_appengine/lib/yaml/lib')

import ww_models

def testNdbModel():
	# create instance, save, retrieve by key, check state
	game = Game.newGame(9,9)
	game.put()
	assert(game.key != null)
	retrieved = Game.query(Game.key == game.key).get()
	retrieved = ndb.getByKey(key)
	assert(retrieved != null)
	assert(retrieved.state == stored.state)

def testNewGame():
	assert urlSafeId != null
	game = getGame(urlSafeId) != null
	game.state == initial

def testMakeMove():
	assert game.state == moveMade

# def assert(condition):
# 	if not condition:
# 		raise ValueError("test failed: ")

# Architecture:
# - models defines persistent object types (okay to put all models in one module? : yes, until you want to share them independently, or if they become large with behavior)
# - app classes for any additional non-persitent types, application behavior, can delegate state to a persistent object.
# - web app platform call handler in webAppApi.py (target to Google app engine platform, endpoints-api)

testNdbModel()