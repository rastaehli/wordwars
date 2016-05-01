ww-models.py


"""ww-models.py - This file contains the class definitions for the Datastore
entities used by Word Wars. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""
    players = ndb.KeyProperty(required=True, kind='PlayerState')	#TODO: make this a list of player state
    bagOfLetters = ndb.StringProperty(required=True)
    boardWidth = ndb.IntegerProperty(required=True)
    boardHeight = ndb.IntegerProperty(required=True)
    boardContent = ndb.StringProperty(required=True)
    playerCount = ndb.IntegerProperty(required=True)
    consecutivePasses = ndb.IntegerProperty(required=True)
    created = ndb.StringProperty(required=True)


class PlayerState(ndb.Model):
	game = ndb.KeyProperty(required=True, kind='Game')
	player = ndb.KeyProperty(required=True, kind='User')
	turnNumber = ndb.IntegerProperty(required=True)
	letters = ndb.StringProperty(required=True)
	score = ndb.IntegerProperty(required=True)
