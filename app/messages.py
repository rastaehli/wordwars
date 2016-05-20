"""ww_messages.py defines google app engine Message subclasses 
for the WordWars webapp api requests and responses."""

from protorpc import messages

class StringMessage(messages.Message):
    """Outbound (single) string message."""
    message = messages.StringField(1, required=True)

class StringList(messages.Message):
    """Outbound list of string messages."""
    strings = messages.StringField(1, repeated=True)

class GameForm(messages.Message):
    """Outbound description of game state."""
    urlsafe_key = messages.StringField(1, required=True)
    board = messages.StringField(2, required=True)
    status = messages.StringField(3, required=True)
    user_turn = messages.StringField(4, required=True)
    user_letters = messages.StringField(5, required=True)
    user_score = messages.IntegerField(6, required=True)

class MakeMoveForm(messages.Message):
    """Input fields to request a word be added at x,y, across/down, by user."""
    user_name = messages.StringField(1, required=True)
    x = messages.IntegerField(2)  # if x, y, or across are missing, skip turn
    y = messages.IntegerField(3)
    across = messages.BooleanField(4)
    word = messages.StringField(5, required=True)  # empty string means skip turn

class IdForm(messages.Message):
    """Outbound id value for a persistent entity, such as game state."""
    urlsafe_key = messages.StringField(1, required=True)
