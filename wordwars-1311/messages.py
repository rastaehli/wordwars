"""ww_messages.py defines google app engine Message subclasses
for the WordWars webapp api requests and responses."""

from protorpc import messages
from protorpc.message_types import DateTimeField


class StringMessage(messages.Message):
    """Outbound (single) string message."""
    message = messages.StringField(1, required=True)


class StringList(messages.Message):
    """Outbound list of string messages."""
    strings = messages.StringField(1, repeated=True)


class GameForm(messages.Message):
    """Outbound description of game state."""
    gameid = messages.StringField(1, required=True)
    board = messages.StringField(2, required=True)
    status = messages.StringField(3, required=True)
    user_turn = messages.StringField(4, required=True)
    user_letters = messages.StringField(5, required=True)
    user_score = messages.IntegerField(6, required=True)
    y0 = messages.StringField(7, required=True)
    y1 = messages.StringField(8, required=True)
    y2 = messages.StringField(9, required=True)
    y3 = messages.StringField(10, required=True)
    y4 = messages.StringField(11, required=True)
    y5 = messages.StringField(12, required=True)
    y6 = messages.StringField(13, required=True)
    y7 = messages.StringField(14, required=True)
    y8 = messages.StringField(15, required=True)
    y9 = messages.StringField(16, required=True)


class MakeMoveForm(messages.Message):
    """Input to request a word be added at x,y, across/down, by user."""
    user_name = messages.StringField(1, required=True)
    x = messages.IntegerField(2)  # if x, y, or across are missing, skip turn
    y = messages.IntegerField(3)
    across = messages.BooleanField(4)
    # empty word allowed.  It means skip turn
    word = messages.StringField(5, required=True)


class IdForm(messages.Message):
    """Outbound id value for a persistent entity, such as game state."""
    urlsafe_key = messages.StringField(1, required=True)


class WinLossRecord(messages.Message):
    """Outbound record of player wins and losses."""
    name = messages.StringField(1, required=True)
    wins = messages.IntegerField(2, required=True)
    losses = messages.IntegerField(3, required=True)


class RankingList(messages.Message):
    """Outbound list of WinLossRecord."""
    rankings = messages.MessageField(WinLossRecord, 1, repeated=True)


class MoveRecord(messages.Message):
    """Outbound record of a word added at x,y, across/down, by user."""
    user_name = messages.StringField(1, required=True)
    x = messages.IntegerField(2)
    y = messages.IntegerField(3)
    across = messages.BooleanField(4)
    word = messages.StringField(5, required=True)  # empty if skipped turn
    moveScore = messages.IntegerField(6, required=True)
    time = DateTimeField(7, required=True)


class MoveList(messages.Message):
    """Outbound list of WinLossRecord."""
    moves = messages.MessageField(MoveRecord, 1, repeated=True)
