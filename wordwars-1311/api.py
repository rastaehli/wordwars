"""ww_api.py - Create RESTful API endpoints (URLs) for interacting
with the WordWars web app.  This API imports and delegates to the model
objects that implement the game logic, including repository objects:
the Repository pattern is used to separate details of the persistence
service from the application logic."""
# -*- coding: utf-8 -*-`


import re
import logging
import endpoints
from protorpc import (
    remote,
    messages,
)
from models import (
    User,
    GameState,
    Move,
)
from repositories import (
    GameStateRepository,
    UserRepository,
    PlayerStateRepository,
    MoveRepository,
)
from print_view import PrintView
from utils import get_by_urlsafe
from messages import (
    StringMessage,
    StringList,
    GameForm,
    MakeMoveForm,
    IdForm,
    WinLossRecord,
    RankingList,
    MoveList,
    MoveRecord
)

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

GAME_ID_REQUEST = endpoints.ResourceContainer(gameid=messages.StringField(1))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm, gameid=messages.StringField(1))
NEW_USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1), email=messages.StringField(2))
USERNAME_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1))
ADD_USER_REQUEST = endpoints.ResourceContainer(
    gameid=messages.StringField(1), user_name=messages.StringField(2))
PLAIN_REQUEST = endpoints.ResourceContainer()


@endpoints.api(
    name='wordwars',
    version='v1',
    # grant access to ourselves and google's api_explorer also.
    allowed_client_ids=['wordwars-1311', endpoints.API_EXPLORER_CLIENT_ID])
