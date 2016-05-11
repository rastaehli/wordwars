# -*- coding: utf-8 -*-`
"""ww_api.py - Create RESTful API endpoints (URLs) for interacting
with the WordWars web app.  This API imports and delegates to the model
objects that implement the game logic, including repository objects:
the Repository pattern is used to separate details of the persistence
service from the application logic."""


import logging
import endpoints
from protorpc import remote, messages
# from google.appengine.api import memcache
# from google.appengine.api import taskqueue

from ww_models import User, GameState, GameStateRepository, UserRepository
from ww_print_view import PrintView
from utils import get_by_urlsafe
from ww_messages import NewGameForm, StringMessage, GameForm, MakeMoveForm

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
         urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
     MakeMoveForm,
     urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

# MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='word_wars', version='v1')
class WordWarsApi(remote.Service):

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
    	users = UserRepository()
        """Create a User. Requires a unique username"""
        if users.findByName(request.user_name):
            raise endpoints.ConflictException('A User with that name already exists!')
        user = User.create(request.user_name, request.email)
        users.register(user)
        return StringMessage(message='User {} created!'.format(request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        users = UserRepository()
        games = GameStateRepository()
        user = users.findByName(request.user_name)
        user2 = users.findByName(request.user2_name)
        if not user:
            raise endpoints.NotFoundException(
                    'A User with name {} does not exist!'.format(user))
        if not user2:
            raise endpoints.NotFoundException(
                    'A User with name {} does not exist!'.format(user2))
        game = GameState.create([user, user2])
        game.start()
        games.register(game)  # important to define "board" and other persistent variables returned below
        # TODO: JSON response
        next = game.nextPlayer()
        return GameForm(
		    urlsafe_key = games.id(game),
		    board = game.board,
		    game_over = game.gameOver(),
		    user_turn = next.player.name,
		    user_letters = next.letters,
		    user_score = next.score)

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        games = GameStateRepository()
        view = PrintView()
        """Return the current game state."""
        game = games.findById(request.urlsafe_game_key)
        if game:
        	next = game.nextPlayer()
	        return GameForm(
			    urlsafe_key = games.id(game),
			    board = game.board,
			    game_over = game.gameOver(),
			    user_turn = next.player.name,
			    user_letters = next.letters,
			    user_score = next.score)
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        games = GameStateRepository()
        view = PrintView()
    	users = UserRepository()
        """Return the current game state."""
        game = games.getById(request.urlsafe_game_key)
        user = users.getByName(request.user_name)
        if game.gameOver():
            return StringMessage(message='Game already over!')
        scoreBefore = game.scoreForUser(user)
        game.playWord(user, request.x, request.y, request.across, request.word)
        scoreAfter = game.scoreForUser(user)
        games.update(game)
        # TODO: JSON response
        return StringMessage(message='you added {} points!'.format(scoreAfter - scoreBefore))


api = endpoints.api_server([WordWarsApi])
