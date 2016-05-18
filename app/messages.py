"""ww_messages.py defines google app engine Message subclasses 
for the WordWars webapp api requests and responses."""

from protorpc import messages

"""Outbound (single) string message."""
class StringMessage(messages.Message):
    message = messages.StringField(1, required=True)

"""Outbound list of string messages."""
class StringList(messages.Message):
    message = messages.StringField(1, repeated=True)

"""Outbound description of game state."""
class GameForm(messages.Message):
    urlsafe_key = messages.StringField(1, required=True)
    board = messages.StringField(2, required=True)
    game_over = messages.BooleanField(4, required=True)
    user_turn = messages.StringField(5, required=True)
    user_letters = messages.StringField(6, required=True)
    user_score = messages.IntegerField(7, required=True)

"""Input fields to request a word be added at x,y, across/down, by user."""
class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    x = messages.IntegerField(2)  # if x, y, or across are missing, skip turn
    y = messages.IntegerField(3)
    across = messages.BooleanField(4)
    word = messages.StringField(5, required=True)  # empty string means skip turn

"""Outbound id value for a persistent entity, such as game state."""
class IdForm(messages.Message):
    """for outbound model identity"""
    urlsafe_key = messages.StringField(1, required=True)
