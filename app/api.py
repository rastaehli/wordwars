"""ww_api.py - Create RESTful API endpoints (URLs) for interacting
with the WordWars web app.  This API imports and delegates to the model
objects that implement the game logic, including repository objects:
the Repository pattern is used to separate details of the persistence
service from the application logic."""
# -*- coding: utf-8 -*-`


import logging
import endpoints
from protorpc import remote, messages
# from google.appengine.api import memcache
# from google.appengine.api import taskqueue

from models import User, GameState
from repositories import GameStateRepository, UserRepository, PlayerStateRepository
from print_view import PrintView
from utils import get_by_urlsafe
from messages import StringMessage, StringList, GameForm, MakeMoveForm, IdForm


@endpoints.api(name='api', version='v1',
    # grant access to ourselves and google's api_explorer also.
    allowed_client_ids=['wordwars-1311', endpoints.API_EXPLORER_CLIENT_ID])
class WordWarsApi(remote.Service):
    """Google endpoints API for WordWars game service."""
    def __init__(self):
        self.games = GameStateRepository()
        self.users = UserRepository()

    @endpoints.method(request_message=endpoints.ResourceContainer( name=messages.StringField(1), email=messages.StringField(2) ),
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

    @endpoints.method(request_message=endpoints.ResourceContainer(user_name=messages.StringField(1)),
                        response_message=StringList,
                        path='user/{user_name}/games',
                        name='get_user_games',
                        http_method='GET')
    def get_user_games(self, request):
        """Return id values for all games where this user is a player."""
        user = self.userByName(request.user_name)
        idList = []
        for p in PlayerStateRepository().findByUser(user):
            idList.append( self.games.id( p.game ))
        gameIds = StringList()
        gameIds.strings = idList
        return gameIds

    @endpoints.method(request_message=endpoints.ResourceContainer(gameid=messages.StringField(1)),
                      response_message=StringMessage,
                      path='game/{gameid}',
                      name='cancel_game',
                      http_method='POST')
    def cancel_game(self, request):
        """Mark game as cancelled, with no winner."""
        game = self.gameById(request.gameid)
        game.cancel()
        return StringMessage('Game is cancelled.')

    def gameFormFrom(self, game):
        """Return game state, including identity of whose turn is next."""
        next = game.nextPlayer()
        if next == None:
            return GameForm(
                urlsafe_key = self.gameDb().id(game),
                board = game.board,
                status = game.mode,
                user_turn = 'None',
                user_letters = '',
                user_score = 0)
        else:
            return GameForm(
                urlsafe_key = self.gameDb().id(game),
                board = game.board,
                status = game.mode,
                user_turn = next.player.name,
                user_letters = next.letters,
                user_score = next.score)

    def gameDb(self):
        """Set reference to repository of persistent game state."""
        if not self.games:
            self.games = GameStateRepository()
        return self.games

    def userDb(self):
        """Set reference to repository of persistent user objects."""
        if not self.users:
            self.users = UserRepository()
        return self.users

    @endpoints.method(request_message=endpoints.ResourceContainer(),
                      response_message=IdForm,
                      path='game/new',
                      name='new_unstarted_game',
                      http_method='POST')
    def new_unstarted_game(self, request):
        """Create a new game with no users and return its ID."""
        game = GameState.create()
        self.gameDb().register(game)  # important to define "board" and other persistent variables returned below
        # TODO: JSON response
        next = game.nextPlayer()
        return IdForm(urlsafe_key=self.gameDb().id(game))

    @endpoints.method(request_message=endpoints.ResourceContainer(),
                      response_message=StringList,
                      path='users',
                      name='get_all_users',
                      http_method='GET')
    def get_all_users(self, request):
        """Return list of all known users."""
        nameList = StringList()
        for u in self.userDb().all():
            nameList.append(u.name)
        return nameList

    @endpoints.method(request_message=endpoints.ResourceContainer(gameid=messages.StringField(1)),
                      response_message=GameForm,
                      path='game/{gameid}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return game state for requested ID."""
        game = self.gameById(request.gameid)
        return self.gameFormFrom(game)

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

    @endpoints.method(request_message=endpoints.ResourceContainer( gameid=messages.StringField(1), name=messages.StringField(2)),
                      response_message=StringMessage,
                      path='game/{gameid}/add_user',
                      name='add_user',
                      http_method='PUT')
    def add_user(self, request):
        """Add user to requested game."""
        game = self.gameById(request.gameid)
        user = self.userByName(request.name)
        game.addPlayer(user)
        self.gameDb().update(game)
        return StringMessage(message='User {} added!'.format(request.name))

    @endpoints.method(request_message=endpoints.ResourceContainer( gameid=messages.StringField(1) ),
                      response_message=GameForm,
                      path='game/{gameid}/start',
                      name='start_game',
                      http_method='PUT')
    def start_game(self, request):
        """Start requested game (no more players may be added)."""
        game = self.gameById(request.gameid)
        game.start()
        self.gameDb().update(game)
        return self.gameFormFrom(game)

    def scoreInfo(self, before, total):
        playScore = total - before
        if playScore > 5:
            return StringMessage(message='Good job!  You added {} for a total score of {}.'.format(playScore, total))
        else:
            return StringMessage(message='You added {} for a total score of {}.'.format(playScore, total))

    @endpoints.method(request_message=endpoints.ResourceContainer( MakeMoveForm, gameid=messages.StringField(1) ),
                      response_message=StringMessage,
                      path='game/{gameid}/move',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Add requested word to the board at x,y, across or not."""
        game = self.gameById(request.gameid)
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
