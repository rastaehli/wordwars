WordWars:  Udacity full stack web developer project 4: create a multiuser game on google app engine.

This is a simplified "Scrabble"-like game where each player takes turns adding words to a crossword board.  Scoring is based on the individual value of the letters played, plus the value of letters already on the board that are used in the play.  Players may place letters anywhere on the board to form a word from contiguous letters across (left to right) in one row or down in one column.  A higher score results from reusing letters already on the board in addition to those added.  At the start, each player is given seven random letters.  In each turn, additional random letters are drawn from the game bag to replace those played until there are no more.  If a player chooses not to play (or cannot play) they may skip their turn.  When every player skips their turn, the game is over.  The player with the highest score wins.

Unlike Scrabble, there is (currently) no consideration of additional words formed by adjacent letters to those played; no value added and no error if the adjacent letters do not form a valid word.

To play this game (see how to run/execute the software below):
- create users with the 'create_user' request
- create a game with the 'new_unstarted_game' request
- add a user to the game (and repeat until started) with the 'add_user' request
- start the game with the 'start_game' request
- get game state with the 'get_game' request
- make a move with the 'make_move' request
- pass/skip your turn with the 'make_move' request where 'word' value is empty
- when all players pass, the game is over

To run this game on your local machine:
- install the Google App Engine SDK
- clone this project and change to the root directory with app.yaml
- run the command 'dev_appserver.py .'
- note the url in the  "Starting module 'default' running at <app_url>" message
- open a browser on <app_url>/_ah/api/explorer
-- IMPORTANT: because most browsers block content from this unsecure deployment of the service you'll need to disable protection.  For Chrome on Mac OS X, launch Chrome with the following command:
	Chrome: /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost:8080

To execute tests from the test directory:
- python letterbag_test.py  # unit test for LetterBag class
- python gamestate_test.py  # unit test for main GameState model class
- python gamerepository_test.py  # unit test for GameState persistence in DataStore


API

- **create_user**
	- create users with the 'create_user' request

- **new_unstarted_game**
	- create a game with the 'new_unstarted_game' request

- **add_user**
	- add a user to the game (and repeat until started) with the 'add_user' request

- **start_game**
	- start the game with the 'start_game' request

- **get_game**
	- get game state with the 'get_game' request

- **make_move**
	- make a move with the 'make_move' request, pass/skip your turn when 'word' value is empty

 - **get_user_games**
 	- NOT YET IMPLEMENTED
    - This returns all of a User's active games. <todo what if the player prevented concurrent games? Maybe this should be a list of all games (active or not) that the user is related to>
    - You may want to modify the `User` and `Game` models to simplify this type
    of query. **Hint:** it might make sense for each game to be a `descendant` 
    of a `User`.
    
 - **cancel_game**
 	- NOT YET IMPLEMENTED
    - This endpoint allows users to cancel a game in progress.
    You could implement this by deleting the Game model itself, or add a Boolean field such as 'cancelled' to the model.     Ensure that Users are not permitted to remove *completed* games.
    
 - **get_high_scores**
 	- NOT YET IMPLEMENTED
    - Remember how you defined a score in Task 2?
    Now we will use that to generate a list of high scores in descending order, a leader-board!
    - Accept an optional parameter `number_of_results` that limits the number of results returned.
    - Note: If you choose to implement a 2-player game this endpoint is not required.
    
 - **get_user_rankings**
 	- NOT YET IMPLEMENTED
    - Come up with a method for ranking the performance of each player.
      For "Guess a Number" this could be by winning percentage with ties broken by the average number of guesses.
    - Create an endpoint that returns this player ranking. The results should include each Player's name and the 'performance' indicator (eg. win/loss ratio).
 
 - **get_game_history**
 	- NOT YET IMPLEMENTED
    - Your API Users may want to be able to see a 'history' of moves for each game.
    - For example, Chess uses a format called <a href="https://en.wikipedia.org/wiki/Portable_Game_Notation" target="_blank">PGN</a>) which allows any game to be replayed and watched move by move.
    - Add the capability for a Game's history to be presented in a similar way. For example: If a User made played 'Guess a Number' with the moves:
    (5, 8, 7), and received messages such as: ('Too low!', 'Too high!',
    'You win!'), an endpoint exposing the game_history might produce something like:
    [('Guess': 5, result: 'Too low'), ('Guess': 8, result: 'Too high'),
    ('Guess': 7, result: 'Win. Game over')].
    - Adding this functionality will require some additional properties in the 'Game' model along with a Form, and endpoint to present the data to the User.
