#WordWars
This is my implementation of Udacity Full Stack Web Developer project 4: create a multiuser game on google app engine.

##Description

WordWars is a simplified "Scrabble"-like game where each player takes turns adding words to a crossword board.  In each game there is a fixed set of letters that can be played and each player is given a bag of seven letters from this set.  Words must be formed only from the letters in a player's bag in combination with the letters already on the board.Although this implementation does not validate the words played, the intention is that users agree on a dictionary of valid words and only play letters that form valid words across and down on the game board.

For example, suppose that Joe, Rich and Jan are registered as WordWars users and have letters 'aadgqss', 'ihlpstu', and 'deefwxz' respectively in some game, Joe could play 'sad' across at the upper left corner position (0, 0).  Rich could then reuse the last letter 'd' played by Joe to play 'dust' down at position (2, 0).  Jan could play 'wet' at (0, 3) and then it would be Joe's turn again.

Once the game is started, no more players can be added.  The order of play is the same as the order added.  
In each turn, additional random letters are drawn from the game bag to replace those played until there are no more.  
The "board" is just a square matrix where letters can be placed.  Positions on the board are addressed by (x, y) coordinates, with (0, 0) at the top left.  While the board is persisted as a string of characters, the endpoint response messages include a string for each y coordinate row to help visualize the board state.  Scoring is based on the individual value of the letters played, plus the value of letters already on the board that are used in the play.  Players may place letters anywhere on the board to form a word from contiguous letters across (left to right) in one row or down in one column.  A higher score results from reusing letters already on the board in addition to those added.  

If a player chooses not to play (or cannot play) they may skip their turn (by playing an empty word at any position).  When every player skips their turn, the game is over.  The player with the highest score wins.

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
	- Description: Register a new user to play in games.  
	- Path: 'user'
	- Method: POST
	- Parameters: user_name, email
	- Returns: Message confirming user created.
	- Exceptions: Raises ConflictException if user_name already registered.
	  Raises BadRequestException if email parameter has invalid syntax.

- **new_unstarted_game**
	- Description: Create a new game, ready to add users.  Game is initialized
	with an empty 10 x 10 board and the standard set of letters to play.  
	- Path: 'game/new'
	- Method: POST
	- Parameters: <none>
	- Returns: Message with game ID.
	- Exceptions: <none>

- **add_user**
	- Description: Add user identified by user_name as player to game with 
	gameid.  Order of play is determined by order added.  As each player is 
	added, they are given a bag of 7 randomly selected letters from the board
	state.  Cannot add users after game has started.
	- Path: 'game/{gameid}/add_user'
	- Method: PUT
	- Parameters: 'gameid' from prior new_unstarted_game request, 'user_name'
	from prior create_user request.
	- Returns: Message confirming user was added.
	- Exceptions: Raises NotFoundException if no user found for user_name
	or no game found for gameid.  Raises BadRequestException if game has 
	already started.

- **start_game**
	- Description: Update game so it is ready to play.  Cannot start game
	before at least one user has been added.  Cannot add users after
	game has started.
	- Path: 'game/{gameid}/start'
	- Method: PUT
	- Parameters: 'gameid' from prior new_unstarted_game request.
	- Returns: 'gameid' for game identity, 'board' showing all letters in a 
	left-right-top-down scan of the board, 'status' showing one of ('new',
	'playing', 'cancelled', 'over'), 'user_turn' showing the next player's 
	user_name, 'user_letters' showing the letters in next player's bag, and
	'user_score' showing the next player's current score.  To compensate for
	the lack of a good frontend, the content of each row of the board is also
	shown in return values 'y0' through 'y9'.  When printed in order, these 
	rows give a workable visual representation of the board state.
	- Exceptions: Raises NotFoundException if no game found for gameid.  
	Raises BadRequestException if no users have been added.

- **get_game**
	- Description: Get current state of game.
	- Path: 'game/{gameid}'
	- Method: GET
	- Parameters: 'gameid' from prior new_unstarted_game request.
	- Returns: same representation of game state as game/{gameid}/start.  
	See start_game request.
	- Exceptions: Raises NotFoundException if no game found for gameid. 

- **make_move**
	- Description: Play word on the board for given user.
	- Path: 'game/{gameid}/move'
	- Method: PUT
	- Parameters: 'gameid' from prior new_unstarted_game request.  'user_name'
	for game player making the move.  'x' and 'y' for position of first letter
	to play.  'across' set True if the word is to be played across one row or
	False if the word is to be played down.  'word' to be played.  If user
	is skipping this turn, the value of 'word' may be empty and 'x', 'y', and
	'across' parameters may be omitted.
	- Returns: Message indicating move score, plus the same representation of
	game state as game/{gameid}/start.  See start_game request.
	- Exceptions: Raises NotFoundException if no game found for gameid.
	Raises BadRequestException if game is not started, is cancelled, or is
	already over.  Raises BadRequestException if 'word' cannot be played 
	at that position.

- **get_user_games**
	- Description: Get id values for all active games where 'user_name' is a
	player.
	- Path: 'user/{user_name}/games'
	- Method: GET
	- Parameters: 'user_name' from prior create_user request.
	- Returns: List of gameid values.
	- Exceptions: Raises NotFoundException if no user found for user_name.
    
- **cancel_game**
	- Description: Cancel a game so it does not count in user rankings.
	- Path: 'game/{gameid}/cancel'
	- Method: PUT
	- Parameters: 'gameid' from prior new_unstarted_game request.
	- Returns: Message confirming game is cancelled.
	- Exceptions: Raises NotFoundException if no game found for gameid.

- **get_all_users**
	- Description: Return list of registered user_name values.
	- Path: 'user/all'
	- Method: GET
	- Parameters: <none>
	- Returns: Message with list of user_name values.
	- Exceptions: <none>
 
- **get_user_rankings**
	- Description: Return ranking of each player by win/loss ratio.
	- Path: 'user/rankings'
	- Method: GET
	- Parameters: <none>
	- Returns: Message with list of records: 'name' for user, 'wins' for
	the number of completed games where user was high scorer, 'losses' for
	the number of completed games where user was not the high scorer.  List is
	sorted highest win/loss ratio first.
	- Exceptions: <none>
 
- **get_game_history**
	- Description: Show ordered sequence of moves for a game.
	- Path: 'game/{gameid}/history'
	- Method: GET
	- Parameters: 'gameid' from prior new_unstarted_game request.
	- Returns: Message with list of records: 'user_name' for player, 'x' and 
	'y' for board position of first letter, 'across' True if word played 
	across or False if played down, 'word' played, 'moveScore' for the points
	gained by this play, and 'time' for the date and time the move was made.
	- Exceptions: Raises NotFoundException if no game found for gameid.

