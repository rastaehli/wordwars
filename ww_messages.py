"""ww_messages.py defines google app engin Message classes to
construct and send requests to the WordWars webapp."""

from protorpc import messages

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    user2_name = messages.StringField(2, required=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

class StringList(messages.Message):
    message = messages.StringField(1, repeated=True)

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    board = messages.StringField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    user_turn = messages.StringField(4, required=True)
    user_letters = messages.StringField(5, required=True)
    user_score = messages.IntegerField(6, required=True)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    x = messages.IntegerField(1, required=True)
    y = messages.IntegerField(2, required=True)
    across = messages.BooleanField(3, required=True)
    word = messages.StringField(4, required=True)

class IdForm(messages.Message):
    """for outbound model identity"""
    urlsafe_key = messages.StringField(1, required=True)
