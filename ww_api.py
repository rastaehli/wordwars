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
from ww_messages import NewGameForm, StringMessage, GameForm, MakeMoveForm, IdForm

NEW_GAME_REQUEST = endpoints.ResourceContainer()
START_GAME_REQUEST = endpoints.ResourceContainer()
GET_GAME_REQUEST = endpoints.ResourceContainer()
ADD_USER_TO_GAME_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(MakeMoveForm)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
ALL_USERS_REQUEST = endpoints.ResourceContainer()
USER_GAMES_REQUEST = endpoints.ResourceContainer()

@endpoints.api(name='word_wars_api', version='v1',
    allowed_client_ids=['wordwars-1311', endpoints.API_EXPLORER_CLIENT_ID])
    # grant access to ourselves and google's api_explorer also.
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

    def nextPlayerInfo(game):
        next = game.nextPlayer()
        return GameForm(
		    urlsafe_key = games.id(game),
		    board = game.board,
		    game_over = game.gameOver(),
		    user_turn = next.player.name,
		    user_letters = next.letters,
		    user_score = next.score)

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=IdForm,
                      path='game/new',
                      name='new_unstarted_game',
                      http_method='POST')
    def new_unstarted_game(self, request):
        """Creates new game with no users"""
        users = UserRepository()
        games = GameStateRepository()
        game = GameState.create()
        games.register(game)  # important to define "board" and other persistent variables returned below
        # TODO: JSON response
        next = game.nextPlayer()
        return IdForm(urlsafe_key = games.id(game))

    @endpoints.method(request_message=ALL_USERS_REQUEST,
    				response_message=StringMessage,
    				path='users',
    				name='get_all_users',
    				http_method='GET')
    def get_all_users(self, request):
    	users = UserRepository()
    	list = StringList()
    	for u in users.all():
	    	response.append(user.name)
    	return list

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{id}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = gameById(GameStateRepository(),request.id)
        return nextPlayerInfo(game)

    def gameById(games, id):
    	game = games.findById(id)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        return game

    def userByName(users, name):
    	user = users.findByName(name)
        if not user:
            raise endpoints.NotFoundException('User {} not found!'.format(name))
        return user

    @endpoints.method(request_message=ADD_USER_TO_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{id}/add_user',
                      name='add_user',
                      http_method='PUT')
    def add_user(self, request):
        games = GameStateRepository()
        game = gameById(games,request.id)
        users = UserRepository()
        user = userByName(users, request.user_name)
        game.addPlayer(user)
        games.update(game)
        return StringMessage(message='User {} added!'.format(request.user_name))

    @endpoints.method(request_message=START_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{id}',
                      name='start_game',
                      http_method='PUT')
    def start_game(self, request):
        games = GameStateRepository()
        game = gameById(games,request.id)
        game.start()
        games.update(game)
        return nextPlayerInfo(game)

    def scoreInfo(before, total):
        playScore = total - before
        if playScore > 5:
            return StringMessage(message='Good job!  You added {} for a total score of {}.'.format(playScore, total))
        else:
            return StringMessage(message='You added {} for a total score of {}.'.format(playScore, total))

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=StringMessage,
                      path='game/{id}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        games = GameStateRepository()
    	users = UserRepository()
        game = gameById(games,request.id)
        user = users.getByName(request.user_name)
        if game.gameOver():
            return StringMessage(message='Game already over!')
        scoreBefore = game.scoreForUser(user)
        game.playWord(user, request.x, request.y, request.across, request.word)
        scoreAfter = game.scoreForUser(user)
        games.update(game)
        return scoreInfo(scoreBefore, scoreAfter)


api = endpoints.api_server([WordWarsApi])
