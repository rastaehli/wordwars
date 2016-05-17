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

from models import User, GameState
from repositories import GameStateRepository, UserRepository, PlayerStateRepository
from print_view import PrintView
from utils import get_by_urlsafe
from messages import NewGameForm, StringMessage, GameForm, MakeMoveForm, IdForm

NEW_GAME_REQUEST = endpoints.ResourceContainer()
START_GAME_REQUEST = endpoints.ResourceContainer( id=messages.StringField(1) )
GET_GAME_REQUEST = endpoints.ResourceContainer( id=messages.StringField(1) )
ADD_USER_TO_GAME_REQUEST = endpoints.ResourceContainer( id=messages.StringField(1), user_name=messages.StringField(2))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer( MakeMoveForm, id=messages.StringField(1) )
USER_REQUEST = endpoints.ResourceContainer( user_name=messages.StringField(1), email=messages.StringField(2) )
ALL_USERS_REQUEST = endpoints.ResourceContainer()
USER_GAMES_REQUEST = endpoints.ResourceContainer()

@endpoints.api(name='word_wars_api', version='v1',
    allowed_client_ids=['wordwars-1311', endpoints.API_EXPLORER_CLIENT_ID])
    # grant access to ourselves and google's api_explorer also.
class WordWarsApi(remote.Service):
    def __init__(self):
        self.games = GameStateRepository()
        self.users = UserRepository()

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if self.userDb().findByName(request.user_name):
            raise endpoints.ConflictException('A User with that name already exists!')
        user = User.create(request.user_name, request.email)
        self.userDb().register(user)
        return StringMessage(message='User {} created!'.format(request.user_name))

    # def get_user_games(self, request):
    #     """return all games where this user is a player"""
    #     user = self.userByName(request.user_name)
    #     pList = PlayerStateRepository().

    def nextPlayerInfo(self, game):
        next = game.nextPlayer()
        if next:
          return GameForm(
            urlsafe_key = self.gameDb().id(game),
            board = game.board,
            game_over = game.gameOver(),
            user_turn = next.player.name,
            user_letters = next.letters,
            user_score = next.score)
        else:
          return GameForm(
            urlsafe_key = self.gameDb().id(game),
            board = game.board,
            game_over = game.gameOver(),
            user_turn = 'None',
            user_letters = '',
            user_score = 0)

    def gameDb(self):
      if not self.games:
        self.games = GameStateRepository()
      return self.games
      
    def userDb(self):
      if not self.users:
        self.users = UserRepository()
      return self.users
      
    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=IdForm,
                      path='game/new',
                      name='new_unstarted_game',
                      http_method='POST')
    def new_unstarted_game(self, request):
        """Creates new game with no users"""
        game = GameState.create()
        self.gameDb().register(game)  # important to define "board" and other persistent variables returned below
        # TODO: JSON response
        next = game.nextPlayer()
        return IdForm(urlsafe_key = self.gameDb().id(game))

    @endpoints.method(request_message=ALL_USERS_REQUEST,
    				response_message=StringMessage,
    				path='users',
    				name='get_all_users',
    				http_method='GET')
    def get_all_users(self, request):
    	nameList = []
    	for u in self.userDb().all():
	    	nameList.append(u.name)
    	return StringMessage(message=', '.join(nameList))

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{id}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = self.gameById(request.id)
        return self.nextPlayerInfo(game)

    def gameById(self, id):
    	game = self.gameDb().findById(id)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        return game

    def userByName(self, name):
    	user = self.userDb().findByName(name)
        if not user:
            raise endpoints.NotFoundException('User {} not found!'.format(name))
        return user

    @endpoints.method(request_message=ADD_USER_TO_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{id}/add_user',
                      name='add_user',
                      http_method='PUT')
    def add_user(self, request):
        game = self.gameById(request.id)
        user = self.userByName(request.user_name)
        game.addPlayer(user)
        self.gameDb().update(game)
        return StringMessage(message='User {} added!'.format(request.user_name))

    @endpoints.method(request_message=START_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{id}/start',
                      name='start_game',
                      http_method='PUT')
    def start_game(self, request):
        game = self.gameById(request.id)
        game.start()
        self.gameDb().update(game)
        return self.nextPlayerInfo(game)

    def scoreInfo(self, before, total):
        playScore = total - before
        if playScore > 5:
            return StringMessage(message='Good job!  You added {} for a total score of {}.'.format(playScore, total))
        else:
            return StringMessage(message='You added {} for a total score of {}.'.format(playScore, total))

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=StringMessage,
                      path='game/{id}/move',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        game = self.gameById(request.id)
        user = self.userDb().findByName(request.user_name)
        if game.gameOver():
            return StringMessage(message='Game already over!')
        scoreBefore = game.scoreForUser(user)
        if len(request.word) <= 0:
          game.skipTurn(user)
        else:
          game.playWord(user, request.x, request.y, request.across, request.word)
        scoreAfter = game.scoreForUser(user)
        self.gameDb().update(game)
        return self.scoreInfo(scoreBefore, scoreAfter)


api = endpoints.api_server([WordWarsApi])
