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
    game_over = messages.BooleanField(4, required=True)
    user_turn = messages.StringField(5, required=True)
    user_letters = messages.StringField(6, required=True)
    user_score = messages.IntegerField(7, required=True)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    x = messages.IntegerField(2)  # if x, y, or across are missing, skip turn
    y = messages.IntegerField(3)
    across = messages.BooleanField(4)
    word = messages.StringField(5, required=True)  # empty string means skip turn

class IdForm(messages.Message):
    """for outbound model identity"""
    urlsafe_key = messages.StringField(1, required=True)