class WordWarsApi(remote.Service):
    """Google endpoints API for WordWars game service."""

    def __init__(self):
        """initialize objects available to all api endpoint methods"""
        self.games = GameStateRepository()
        self.users = UserRepository()
        self.moves = MoveRepository()

    @endpoints.method(request_message=NEW_USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if self.users.findByName(request.user_name):
            raise endpoints.ConflictException(
                'A User with that name already exists!')
        if not EMAIL_REGEX.match(request.email):
            raise endpoints.BadRequestException(
                'Email address is not valid: {}'.format(request.email))
        user = User.create(request.user_name, request.email)
        self.users.register(user)
        return StringMessage(message='User {} created!'.format(request.user_name))

    @endpoints.method(request_message=USERNAME_REQUEST,
                      response_message=StringList,
                      path='user/{user_name}/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return id values for all games where this user is a player."""
        user = self.userByName(request.user_name)
        idList = []
        for p in PlayerStateRepository().findByUser(user):
            idList.append(self.games.id(p.game))
        gameIds = StringList()
        gameIds.strings = idList
        return gameIds

    @endpoints.method(request_message=PLAIN_REQUEST,
                      response_message=IdForm,
                      path='game/new',
                      name='new_unstarted_game',
                      http_method='POST')
    def new_unstarted_game(self, request):
        """Create a new game with no users and return its ID."""
        game = GameState.create()
        # "register" on next line sets "board" and other persistent variables
        self.games.register(game)
        # TODO: JSON response
        next = game.nextPlayer()
        return IdForm(urlsafe_key=self.games.id(game))

    @endpoints.method(request_message=GAME_ID_REQUEST,
                      response_message=GameForm,
                      path='game/{gameid}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return game state for requested ID."""
        game = self.gameById(request.gameid)
        return self.gameFormFrom(game, '')

    @endpoints.method(request_message=ADD_USER_REQUEST,
                      response_message=StringMessage,
                      path='game/{gameid}/add_user',
                      name='add_user',
                      http_method='PUT')
    def add_user(self, request):
        """Add user to requested game."""
        game = self.gameById(request.gameid)
        if game.started():
            raise endpoints.BadRequestException(
                'Can''t add user after game is started.')
        user = self.userByName(request.user_name)
        game.addPlayer(user)
        self.games.update(game)
        return StringMessage(message='User {} added!'.format(request.user_name))

    @endpoints.method(request_message=GAME_ID_REQUEST,
                      response_message=GameForm,
                      path='game/{gameid}/start',
                      name='start_game',
                      http_method='PUT')
    def start_game(self, request):
        """Start requested game (no more players may be added)."""
        game = self.gameById(request.gameid)
        if len(game.players) <= 0:
            raise endpoints.BadRequestException(
                'Must add players before starting.')
        self.validateNotOver(game)
        self.validateNotCancelled(game)
        game.start()
        self.games.update(game)
        return self.gameFormFrom(game, '')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{gameid}/move',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Add requested word to the board at x,y, across or not."""
        game = self.gameById(request.gameid)
        self.validateStarted(game)
        self.validateNotOver(game)
        self.validateNotCancelled(game)
        if game.nextPlayer().player.name != request.user_name:
            raise endpoints.BadRequestException(
                'Not turn yet for {}'.format(request.user_name))
        user = self.users.findByName(request.user_name)
        word = request.word
        across = request.across
        x = request.x
        y = request.y
        scoreBefore = game.scoreForUser(user)
        if len(request.word) <= 0:
            game.skipTurn(user)
        else:
            try:
                game.playWord(user, x, y, across, word)
            except Exception, e:
                raise endpoints.BadRequestException(
                    'Illegal move: {}'.format(e.message))
        scoreAfter = game.scoreForUser(user)
        playScore = scoreAfter - scoreBefore
        self.games.update(game)
        # keep history of moves
        self.moves.register(
            Move.create(game, user, word, across, x, y, playScore))
        return self.gameFormFrom(
            game, self.lastPlayDescription(scoreBefore, scoreAfter))

    @endpoints.method(request_message=PLAIN_REQUEST,
                      response_message=StringList,
                      path='user/all',
                      name='get_all_users',
                      http_method='GET')
    def get_all_users(self, request):
        """Return list of all known users."""
        nameList = []
        for u in self.users.all():
            nameList.append(u.name)
        return StringList(strings=nameList)

    @endpoints.method(request_message=GAME_ID_REQUEST,
                      response_message=StringMessage,
                      path='game/{gameid}/cancel',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Mark game as cancelled, with no winner."""
        game = self.gameById(request.gameid)
        game.cancel()
        self.games.update(game)
        return StringMessage(message='Game is cancelled.')

    @endpoints.method(request_message=PLAIN_REQUEST,
                      response_message=RankingList,
                      path='user/rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return sorted list of the win/loss ratio by player."""
        wins = {}
        losses = {}
        for user in self.users.all():
            wins[user.name] = 0
            losses[user.name] = 0
        for game in self.games.allCompleted():
            winner = game.leader().player
            wins[winner.name] += 1
            for p in game.players:
                if p.player != winner:
                    losses[p.player.name] += 1
        records = []
        for userName in wins:
            records.append(WinLossRecord(
                name=userName,
                wins=wins[userName],
                losses=losses[userName]))
        return RankingList(
            # sort highest ratio first
            rankings=sorted(
                records,
                key=lambda record: record.wins/(1+record.losses),
                reverse=True))

    @endpoints.method(request_message=GAME_ID_REQUEST,
                      response_message=MoveList,
                      path='game/{gameid}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return sorted list of the win/loss ratio by player."""
        game = self.gameById(request.gameid)
        moveList = []
        for move in self.moves.historyForGame(game):
            moveList.append(MoveRecord(
                user_name=move.user.name,
                x=move.x,
                y=move.y,
                across=move.across,
                word=move.word,
                moveScore=move.moveScore,
                time=move.time))
        # return sorted by time
        return MoveList(
            moves=sorted(moveList, key=lambda move: move.time))

    # The methods below provide common utility functions.

    def gameFormFrom(self, game, lastPlay):
        """Return game state, including identity of whose turn is next."""
        next = game.nextPlayer()
        if next is None:
            return GameForm(
                gameid=self.games.id(game),
                board=game.board,
                status=game.mode,
                user_turn='None',
                user_letters='',
                user_score=0,
                y0=game.board[0:10],
                y1=game.board[10:20],
                y2=game.board[20:30],
                y3=game.board[30:40],
                y4=game.board[40:50],
                y5=game.board[50:60],
                y6=game.board[60:70],
                y7=game.board[70:80],
                y8=game.board[80:90],
                y9=game.board[90:100]
                )
        else:
            return GameForm(
                gameid=self.games.id(game),
                board=game.board,
                status=game.mode + ":  " + lastPlay,
                user_turn=next.player.name,
                user_letters=next.bag.asString(),
                user_score=next.score,
                y0=game.board[0:10],
                y1=game.board[10:20],
                y2=game.board[20:30],
                y3=game.board[30:40],
                y4=game.board[40:50],
                y5=game.board[50:60],
                y6=game.board[60:70],
                y7=game.board[70:80],
                y8=game.board[80:90],
                y9=game.board[90:100]
                )

    def gameById(self, id):
        game = self.games.findById(id)
        if not game:
            raise endpoints.NotFoundException(
                'Game not found for id: {}'.format(id))
        return game

    def userByName(self, name):
        user = self.users.findByName(name)
        if not user:
            raise endpoints.NotFoundException(
                'User {} not found!'.format(name))
        return user

    def lastPlayDescription(self, before, total):
        added = total - before
        if total <= 0:
            lastPlay = ''
        else:
            lastPlay = 'You added {} for a total score of {}.'.format(added, total)
        if added > 5:
            lastPlay = 'Good job!  '+lastPlay
        return lastPlay

    def validateStarted(self, game):
        if not game.started():
            raise endpoints.BadRequestException('Game is already over.')

    def validateNotOver(self, game):
        if game.gameOver():
            raise endpoints.BadRequestException('Game is already over.')

    def validateNotCancelled(self, game):
        if game.cancelled():
            raise endpoints.BadRequestException('Game is already cancelled.')


api = endpoints.api_server([WordWarsApi])
