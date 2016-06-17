WordWars:  Udacity full stack web developer project 4: create a multiuser game on google app engine.

This is a simplified "Scrabble"-like game where each player takes turns adding words to a crossword board.  The "board" is just a square matrix where letters can be placed.  Positions on the board are addressed by (x, y) coordinates, with (0, 0) at the top left.  While the board is persisted as a string of characters, the endpoint response messages include a string for each y coordinate row to help visualize the board state.  Scoring is based on the individual value of the letters played, plus the value of letters already on the board that are used in the play.  Players may place letters anywhere on the board to form a word from contiguous letters across (left to right) in one row or down in one column.  A higher score results from reusing letters already on the board in addition to those added.  At the start, each player is given seven random letters.  In each turn, additional random letters are drawn from the game bag to replace those played until there are no more.  If a player chooses not to play (or cannot play) they may skip their turn (by playing an empty word at any position).  When every player skips their turn, the game is over.  The player with the highest score wins.

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

To execute tests from the project root directory:
- FIRST: uncomment the sys import lines at the top so python can find google libs.
- python test/letterbag_test.py  # unit test for LetterBag class
- python test/gamestate_test.py  # unit test for main GameState model class
- python test/gamerepository_test.py  # unit test for GameState persistence in DataStore


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
    - This returns all of a User's active games.
    
 - **cancel_game**
    - cancel a game in progress.
        
 - **get_user_rankings**
    - return ranking of each player by win/loss ratio.
 
 - **get_game_history**
    - shows 'history' of moves for a game.
